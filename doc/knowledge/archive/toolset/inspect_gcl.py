"""Export a bounded, read-only catalog; does not claim to decode bytecode."""
import archive_paths as ap
import hashlib, json, re, struct
from pathlib import Path

root = Path(__file__).resolve().parent / 'output' / 'decompilation'
root.mkdir(parents=True, exist_ok=True)
source = ap.install('bin/game.gcl')
b = source.read_bytes()
count = struct.unpack_from('<I', b)[0]
if not 0 < count < 10000: raise ValueError('Unexpected source table size')
pos = 4
paths = []
for _ in range(count):
    ident, n = struct.unpack_from('<II', b, pos); pos += 8
    if not 0 < n < 2048 or pos+n > len(b): raise ValueError('Invalid path length')
    path = b[pos:pos+n].decode('utf-8'); pos += n
    if not path.endswith('.gc'): raise ValueError('Unexpected source path')
    paths.append({'id': ident, 'path': path})
global_count = struct.unpack_from('<I', b, pos)[0]; pos += 4
globals_table = []
for _ in range(global_count):
    row = []
    for field in ('type', 'name'):
        n = struct.unpack_from('<I', b, pos)[0]; pos += 4
        if not 0 < n < 4096 or pos+n > len(b): raise ValueError('Invalid global field')
        row.append(b[pos:pos+n].decode('utf-8')); pos += n
    globals_table.append(dict(zip(('type', 'name'), row)))
strings = []
seen = set()
for m in re.finditer(rb'[\x20-\x7e]{8,2048}', b):
    s = m.group().decode('ascii')
    if s not in seen and any(k in s.lower() for k in ('microcontroller', 'vehicle', 'telemetry', 'inspect', 'tick_rate', 'save', 'load', 'geocode')):
        strings.append({'offset': m.start(), 'text': s})
        seen.add(s)
result = {'source': str(source), 'sha256': hashlib.sha256(b).hexdigest(),
          'bytes': len(b), 'source_path_table_end': 4 + sum(8+len(x['path'].encode('utf-8')) for x in paths), 'source_paths': paths,
          'global_names_and_types': globals_table, 'global_table_end': pos,
          'selected_strings': strings,
          'limitations': 'Source paths and readable names only; bytecode and later binary tables are not decoded.'}
with (root / 'gcl-symbol-catalog.json').open('x', encoding='utf-8') as f: json.dump(result, f, indent=2)
print(f'Cataloged {len(paths)} source paths, {len(globals_table)} global names/types, and {len(strings)} unique selected strings.')
