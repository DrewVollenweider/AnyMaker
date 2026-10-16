"""Copy and index already-downloaded Anymaker Workshop examples; never execute content."""
import argparse
from collections import Counter
import hashlib
import html
import json
from pathlib import Path
import anymaker as am


def script_fields(value, path=''):
    found=[]
    if isinstance(value,dict):
        for key,item in value.items():
            p=path+'/'+key
            if isinstance(item,str) and (key.lower() in ('script','source','code') or 'on_tick' in item):
                found.append({'path':p,'text':item})
            else: found.extend(script_fields(item,p))
    elif isinstance(value,list):
        for i,item in enumerate(value): found.extend(script_fields(item,path+'/'+str(i)))
    return found


def build(source,name):
    source=Path(source).resolve(); cat=am.definitions(); entries=[]; originals=[]
    folders=sorted(p for p in source.iterdir() if p.is_dir() and p.name.isdecimal() and (p/'vehicle.data').is_file())
    if not folders: raise ValueError('No downloaded Workshop creation folders found')
    # Preflight the entire destination tree before writing anything.
    for folder in folders:
        for filename in ('vehicle.data','vehicle.meta','workshop_preview.png'):
            if (folder/filename).is_file(): am.destination(f'{name}/{folder.name}/{filename}')
    for filename in ('index.json','index.html','integrity.json'):
        am.destination(f'{name}/{filename}')
    for folder in folders:
        paths=[]
        for filename in ('vehicle.data','vehicle.meta','workshop_preview.png'):
            original=folder/filename
            if not original.is_file(): continue
            raw=original.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
            target=am.destination(f'{name}/{folder.name}/{filename}'); target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as stream: stream.write(raw)
            originals.append({'source':str(original),'copy':str(target),'sha256':digest})
            paths.append(str(target))
        doc=am.load(am.OUTPUT/name/folder.name/'vehicle.data'); audit=am.audit(doc,cat); counts=Counter()
        if not am.shape_errors(doc):
            refs=am.references(doc)
            for v in am.vehicles(doc):
                for c in am.components(v):
                    if 0<=c['def']<len(refs): counts[refs[c['def']]]+=1
        scripts=script_fields(doc)
        entry={'workshop_id':folder.name,'workshop_url':f'https://steamcommunity.com/sharedfiles/filedetails/?id={folder.name}',
               'source':str(folder),'copies':paths,'component_counts':dict(counts),'audit':audit,'embedded_scripts':scripts}
        entries.append(entry)
    integrity=[dict(record,source_unchanged=hashlib.sha256(Path(record['source']).read_bytes()).hexdigest()==record['sha256'],copy_matches=hashlib.sha256(Path(record['copy']).read_bytes()).hexdigest()==record['sha256']) for record in originals]
    am.save(f'{name}/integrity.json',integrity)
    am.save(f'{name}/index.json',entries)
    am.save(f'{name}/index.html',render(entries))
    return {'creations':len(entries),'files_copied':len(integrity),'originals_unchanged':all(i['source_unchanged'] for i in integrity),'copies_match':all(i['copy_matches'] for i in integrity),'audit_errors':sum(not e['audit']['ok'] for e in entries),'script_examples':[e['workshop_id'] for e in entries if e['embedded_scripts']]}


def render(entries):
    parts=['<!doctype html><meta charset="utf-8"><title>Anymaker Workshop examples</title><style>body{font:15px system-ui;background:#111923;color:#e8f0fa;margin:24px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}article{background:#202e3f;padding:16px;border-radius:8px}img{width:100%;height:180px;object-fit:contain}a{color:#8acaff}li{margin:4px}h1{margin:0}small{color:#bdcce0}</style><h1>Downloaded Anymaker Workshop examples</h1><p>Local copies only. IDs identify sources; titles and functionality have not been verified. Audit findings are offline checks, not proof that a build works.</p><main>']
    for e in entries:
        if not e['workshop_id'].isdecimal(): raise ValueError('Workshop IDs must be numeric')
        wid=html.escape(e['workshop_id']); counts=Counter(e['component_counts']); report=e['audit']; errors=sum(i['severity']=='error' for i in report['issues']); warnings=sum(i['severity']=='warning' for i in report['issues'])
        parts.append(f'<article><h2><a href="https://steamcommunity.com/sharedfiles/filedetails/?id={wid}">Workshop {wid}</a></h2><img src="{wid}/workshop_preview.png" alt="Workshop preview {wid}"><small>{len(report["vehicles"])} bodies · {sum(counts.values())} components · {errors} errors · {warnings} warnings · {len(e["embedded_scripts"])} script fields</small><ul>')
        parts.extend(f'<li>{html.escape(k)} × {v}</li>' for k,v in counts.most_common(10))
        parts.append(f'</ul><a href="{wid}/vehicle.data">Creation copy</a></article>')
    parts.append('</main>'); return ''.join(parts)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('source'); parser.add_argument('--out',required=True); parser.add_argument('--render-index',action='store_true')
    args=parser.parse_args()
    try:
        if args.render_index: print(am.save(args.out+'/index.html',render(am.load(args.source))))
        else: print(json.dumps(build(args.source,args.out),indent=2))
    except (OSError,ValueError,KeyError,IndexError,TypeError) as error: parser.exit(1,f'Error: {error}\n')
