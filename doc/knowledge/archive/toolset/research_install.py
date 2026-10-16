"""Read-only installation refresh; preserve source hashes and version differences."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct

import anymaker as tools


def fingerprint(path):
    before = path.stat()
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError(f'Source changed during hashing: {path}')
    return {'source': str(path.resolve()), 'bytes': after.st_size,
            'sha256': digest.hexdigest()}


def gcl_tables(path):
    # Same validated table layout as inspect_gcl.py; no code execution.
    raw = path.read_bytes()
    pos = 0

    def u32():
        nonlocal pos
        value = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
        return value

    def string(limit):
        nonlocal pos
        size = u32()
        if not 0 < size < limit or pos + size > len(raw):
            raise ValueError('Unexpected GCL string size')
        result = raw[pos:pos + size].decode('utf-8')
        pos += size
        return result

    count = u32()
    if not 0 < count < 10000:
        raise ValueError('Unexpected source table count')
    paths = []
    for _ in range(count):
        ident = u32()
        value = string(2048)
        if not value.endswith('.gc'):
            raise ValueError('Unexpected GCL source path')
        paths.append({'id': ident, 'path': value})
    count = u32()
    if not 0 < count < 100000:
        raise ValueError('Unexpected globals count')
    globals_ = [{'type': string(4096), 'name': string(4096)} for _ in range(count)]
    return {'source_paths': paths, 'global_names_and_types': globals_,
            'global_table_end': pos,
            'limitations': 'Names and types only; these do not prove function behavior.'}


def creation_record(path):
    doc = tools.load(path)
    refs = tools.references(doc)
    if tools.shape_errors(doc):
        return {'file': path.name, 'shape_errors': tools.shape_errors(doc)}
    counts = Counter()
    bodies = []
    scripts = []
    for vehicle in tools.vehicles(doc):
        aliases = {}
        for c in tools.components(vehicle):
            definition = refs[c['def']] if 0 <= c['def'] < len(refs) else None
            counts[definition or '<unknown>'] += 1
            if c.get('user_defined_alias'):
                aliases.setdefault(c['user_defined_alias'], []).append(
                    {'component': c['id'], 'definition': definition})
            if isinstance(c.get('script'), str):
                scripts.append({'vehicle': vehicle['id'], 'component': c['id'],
                                'text': c['script'],
                                'channel_references': sorted(set(re.findall(
                                    r'\b(in|out)\s+([\w]+)\.([\w]+)', c['script'])))})
        bodies.append({'id': vehicle['id'], 'grid_count': len(vehicle.get('grids', [])),
                       'mounting_grids': [{k: g[k] for k in ('origin', 'dir') if k in g}
                                         for g in vehicle.get('grids', [])],
                       'aliases': aliases})
    return {'file': path.name, 'component_counts': dict(counts), 'bodies': bodies,
            'scripts': scripts,
            'limitations': 'Saved fields; aliases do not prove connected data networks. Scripts were not executed.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('installation', type=Path)
    parser.add_argument('--creations', type=Path)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    install = args.installation.resolve()
    out = tools.destination(args.out)
    out.mkdir(parents=True, exist_ok=False)
    initial = []
    for path in sorted((install / 'rom/data').glob('*.json')):
        initial.append(fingerprint(path))
    for relative in ('game.exe', 'steam_api64.dll', 'bin/game.gcl',
                     'rom/languages.tsv', 'rom/textures/color_palette.txtr'):
        path = install / relative
        if path.exists():
            initial.append(fingerprint(path))
    old_index = tools.load(tools.HOME.parent / 'exploration/reference/source-index.json')
    old_hashes = {Path(x['Path']).name: x['SHA256'].lower() for x in old_index}
    updates = [{'file': Path(x['source']).name, 'before_sha256': old_hashes.get(Path(x['source']).name),
                'after_sha256': x['sha256'],
                'same_as_prior': old_hashes.get(Path(x['source']).name) == x['sha256']}
               for x in initial if Path(x['source']).name in old_hashes]
    comparisons = []
    for name in ('vehicle_component_definitions', 'inventory_definitions'):
        doc = tools.load(install / f'rom/data/{name}.json')
        tools.save(f'{args.out}/{name}.json', doc)
        before = tools.load(tools.HOME / f'reference/{name}.json')
        comparisons.append({'name': name, 'definition_count': len(doc['definitions']),
                            'changes': tools.differences(before, doc)})
    catalog = {d['id']: d for d in tools.load(install / 'rom/data/vehicle_component_definitions.json')['definitions']}
    # Exact raw interfaces, fields and values: omitted fields stay omitted.
    interfaces = [{k: d[k] for k in ('id', 'name', 'class', 'description', 'surfaces',
                                    'logic_nodes', 'data_descriptors', 'mateable_port_types',
                                    'constraint_orientations') if k in d}
                  for d in catalog.values()]
    tools.save(f'{args.out}/interfaces.json', interfaces)
    tables = gcl_tables(install / 'bin/game.gcl')
    tools.save(f'{args.out}/gcl-tables.json', tables)
    old_tables = tools.load(tools.HOME / 'output/decompilation/gcl-symbol-catalog.json')
    symbols = {}
    for field, key in (('source_paths', 'path'), ('global_names_and_types', 'name')):
        before = {x[key] for x in old_tables[field]}
        after = {x[key] for x in tables[field]}
        symbols[field] = {'before_count': len(before), 'after_count': len(after),
                          'added': sorted(after - before), 'removed': sorted(before - after)}
    creations = []
    if args.creations:
        for path in sorted(args.creations.glob('*.data')):
            initial.append(fingerprint(path))
            try:
                creations.append(creation_record(path))
            except (ValueError, KeyError, TypeError, IndexError) as exc:
                creations.append({'file': path.name, 'read_error': str(exc)})
        tools.save(f'{args.out}/creation-index.json', creations)
        scripts = []
        for path in sorted((args.creations.parent / 'scripts').glob('*.txt')):
            initial.append(fingerprint(path))
            scripts.append({'file': path.name, 'text': path.read_text(encoding='utf-8-sig')})
        tools.save(f'{args.out}/saved-scripts.json', scripts)
    final = [fingerprint(Path(x['source'])) for x in initial]
    report = {'captured_utc': datetime.now(timezone.utc).isoformat(),
              'installation': str(install), 'definitions': comparisons,
              'prior_reference_hash_comparison': updates, 'gcl_symbol_changes': symbols,
              'creation_count': len(creations),
              'script_count': sum(len(x.get('scripts', [])) for x in creations),
              'integrity': {'all_sources_unchanged': initial == final, 'before': initial, 'after': final},
              'limits': ['Read-only file research; no game load or physics test.',
                         'Prior executable decompilation addresses must not be reused without matching hashes.',
                         'Surface dir/gender codes and omitted defaults remain raw, not inferred.']}
    tools.save(f'{args.out}/report.json', report)
    print(json.dumps({'definitions': report['definitions'],
                      'gcl_symbol_counts': {k: {n: len(v[n]) if isinstance(v[n], list) else v[n]
                                                for n in v}
                                            for k, v in symbols.items()},
                      'creation_count': len(creations),
                      'script_count': report['script_count']}, indent=2))
    print('All inspected sources unchanged:', report['integrity']['all_sources_unchanged'])
    print('Output:', out)


if __name__ == '__main__':
    main()
