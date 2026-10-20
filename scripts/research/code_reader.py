"""Build/search an offline, source-verified reader for selected GCL decompilations.

The reader combines approximate C, exact assembly, complete operand symbols,
literal-data candidates, and conservative static call-site dependency traces.
It never calls game code. Full local databases/exports must not be committed.
"""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

from baseline import sha,write
from trace_code import audit

VERSION='1.1.0'


def connect(path):
    db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)
    try:
        row=db.execute("SELECT value FROM metadata WHERE key='complete'").fetchone()
        if row is None or row[0]!='true':raise ValueError('Incomplete reader build')
    except Exception:
        db.close();raise
    return db


def build(source,index,output,folders):
    if output.exists():raise FileExistsError(output)
    output.mkdir(parents=True)
    # Audit every folder before advertising a usable reader database.
    reports=[audit(source,index,folder,output/f'audit-{i+1:02}.json') for i,folder in enumerate(folders)]
    expected=sha(source)
    with closing(sqlite3.connect(output/'code.sqlite')) as db:
        db.executescript('''
            CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT);
            CREATE TABLE functions(code_offset INTEGER PRIMARY KEY,signature TEXT,
                code_sha256 TEXT,c_source TEXT,assembly TEXT,evidence TEXT);
            CREATE VIRTUAL TABLE search USING fts5(signature,c_source,symbols,literals);
        ''')
        names={};counts={'functions':0,'identical_exports_deduplicated':0,'instructions_byte_checked':0,'slot_derived_calls':0,'unresolved_calls':0}
        for folder,report in zip(folders,reports):
            if report['source_sha256']!=expected:raise ValueError('Multiple source builds')
            for r in report['functions']:
                c=(folder/'ghidra'/(r['export_name']+'.c')).read_text(encoding='utf-8')
                asm=(folder/'ghidra'/(r['export_name']+'.asm.tsv')).read_text(encoding='utf-8')
                if not c.strip() or c.startswith('ERROR:'):raise ValueError('Incomplete pseudocode')
                evidence=json.dumps(r,ensure_ascii=False)
                identity=(r['signature'],r['code_sha256'],c,asm,
                          json.dumps(r,sort_keys=True,ensure_ascii=False))
                if r['code_offset'] in names:
                    if names[r['code_offset']]!=identity:
                        raise ValueError('Conflicting duplicate export function')
                    counts['identical_exports_deduplicated']+=1
                    continue
                names[r['code_offset']]=identity
                db.execute('INSERT INTO functions VALUES(?,?,?,?,?,?)',
                    (r['code_offset'],r['signature'],r['code_sha256'],c,asm,evidence))
                db.execute('INSERT INTO search(rowid,signature,c_source,symbols,literals) VALUES(?,?,?,?,?)',
                    (r['code_offset'],r['signature'],c,
                     '\n'.join(x.get('symbol') or '' for x in r['slot_reads']),
                     '\n'.join(x['text'] for x in r['literal_strings'])))
                counts['functions']+=1;counts['instructions_byte_checked']+=r['instructions_byte_checked']
                counts['slot_derived_calls']+=sum(x['resolution']=='slot-derived-in-local-block' for x in r['call_sites'])
                counts['unresolved_calls']+=sum(x['resolution']=='unresolved-indirect' for x in r['call_sites'])
        provenance={'schema':1,'tool_version':VERSION,'tool_sha256':sha(Path(__file__)),
                    'source_sha256':expected,'counts':counts,
                    'limits':['Approximate C is not original source or a recovered ABI.',
                              'Slot-derived call sites establish data dependency, not virtual target binding.',
                              'Full-text results and printable strings are investigative leads, not behavioral conclusions.',
                              'No game process, gameplay session, or external Python dependency is required.']}
        if sha(source)!=expected:raise ValueError('Source changed during reader build')
        db.execute('INSERT INTO metadata VALUES(?,?)',('provenance',json.dumps(provenance)))
        db.execute('INSERT INTO metadata VALUES(?,?)',('complete','true'));db.commit()
    if sha(source)!=expected:raise ValueError('Source changed during reader build')
    write(output/'summary.json',provenance)
    print(json.dumps({'database':str(output/'code.sqlite'),**counts},indent=2))
    return provenance


def search(database,term,limit=20):
    if not 1<=limit<=100:raise ValueError('Limit must be in 1..100')
    with closing(connect(database)) as db:
        rows=db.execute('''SELECT rowid,signature,snippet(search,1,'[',']',' ... ',24)
            FROM search WHERE search MATCH ? ORDER BY rank LIMIT ?''',(term,limit)).fetchall()
    return [{'code_offset':r[0],'signature':r[1],'snippet':r[2]} for r in rows]


def show(database,offset,section='evidence'):
    with closing(connect(database)) as db:
        row=db.execute('SELECT signature,c_source,assembly,evidence FROM functions WHERE code_offset=?',(offset,)).fetchone()
    if row is None:raise ValueError('Function not in selected reader; search the main GCL index for further exports')
    if section=='c':return row[1]
    if section=='assembly':return row[2]
    evidence=json.loads(row[3])
    if section=='calls':return evidence['call_sites']
    if section=='constants':return {k:evidence[k] for k in ['embedded_reads','literal_strings','address_literals']}
    return evidence


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    b=sub.add_parser('build')
    for name in ['source','index','output']:b.add_argument(name,type=Path)
    b.add_argument('exports',nargs='+',type=Path)
    s=sub.add_parser('search');s.add_argument('database',type=Path);s.add_argument('term');s.add_argument('--limit',type=int,default=20)
    s=sub.add_parser('show');s.add_argument('database',type=Path);s.add_argument('offset',type=int)
    s.add_argument('--section',choices=['evidence','calls','constants','c','assembly'],default='evidence')
    a=p.parse_args()
    if a.command=='build':build(a.source,a.index,a.output,a.exports)
    else:
        value=search(a.database,a.term,a.limit) if a.command=='search' else show(a.database,a.offset,a.section)
        print(value if isinstance(value,str) else json.dumps(value,indent=2,ensure_ascii=False))
