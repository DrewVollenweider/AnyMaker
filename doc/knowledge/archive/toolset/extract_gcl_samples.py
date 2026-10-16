"""Extract three specifically validated native-code constructors from a copy.

This is not a general parser for GCL. Fail closed if the observed layout changes.
"""
import archive_paths as ap
import hashlib, json, struct
from pathlib import Path

out = Path(__file__).resolve().parent / 'output' / 'decompilation'
source = ap.install('bin/game.gcl')
b = source.read_bytes()
records = []
for name in ('g_server_tick_rate_s32', 'server.G_AUTOSAVE_INTERVAL', 'server.G_AUTOSAVE_MAX_COUNT'):
    signature = f'() {name}.$ctor ()'.encode()
    if b.count(signature) != 1: raise ValueError('Ambiguous signature')
    start = b.index(signature); pos = start + len(signature)
    if b[pos:pos+16] != struct.pack('<IIII', 1, 0, 1, 3): raise ValueError('Unexpected metadata')
    pos += 16
    n = struct.unpack_from('<I', b, pos)[0]; pos += 4
    if b[pos:pos+n] != name.encode(): raise ValueError('Name mismatch')
    pos += n
    extent, size = struct.unpack_from('<II', b, pos); pos += 8
    if not 0 < extent <= size < 256: raise ValueError('Unexpected code extent')
    code = b[pos:pos+size]
    if len(code) != size or code[:3] not in (b'\x48\x8b\x0d', b'\x48\x8b\x05'): raise ValueError('Unexpected instructions')
    target = out / (name.replace('.', '_') + '.bin')
    with target.open('xb') as f: f.write(code)
    records.append({'name': name, 'signature_offset': start, 'code_offset': pos,
                    'extent_field': extent, 'extracted_bytes': size,
                    'file': str(target), 'sha256': hashlib.sha256(code).hexdigest()})
with (out/'gcl-native-samples.json').open('x', encoding='utf-8') as f:
    json.dump({'source': str(source), 'source_sha256': hashlib.sha256(b).hexdigest(),
               'warning': 'Global pointer relocations are unresolved. Static initialization only.',
               'records': records}, f, indent=2)
print('Extracted three validated constructor code blocks; original file unchanged.')
