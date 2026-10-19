"""Index snapshot JSON without inventing omitted defaults or interface semantics."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

from baseline import resources, sha, write

VERSION = '1.0.0'


def build(snapshot, out):
    if out.exists():
        raise FileExistsError(out)
    resources(out.parent)
    out.mkdir()
    db = sqlite3.connect(out / 'definitions.sqlite')
    db.executescript('''
        CREATE TABLE files(path TEXT PRIMARY KEY,sha256 TEXT,root_keys TEXT);
        CREATE TABLE definitions(source TEXT,pointer TEXT,id TEXT,class TEXT,
            name TEXT,description TEXT,sha256 TEXT,json TEXT);
        CREATE INDEX ids ON definitions(id);
        CREATE VIRTUAL TABLE search USING fts5(source,pointer,id,class,name,description,json);
    ''')
    summary, components = [], []
    paths = sorted((snapshot / 'rom/data').rglob('*'))
    for path in paths:
        if not path.is_file():
            continue
        raw = path.read_bytes()
        try:
            value = json.loads(raw.decode('utf-8-sig'))
        except (ValueError, UnicodeDecodeError):
            continue
        rel = path.relative_to(snapshot).as_posix()
        keys = list(value) if isinstance(value, dict) else ['<array>']
        digest = hashlib.sha256(raw).hexdigest()
        db.execute('INSERT INTO files VALUES(?,?,?)', (rel, digest, json.dumps(keys)))
        defs = value.get('definitions') if isinstance(value, dict) else None
        count = 0
        classes = Counter()
        if isinstance(defs, list):
            for i, d in enumerate(defs):
                if not isinstance(d, dict):
                    raise ValueError('Non-object definition: ' + rel)
                pointer = '/definitions/' + str(i)
                canonical = json.dumps(d, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
                fields = (rel, pointer, str(d.get('id', '')), str(d.get('class', '')),
                          str(d.get('name', '')), str(d.get('description', '')))
                dh = hashlib.sha256(canonical.encode()).hexdigest()
                db.execute('INSERT INTO definitions VALUES(?,?,?,?,?,?,?,?)', (*fields, dh, canonical))
                db.execute('INSERT INTO search VALUES(?,?,?,?,?,?,?)', (*fields, canonical))
                classes[str(d.get('class', '<omitted>'))] += 1
                count += 1
                if rel == 'rom/data/vehicle_component_definitions.json':
                    components.append({'id': d.get('id'), 'class': d.get('class'),
                        'pointer': pointer, 'definition_sha256': dh,
                        'logic_nodes': [n.get('type') for n in d.get('logic_nodes', [])],
                        'surface_types': dict(Counter(s.get('type', '<omitted>') for s in d.get('surfaces', []))),
                        'fields_present': sorted(d)})
        summary.append({'path': rel, 'sha256': digest, 'root_keys': keys,
                        'definitions': count, 'classes': dict(classes)})
    db.commit()
    db.close()
    report = {'schema': 1, 'tool_version': VERSION, 'tool_sha256': sha(Path(__file__)),
              'json_files_indexed': len(summary),
              'definitions_indexed': sum(s['definitions'] for s in summary),
              'component_definitions': len(components), 'files': summary,
              'limits': 'Explicit shipped fields only. Omitted defaults, class binding and runtime compatibility are not inferred.'}
    write(out / 'summary.json', report)
    write(out / 'component-index.json', components)
    print(json.dumps({k: v for k, v in report.items() if k != 'files'}, indent=2))


def query(path, term, limit):
    db = sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)
    for row in db.execute('''SELECT source,pointer,id,class,name,description FROM search
                             WHERE search MATCH ? LIMIT ?''', (term, limit)):
        print(json.dumps(dict(zip(('source','pointer','id','class','name','description'),row)), ensure_ascii=False))
    db.close()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('build')
    p.add_argument('snapshot', type=Path)
    p.add_argument('out', type=Path)
    p = sub.add_parser('query')
    p.add_argument('database', type=Path)
    p.add_argument('term')
    p.add_argument('--limit', type=int, default=20)
    a = ap.parse_args()
    if a.command == 'build':
        build(a.snapshot, a.out)
    else:
        query(a.database, a.term, a.limit)
