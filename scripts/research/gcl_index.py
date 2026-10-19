"""Recover bounded GCL native function records and a searchable local index.

This is a structural scanner, not a complete GCL grammar or a decompiler.
Unknown metadata is retained. Signature-looking strings alone are not functions.
Only length-prefixed signatures followed by a fully bounded relocation table,
code/allocation sizes, and exactly one zero pointer slot per relocation qualify.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import struct
import sys

from baseline import resources, sha, write

VERSION = '1.3.0'
SIGNATURE = re.compile(rb'^\([^\x00-\x1f]*\) [^\x00-\x20]+ \([^\x00-\x1f]*\)$')


class Reader:
    def __init__(self, data, pos=0):
        self.data, self.pos = data, pos

    def u32(self):
        if self.pos + 4 > len(self.data):
            raise ValueError('truncated u32')
        n = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return n

    def text(self, limit=65536):
        n = self.u32()
        if not 0 < n <= limit or self.pos + n > len(self.data):
            raise ValueError('invalid string length')
        raw = self.data[self.pos:self.pos+n]
        self.pos += n
        if any(x < 32 for x in raw):
            raise ValueError('control character in symbol')
        return raw.decode('utf-8')


def header(b):
    r = Reader(b)
    n = r.u32()
    if not 0 < n < 10000:
        raise ValueError('unsupported source table')
    sources = []
    for _ in range(n):
        ident, path = r.u32(), r.text(2048)
        if not path.endswith('.gc'):
            raise ValueError('unsupported source entry')
        sources.append({'id': ident, 'path': path})
    n = r.u32()
    if not 0 < n < 100000:
        raise ValueError('unsupported global table')
    globals_ = [{'type': r.text(), 'name': r.text()} for _ in range(n)]
    return {'sources': sources, 'globals': globals_, 'header_end': r.pos}


def record(b, pos):
    r = Reader(b, pos - 4)
    signature = r.text()
    if not SIGNATURE.fullmatch(signature.encode()):
        raise ValueError('not a function signature')
    m0, m1, count = r.u32(), r.u32(), r.u32()
    if not (0 < m0 < 256 and m0 & 1):
        raise ValueError('unsupported metadata flag shape')
    if count > 4096:
        raise ValueError('unbounded relocation count')
    refs = []
    for _ in range(count):
        kind = r.u32()
        if kind == 1:
            # Observed numeric relocation operand. Its runtime meaning is unknown.
            refs.append({'kind': kind, 'symbol': None, 'operand_u32': r.u32()})
            continue
        if kind not in (3, 4, 5, 6):
            raise ValueError('unsupported relocation kind ' + str(kind))
        refs.append({'kind': kind, 'symbol': r.text()})
    size, allocation = r.u32(), r.u32()
    code = r.pos
    serialized_size = size + count * 8
    if not (0 < size <= 4 * 1024**2 and allocation - serialized_size in (0, 8)):
        raise ValueError('unsupported code/allocation relation')
    if code + serialized_size > len(b):
        raise ValueError('truncated code allocation')
    if any(b[code+size:code+serialized_size]):
        raise ValueError('nonzero unresolved pointer slots')
    for i, ref in enumerate(refs):
        ref['slot_offset'] = size + i * 8
    return {'signature': signature, 'signature_offset': pos, 'code_offset': code,
            'code_size': size, 'allocation_size': allocation,
            'serialized_size': serialized_size,
            'allocation_extra_uninterpreted': allocation - serialized_size,
            'metadata_uninterpreted': [m0, m1], 'references': refs,
            'code_sha256': hashlib.sha256(b[code:code+size]).hexdigest(),
            'serialized_sha256': hashlib.sha256(b[code:code+serialized_size]).hexdigest()}


def scan(b):
    found, rejected = [], Counter()
    # Calls also contain signatures. Structural checks, overlapping-allocation
    # checks, and independently sampled code validation are therefore required.
    for m in re.finditer(rb'\(', b):
        pos = m.start()
        if pos < 4:
            continue
        n = struct.unpack_from('<I', b, pos - 4)[0]
        if not 5 < n < 65536 or pos + n > len(b):
            continue
        s = b[pos:pos+n]
        if not SIGNATURE.fullmatch(s):
            continue
        try:
            found.append(record(b, pos))
        except (ValueError, UnicodeDecodeError) as e:
            rejected[str(e)] += 1
    ordered = sorted(found, key=lambda r: r['code_offset'])
    for a, c in zip(ordered, ordered[1:]):
        if a['code_offset'] + a['serialized_size'] > c['signature_offset']:
            raise ValueError('overlapping recovered records; refusing index')
    signatures = Counter(r['signature'] for r in found)
    for r in ordered:
        r['same_signature_records'] = signatures[r['signature']]
    return ordered, rejected


def build(source, out):
    if out.exists():
        raise FileExistsError(out)
    resources(out.parent)
    source_hash = sha(source)
    b = source.read_bytes()
    if hashlib.sha256(b).hexdigest() != source_hash:
        raise ValueError('source changed before parse')
    h = header(b)
    rows, rejected = scan(b)
    if sha(source) != source_hash:
        raise ValueError('source changed after parse')
    out.mkdir()
    db = sqlite3.connect(out / 'index.sqlite')
    db.executescript('''
        CREATE TABLE provenance(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE functions(id INTEGER PRIMARY KEY, signature TEXT,
            code_offset INTEGER, code_size INTEGER, record TEXT);
        CREATE TABLE refs(caller INTEGER, kind INTEGER, slot INTEGER, symbol TEXT,
            target INTEGER, resolution TEXT);
        CREATE INDEX symbol_lookup ON refs(symbol);
        CREATE TABLE globals(name TEXT PRIMARY KEY, type TEXT);
        CREATE TABLE sources(id INTEGER, path TEXT);
    ''')
    counts = Counter(r['signature'] for r in rows)
    ids = {r['signature']: i for i, r in enumerate(rows) if counts[r['signature']] == 1}
    globals_ = {r['name'] for r in h['globals']}
    resolutions = Counter()
    for i, r in enumerate(rows):
        db.execute('INSERT INTO functions VALUES(?,?,?,?,?)',
                   (i, r['signature'], r['code_offset'], r['code_size'], json.dumps(r)))
        for ref in r['references']:
            target = ids.get(ref['symbol']) if ref['kind'] in (4, 6) else None
            resolution = ('function-record' if target is not None else
                'global-table' if ref['kind'] == 3 and ref['symbol'] in globals_
                else 'unresolved')
            resolutions[resolution] += 1
            db.execute('INSERT INTO refs VALUES(?,?,?,?,?,?)', (i, ref['kind'],
                ref['slot_offset'], ref['symbol'], target, resolution))
    db.executemany('INSERT INTO globals VALUES(?,?)', [(r['name'], r['type']) for r in h['globals']])
    db.executemany('INSERT INTO sources VALUES(?,?)', [(r['id'], r['path']) for r in h['sources']])
    report = {'schema': 1, 'tool_version': VERSION, 'tool_sha256': sha(Path(__file__)),
              'source_sha256': source_hash, 'source_bytes': len(b),
              'source_count': len(h['sources']), 'global_count': len(h['globals']),
              'header_end': h['header_end'], 'function_records': len(rows),
              'code_bytes_in_records': sum(r['code_size'] for r in rows),
              'ambiguous_signatures': {s:n for s,n in counts.items() if n > 1},
              'metadata_word0_counts': dict(Counter(r['metadata_uninterpreted'][0] for r in rows)),
              'allocation_extra_counts': dict(Counter(r['allocation_extra_uninterpreted'] for r in rows)),
              'relocations': dict(resolutions), 'rejected_candidates': dict(rejected),
              'decoded_functions': 0, 'understood_functions': 0,
              'limits': ['Scanner coverage is not complete-container coverage.',
                  'Code size includes constants/padding; not every byte is an instruction.',
                  'Relocation targets are symbols, not proven executed calls.',
                  'Metadata words, trailing debug/unwind tables, types and indirect calls remain unresolved.',
                  'No runtime behavior is established by a recovered record.']}
    db.executemany('INSERT INTO provenance VALUES(?,?)',
                   [(k, json.dumps(v)) for k, v in report.items()])
    db.commit()
    db.close()
    write(out / 'summary.json', report)
    write(out / 'header.json', h)
    print(json.dumps({k:v for k,v in report.items() if k != 'rejected_candidates'}, indent=2))


def query(dbpath, term, callers=False, limit=40):
    db = sqlite3.connect(dbpath.resolve().as_uri() + '?mode=ro', uri=True)
    if callers:
        sql = '''SELECT DISTINCT f.record FROM refs r JOIN functions f ON f.id=r.caller
                 WHERE instr(lower(r.symbol),lower(?))>0 ORDER BY f.code_offset LIMIT ?'''
    else:
        sql = 'SELECT record FROM functions WHERE instr(lower(signature),lower(?))>0 ORDER BY code_offset LIMIT ?'
    for row in db.execute(sql, (term, limit)):
        print(row[0])
    db.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('source', type=Path)
    p.add_argument('out', type=Path)
    p = sub.add_parser('query')
    p.add_argument('database', type=Path)
    p.add_argument('term')
    p.add_argument('--callers', action='store_true')
    p.add_argument('--limit', type=int, default=40)
    a = ap.parse_args()
    if a.command == 'build':
        build(a.source, a.out)
    else:
        query(a.database, a.term, a.callers, a.limit)
