"""Account for every indexed record/class without claiming semantic coverage.

Outputs are local indexes, not a publication of complete game symbols/code.
Matching component and method-owner names is a lead, not recovered dispatch.
"""
import argparse
from collections import Counter, defaultdict
from contextlib import closing
import json
from pathlib import Path
import re
import sqlite3

from baseline import sha, write
from code_reader import connect as connect_reader
from system_map import TOPICS

VERSION = '1.0.0'


def qualified_name(signature):
    """Drop the balanced return tuple and arguments; keep templates intact."""
    if not signature.startswith('('):
        return None
    depth = 0
    for i, char in enumerate(signature):
        depth += (char == '(') - (char == ')')
        if depth == 0:
            rest = signature[i + 1:].strip()
            name, separator, _ = rest.partition(' (')
            return name if separator and name else None
    return None


def owner_name(name):
    """Ignore namespace separators inside template argument lists."""
    depth, split = 0, -1
    for i, char in enumerate(name):
        if char == '<':
            depth += 1
        elif char == '>':
            depth = max(0, depth - 1)
        elif char == '.' and depth == 0:
            split = i
    return name[:split] if split >= 0 else '<global>'


def inventory(functions, definitions, exported):
    by_owner, component_rows = defaultdict(list), defaultdict(list)
    patterns = [(ident, re.compile(pattern, re.I)) for ident, _, pattern, _ in TOPICS]
    topic_counts, rows = Counter(), []
    seen = set()
    for function in functions:
        offset = function['code_offset']
        if offset in seen:
            raise ValueError('Duplicate function offset')
        seen.add(offset)
        name = qualified_name(function['signature'])
        owner = owner_name(name) if name else '<unparsed>'
        # Overlapping leads on method names only; parameter/return types cannot
        # accidentally classify unrelated methods as component implementations.
        topics = [ident for ident, pattern in patterns if name and pattern.search(name)]
        topics = topics or ['unclassified']
        topic_counts.update(topics)
        identity = exported.get(offset)
        if identity and identity != (function['signature'], function['code_sha256']):
            raise ValueError('Reader/index identity mismatch')
        row = {key: function[key] for key in
               ('signature', 'code_offset', 'code_size', 'code_sha256')}
        row.update(owner=owner, topic_leads=topics,
                   exported_identity_present=identity is not None,
                   semantic_review='not_inferred_from_export')
        rows.append(row)
        by_owner[owner].append(row)
    unknown = set(exported) - seen
    if unknown:
        raise ValueError('Reader contains functions absent from index')
    for definition in definitions:
        if definition['source'] == 'rom/data/vehicle_component_definitions.json':
            component_rows[definition['class']].append(definition)
    classes = []
    for cls, items in sorted(component_rows.items()):
        owner = 'server_scene.vehicle_component.' + cls if cls else None
        methods = by_owner.get(owner, [])
        classes.append({'class': cls or None, 'definitions': len(items),
                        'definition_refs': [{k: item[k] for k in
                            ('source', 'pointer', 'id', 'sha256')} for item in items],
                        'same_name_owner_candidate': owner,
                        'indexed_exact_owner_methods': len(methods),
                        'method_leads': [{key: row[key] for key in
                            ('signature', 'code_offset', 'code_size', 'code_sha256',
                             'exported_identity_present')} for row in methods],
                        'exported_exact_owner_methods': sum(
                            row['exported_identity_present'] for row in methods),
                        'binding_status': 'name_candidate_only' if methods else 'unresolved',
                        'semantic_status': 'requires_individual_review'})
    definition_groups = Counter((d['source'], d['class']) for d in definitions)
    summary = {'function_records': len(rows), 'method_owner_groups': len(by_owner),
               'unparsed_signatures': len(by_owner.get('<unparsed>', [])),
               'topic_name_leads_overlapping': dict(sorted(topic_counts.items())),
               'reader_identity_matches': len(exported),
               'all_definition_records': len(definitions),
               'definition_source_class_groups': len(definition_groups),
               'component_definitions': sum(len(v) for v in component_rows.values()),
               'explicit_component_classes': sum(bool(k) for k in component_rows),
               'component_definitions_with_omitted_class': len(component_rows.get('', [])),
               'class_groups_with_same_name_owner': sum(
                   bool(c['indexed_exact_owner_methods']) for c in classes)}
    return rows, classes, summary


def load_reader(reader, expected_source):
    with closing(connect_reader(reader)) as db:
        provenance = json.loads(db.execute(
            "SELECT value FROM metadata WHERE key='provenance'").fetchone()[0])
        if provenance['source_sha256'] != expected_source:
            raise ValueError('Reader/index source mismatch')
        return {offset: (sig, digest) for offset, sig, digest in
                db.execute('SELECT code_offset,signature,code_sha256 FROM functions')}


def build(index, catalog, output, reader=None):
    if output.exists():
        raise FileExistsError(output)
    with closing(sqlite3.connect(index.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        functions = [json.loads(row[0]) for row in db.execute('SELECT record FROM functions')]
        provenance = {k: json.loads(v) for k, v in db.execute('SELECT key,value FROM provenance')}
    with closing(sqlite3.connect(catalog.resolve().as_uri() + '?mode=ro', uri=True)) as db:
        definitions = [dict(zip(('source','pointer','id','class','sha256'), row))
                       for row in db.execute('SELECT source,pointer,id,class,sha256 FROM definitions')]
    exported = load_reader(reader, provenance['source_sha256']) if reader else {}
    rows, classes, summary = inventory(functions, definitions, exported)
    metadata = {'schema': 1, 'tool_version': VERSION, 'tool_sha256': sha(Path(__file__)),
                'source_sha256': provenance['source_sha256'],
                'index_sha256': sha(index), 'catalog_sha256': sha(catalog),
                'reader_sha256': sha(reader) if reader else None,
                'summary': summary,
                'required_review_dimensions': [
                    'definition variants and inherited implementation binding',
                    'creation and omitted parser defaults',
                    'structural mounting and moving-body ownership',
                    'interface type, gender, ordinal, position and facing',
                    'inputs, outputs, units and thresholds',
                    'state transitions, power loss and damage',
                    'tick order and network dependencies',
                    'serialization, ID remapping and migration',
                    'render geometry versus collision and buoyancy',
                    'historical claims, contradictions and remaining uncertainty'],
                'limits': 'Exhaustive only over supplied indexes. Names are leads, not binding or behavior. '
                          'Export identity does not establish semantic review. Unclassified records are retained. '
                          'Old claims and runtime evidence require a separate manual review ledger.'}
    output.mkdir(parents=True)
    write(output / 'summary.json', metadata)
    write(output / 'components.json', classes)
    write(output / 'functions.json', rows)
    groups = Counter((d['source'], d['class']) for d in definitions)
    write(output / 'definition-groups.json', [dict(source=source, **{'class': cls or None},
                                                 definitions=count)
          for (source, cls), count in sorted(groups.items())])
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index', type=Path)
    parser.add_argument('catalog', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--reader', type=Path)
    args = parser.parse_args()
    build(args.index, args.catalog, args.output, args.reader)
