"""Offline Anymaker tools. Inputs are read only; outputs are new workspace files."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import os
import time

HOME = Path(__file__).resolve().parent
OUTPUT = HOME / 'output'
LINKS = ('electric_links', 'mechanical_links', 'liquid_links', 'gas_links', 'belt_links', 'data_links')
IDENTITY = [1, 0, 0, 0, 1, 0, 0, 0, 1]


def load(path):
    """Read a stable UTF-8 JSON snapshot, rejecting nonfinite JSON values."""
    path = Path(path)
    for _ in range(3):
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns):
            return json.loads(raw.decode('utf-8-sig'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f'Nonfinite JSON: {x}')))
        time.sleep(.05)
    raise ValueError(f'File changed while reading: {path}')


def destination(name):
    root = OUTPUT.resolve()
    if root != OUTPUT.absolute():
        raise ValueError('The output root must not redirect through a symlink or junction')
    path = (root / name).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError('Outputs must be beneath toolset/output')
    if path.exists():
        raise ValueError(f'Refusing to overwrite: {path}')
    return path


def save(name, content):
    path = destination(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(content if isinstance(content, str) else json.dumps(content, indent=2, ensure_ascii=False, allow_nan=False) + '\n')
    return str(path)


def definitions():
    override = os.environ.get('ANYMAKER_CATALOG')
    source = Path(override) if override else HOME / 'reference/vehicle_component_definitions.json'
    if source.is_file():
        return {d['id']: d for d in load(source)['definitions']}
    if override:
        raise FileNotFoundError(source)
    for parent in HOME.parents:
        published = parent / 'public/data/definitions'
        if published.is_dir():
            return {d['id']: d for d in (load(p) for p in sorted(published.glob('*.json')))}
    raise FileNotFoundError('Set ANYMAKER_CATALOG to a native catalog JSON, or run from the AnyMaker repository containing public/data/definitions')


def vehicles(doc):
    return doc.get('vehicles', {}).get('vehicles', [])


def references(doc):
    return doc.get('definitions', {}).get('components', [])


def components(vehicle):
    return [c for g in vehicle.get('grids', []) for c in g.get('components', [])]


def finite_vector(value, length):
    return isinstance(value, list) and len(value) == length and all(type(x) in (int, float) and math.isfinite(x) for x in value)


def shape_errors(doc):
    errors = []
    def fail(path, message):
        errors.append({'severity': 'error', 'code': 'shape', 'path': path, 'message': message})
    if not isinstance(doc, dict):
        fail('/', 'Creation must be a JSON object'); return errors
    defs = doc.get('definitions', {})
    defs = defs.get('components', []) if isinstance(defs, dict) else None
    if not isinstance(defs, list) or not all(isinstance(x, str) for x in defs):
        fail('/definitions/components', 'Expected an array of component definition IDs')
    container = doc.get('vehicles')
    vs = container.get('vehicles') if isinstance(container, dict) else None
    if not isinstance(vs, list):
        fail('/vehicles/vehicles', 'Expected an array of vehicles'); return errors
    for vi, v in enumerate(vs):
        p = f'/vehicles/vehicles/{vi}'
        if not isinstance(v, dict):
            fail(p, 'Expected vehicle object'); continue
        if type(v.get('id')) is not int: fail(p+'/id', 'Expected integer ID')
        for name in ('nodes', 'edges', 'plates', 'grids') + LINKS:
            a = v.get(name, [])
            if not isinstance(a, list) or not all(isinstance(x, dict) for x in a):
                fail(p+'/'+name, 'Expected an array of objects')
        if errors: continue
        for ni, n in enumerate(v.get('nodes', [])):
            if type(n.get('id')) is not int or not finite_vector(n.get('pos', [0,0,0]), 3):
                fail(f'{p}/nodes/{ni}', 'Expected integer ID and finite 3D position')
        for ei, e in enumerate(v.get('edges', [])):
            if any(type(e.get(k)) is not int for k in ('n0','n1')): fail(f'{p}/edges/{ei}', 'Expected integer endpoint IDs')
        for pi, plate in enumerate(v.get('plates', [])):
            if not isinstance(plate.get('nodes'), list) or not all(type(n) is int for n in plate['nodes']):
                fail(f'{p}/plates/{pi}', 'Expected node ID array')
        for gi, g in enumerate(v.get('grids', [])):
            cs = g.get('components', [])
            if not isinstance(cs, list) or not all(isinstance(c, dict) for c in cs):
                fail(f'{p}/grids/{gi}', 'Expected component array'); continue
            for ci, c in enumerate(cs):
                cp = f'{p}/grids/{gi}/components/{ci}'
                if type(c.get('id')) is not int or type(c.get('def')) is not int: fail(cp, 'Expected integer ID and definition index')
                if not finite_vector(c.get('pos', [0,0,0]), 3): fail(cp+'/pos', 'Expected finite 3D position')
                if not finite_vector(c.get('rot', IDENTITY), 9): fail(cp+'/rot', 'Expected finite 3x3 rotation')
        for name in LINKS:
            for li, link in enumerate(v.get(name, [])):
                for end in ('p0','p1'):
                    e = link.get(end)
                    if not isinstance(e, dict) or type(e.get('comp')) is not int or ('pos' in e and type(e['pos']) is not int):
                        fail(f'{p}/{name}/{li}/{end}', 'Expected component ID and optional integer node index')
    return errors


def partitions(ids, pairs):
    adj = {i: set() for i in ids}
    for a,b in pairs:
        if a in adj and b in adj:
            adj[a].add(b); adj[b].add(a)
    groups = []
    unseen = set(ids)
    while unseen:
        todo = [min(unseen)]; group = set()
        while todo:
            i = todo.pop()
            if i in group: continue
            group.add(i); todo.extend(adj[i] - group)
        unseen -= group; groups.append(sorted(group))
    return groups


def audit(doc, catalog=None):
    catalog = definitions() if catalog is None else catalog
    issues = shape_errors(doc)
    result = {'issues': issues, 'vehicles': [], 'limits': [
        'Offline checks do not prove game loadability or successful physics.',
        'Frame graph groups exclude component attachment and welded geometry.',
        'Logic node indexes use the observed zero-based endpoint convention; omitted definition fields remain unknown.',
        'No collision, watertightness, torque continuity, or spatial mating certification is performed.']}
    if issues: result['ok'] = False; return result
    refs = references(doc)
    def issue(severity, code, path, message):
        issues.append(dict(severity=severity, code=code, path=path, message=message))
    seen_v = set()
    for vi,v in enumerate(vehicles(doc)):
        p = f'/vehicles/vehicles/{vi}'
        if v['id'] in seen_v: issue('error','duplicate_vehicle',p,'Duplicate vehicle ID')
        seen_v.add(v['id'])
        cs = components(v); byid = {}; types = Counter()
        for ci,c in enumerate(cs):
            cp = p+f'/components(id={c["id"]})'
            if c['id'] in byid: issue('error','duplicate_component',cp,'Duplicate component ID within vehicle')
            byid[c['id']] = c
            if not 0 <= c['def'] < len(refs):
                issue('error','definition_index',cp,'Definition index is out of range'); continue
            kind = refs[c['def']]; types[kind] += 1
            if kind not in catalog: issue('warning','unknown_definition',cp,f'No copied definition for {kind}')
            rot = c.get('rot', IDENTITY)
            rows = [rot[i:i+3] for i in (0,3,6)]
            det = (rot[0]*(rot[4]*rot[8]-rot[5]*rot[7])-rot[1]*(rot[3]*rot[8]-rot[5]*rot[6])+rot[2]*(rot[3]*rot[7]-rot[4]*rot[6]))
            if abs(det-1)>1e-5 or any(abs(sum(x*y for x,y in zip(a,b))-(1 if i==j else 0))>1e-5 for i,a in enumerate(rows) for j,b in enumerate(rows)):
                issue('error','rotation',cp,'Rotation is not a proper orthonormal matrix')
        nodes = {}
        for n in v.get('nodes', []):
            if n['id'] in nodes: issue('error','duplicate_node',p+'/nodes','Duplicate frame node ID')
            nodes[n['id']] = n.get('pos',[0,0,0])
        pairs = []; edge_set = set()
        for ei,e in enumerate(v.get('edges', [])):
            a,b = e['n0'],e['n1']; ep=p+f'/edges/{ei}'
            if a not in nodes or b not in nodes: issue('error','dangling_edge',ep,'Edge references missing node'); continue
            if a==b or nodes[a]==nodes[b]: issue('error','zero_edge',ep,'Zero-length edge')
            pair=tuple(sorted((a,b)))
            if pair in edge_set: issue('warning','duplicate_edge',ep,'Duplicate undirected frame edge')
            edge_set.add(pair); pairs.append((a,b))
        for pi,plate in enumerate(v.get('plates', [])):
            ids=plate['nodes']; pp=p+f'/plates/{pi}'
            if len(set(ids))<3: issue('error','plate_loop',pp,'Plate needs at least three distinct nodes')
            if any(i not in nodes for i in ids): issue('error','dangling_plate',pp,'Plate references missing node'); continue
            if len(ids)>2:
                if any(tuple(sorted((a,b))) not in edge_set for a,b in zip(ids,ids[1:]+ids[:1])):
                    issue('warning','plate_boundary',pp,'A plate boundary segment lacks an exact frame edge; subdivision may explain it')
                pts=[nodes[i] for i in ids]; base=pts[0]; normal=None
                for k in range(1,len(pts)-1):
                    a=[pts[k][j]-base[j] for j in range(3)]; b=[pts[k+1][j]-base[j] for j in range(3)]
                    cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
                    norm=math.sqrt(sum(x*x for x in cross))
                    if norm>1e-8: normal=[x/norm for x in cross]; break
                if normal is None: issue('error','plate_degenerate',pp,'Plate nodes are collinear')
                elif any(abs(sum(normal[j]*(q[j]-base[j]) for j in range(3)))>1e-5 for q in pts):
                    issue('error','plate_nonplanar',pp,'Plate nodes are not coplanar')
        for name in LINKS:
            for li,link in enumerate(v.get(name, [])):
                lp=p+f'/{name}/{li}'; selected=[]
                for end in ('p0','p1'):
                    e=link[end]; c=byid.get(e['comp']); selected.append(None)
                    if c is None: issue('error','dangling_link',lp+'/'+end,'Missing component endpoint'); continue
                    if not 0<=c['def']<len(refs): continue
                    definition=catalog.get(refs[c['def']])
                    if definition is None: continue
                    ns=definition.get('logic_nodes',[]); index=e.get('pos',0)
                    # create_node converts gas ordinals through get_logic_node_index.
                    # Saved valve endpoints therefore use mixed-list indexes 1/2/3.
                    # Evidence: output/shift-repair/gas-node-create.{bin,json,c}.
                    if name=='gas_links' and refs[c['def']]=='gas_valve_t':
                        if index not in [1,2,3]:
                            issue('error','native_gas_valve_node',lp+'/'+end,f'Gas valve saved gas nodes are 1, 2, 3; node {index} is invalid');continue
                    if not 0<=index<len(ns):
                        issue('warning','node_index',lp+'/'+end,f'Node {index} absent in static definition; dynamic nodes may exist'); continue
                    selected[-1]=ns[index]
                    typ=ns[index].get('type')
                    expected='mechanical_out' if name=='mechanical_links' and end=='p0' else 'mechanical_in' if name=='mechanical_links' else name.removesuffix('_links')
                    if typ is not None and typ!=expected:
                        issue('warning','link_type',lp+'/'+end,f'Declared node type {typ} differs from expected {expected}')
                if link['p0']==link['p1']: issue('warning','self_link',lp,'Same endpoint on both sides')
                if name in ('liquid_links','gas_links') and all(selected):
                    sizes=[n.get('size') for n in selected]
                    if all(s is not None for s in sizes) and sizes[0]!=sizes[1]: issue('warning','pipe_size',lp,'Declared pipe sizes differ')
        groups=partitions(nodes,pairs)
        if len(groups)>1: issue('warning','frame_groups',p,f'{len(groups)} disconnected frame-only groups; component bridges are not evaluated')
        result['vehicles'].append({'id':v['id'],'components':len(cs),'component_types':dict(types),'nodes':len(nodes),'edges':len(pairs),'plates':len(v.get('plates',[])), 'frame_groups':groups,'links':{n:len(v.get(n,[])) for n in LINKS}})
    result['ok']=not any(i['severity']=='error' for i in issues)
    result['counts']=dict(Counter(i['severity'] for i in issues))
    return result


def differences(a,b,path=''):
    result=[]
    if type(a)!=type(b): return [{'path':path or '/', 'before':a,'after':b}]
    if isinstance(a,dict):
        for k in sorted(a.keys()|b.keys()):
            p=path+'/'+k.replace('~','~0').replace('/','~1')
            if k not in a: result.append({'path':p,'added':b[k]})
            elif k not in b: result.append({'path':p,'removed':a[k]})
            else: result.extend(differences(a[k],b[k],p))
    elif isinstance(a,list):
        for i in range(max(len(a),len(b))):
            p=path+'/'+str(i)
            if i>=len(a): result.append({'path':p,'added':b[i]})
            elif i>=len(b): result.append({'path':p,'removed':a[i]})
            else: result.extend(differences(a[i],b[i],p))
    elif a!=b: result.append({'path':path or '/', 'before':a,'after':b})
    return result


def replace_pointer(doc,pointer,value):
    if not pointer.startswith('/') or pointer=='/': raise ValueError('Use a JSON pointer to an existing field')
    keys=[k.replace('~1','/').replace('~0','~') for k in pointer[1:].split('/')]
    target=doc
    for k in keys[:-1]: target=target[int(k)] if isinstance(target,list) else target[k]
    last=int(keys[-1]) if isinstance(target,list) else keys[-1]
    old=target[last]  # Replacements only; typo paths must fail.
    target[last]=deepcopy(value)
    return old


def draft(base,plan):
    """Preserve unknown fields and IDs; make explicit replacements or additions."""
    doc=deepcopy(base)
    for edit in plan.get('replace',[]): replace_pointer(doc,edit['path'],edit['value'])
    for edit in plan.get('append',[]):
        pointer=edit['path']
        if not pointer.startswith('/'): raise ValueError('Append requires a JSON pointer')
        target=doc
        for k in pointer[1:].split('/'):
            k=k.replace('~1','/').replace('~0','~')
            target=target[int(k)] if isinstance(target,list) else target[k]
        if not isinstance(target,list) or not isinstance(edit['values'],list): raise ValueError('Append requires two arrays')
        target.extend(deepcopy(edit['values']))
    vs=vehicles(doc); refs=doc.setdefault('definitions',{}).setdefault('components',[]); catalog=definitions()
    for addition in plan.get('add_components',[]):
        matches=[v for v in vs if v['id']==addition['vehicle_id']]
        if len(matches)!=1: raise ValueError('Addition must identify exactly one existing vehicle')
        v=matches[0]; kind=addition['definition']
        if kind not in catalog: raise ValueError(f'Unknown definition: {kind}')
        if kind not in refs: refs.append(kind)
        c=deepcopy(addition['component'])
        if 'id' not in c: c['id']=max((x['id'] for x in components(v)),default=0)+1
        c['def']=refs.index(kind)
        if not v.get('grids'): v['grids']=[{'components':[]}]
        v['grids'][addition.get('grid',0)].setdefault('components',[]).append(c)
    unknown=set(plan)-{'replace','append','add_components'}
    if unknown: raise ValueError(f'Unknown plan operations: {sorted(unknown)}')
    check=audit(doc)
    if not check['ok']: raise ValueError('Draft rejected: '+json.dumps([i for i in check['issues'] if i['severity']=='error']))
    return doc,check


def schematic(doc):
    if shape_errors(doc): raise ValueError('Cannot draw malformed creation')
    refs=references(doc); parts=['<!doctype html><meta charset="utf-8"><title>Anymaker schematic</title><style>body{font:14px system-ui;background:#101820;color:#eee}svg{background:#192632;margin:8px;border:1px solid #506070}h2{margin:16px}text{fill:#dfefff;font:11px monospace}</style><h1>Anymaker creation schematic</h1><p>Frame edges and component origins only. Local coordinates per vehicle; no collision or mating proof. Grid unit = 8 cm is the documented building convention. Vehicle transforms are not applied.</p>']
    for v in vehicles(doc):
        ns={n['id']:n.get('pos',[0,0,0]) for n in v.get('nodes',[])}; cs=components(v)
        pts=list(ns.values())+[c.get('pos',[0,0,0]) for c in cs]
        if not pts: continue
        parts.append(f'<h2>Vehicle {html.escape(str(v["id"]))}</h2>')
        for label,axes in [('Top X/Z',(0,2)),('Front X/Y',(0,1)),('Side Z/Y',(2,1))]:
            lo=[min(p[a] for p in pts) for a in axes]; hi=[max(p[a] for p in pts) for a in axes]
            scale=min(420/max(1,hi[0]-lo[0]),260/max(1,hi[1]-lo[1]))
            def xy(p): return 40+(p[axes[0]]-lo[0])*scale,320-(p[axes[1]]-lo[1])*scale
            parts.append(f'<svg width="510" height="360" viewBox="0 0 510 360"><text x="20" y="22">{label}</text>')
            for e in v.get('edges',[]):
                if e['n0'] not in ns or e['n1'] not in ns: continue
                x,y=xy(ns[e['n0']]); xx,yy=xy(ns[e['n1']]); parts.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="#81a9b8"/>')
            for c in cs:
                x,y=xy(c.get('pos',[0,0,0])); kind=refs[c['def']] if 0<=c['def']<len(refs) else '?'
                title=html.escape(f'{c["id"]}: {kind} {c.get("pos",[0,0,0])}')
                parts.append(f'<circle cx="{x}" cy="{y}" r="4" fill="#ffca64"><title>{title}</title></circle><text x="{x+5}" y="{y-5}">{c["id"]}</text>')
            parts.append('</svg>')
        parts.append('<ul>'+''.join(f'<li>{c["id"]}: {html.escape(refs[c["def"]] if 0<=c["def"]<len(refs) else "?")}</li>' for c in cs)+'</ul>')
    return ''.join(parts)


def systems_review(doc, catalog=None, rules=None):
    """Describe system requirements without asserting physical/runtime connectivity."""
    catalog=definitions() if catalog is None else catalog
    rules=load(HOME/'vehicle_rules.json') if rules is None else rules
    check=audit(doc,catalog)
    result={'structural_audit':check,'review_available':check['ok'],
            'functional_status':'unverified',
            'limits':['Direct saved links are listed; attachment faces, ports and shared networks are not resolved.',
                      'Requirements are review tasks, not missing-part errors or proof of a working vehicle.',
                      'Saved component state is not a continuous reading of the running game.'],
            'components':[]}
    if not check['ok']: return result
    refs=references(doc)
    for v in vehicles(doc):
        for c in components(v):
            kind=refs[c['def']]; definition=catalog.get(kind,{})
            direct=[]
            for link_type in LINKS:
                for i,link in enumerate(v.get(link_type,[])):
                    if any(link.get(p,{}).get('comp')==c['id'] for p in ('p0','p1')):
                        direct.append({'type':link_type,'index':i,'endpoints':deepcopy(link)})
            channels=[]
            for channel in definition.get('data_descriptors',[]):
                t=channel.get('type') or ''
                direction='input' if t.endswith('_input') else 'output' if t.endswith('_output') else 'unknown'
                channels.append({'name':channel.get('name'),'direction':direction,'declared_type':channel.get('type')})
            result['components'].append({'vehicle':v['id'],'id':c['id'],'definition':kind,
                'definition_known':kind in catalog,'documented_description':definition.get('description',''),
                'direct_saved_links':direct,'data_channels':channels,
                'requirements':[{'check':s,'status':'unverified'} for s in rules.get(kind,[])],
                'rule_coverage':'curated_checklist' if kind in rules else 'definition_only'})
    return result


def systems_markdown(result):
    def text(value): return html.escape(str(value)).replace('\\','\\\\').replace('`','\\`').replace('|','\\|').replace('\n',' ')
    lines=['# Vehicle systems review','','Functional behavior remains unverified. Structural checks and documented requirements are listed separately.','']
    if 'source' in result: lines.extend(['Source: '+text(result['source']), ''])
    lines.append('Structural audit: '+('passed implemented checks' if result['structural_audit']['ok'] else 'has errors; systems review withheld')+'.')
    lines.extend(['','## Limits','']+['- '+s for s in result['limits']])
    issues=result['structural_audit']['issues']
    if issues:
        lines.extend(['','## Structural findings',''])
        lines.extend('- '+text(x['severity'])+': '+text(x['message']) for x in issues)
    if not result['review_available']: return '\n'.join(lines)+'\n'
    groups={}
    for c in result['components']: groups.setdefault(c['definition'],[]).append(c)
    for kind,cs in sorted(groups.items()):
        lines.extend(['','## '+text(kind)+f' ({len(cs)})','',text(cs[0]['documented_description']) or 'No documented description available.','',
                      'Instances: '+', '.join(f"vehicle {c['vehicle']}, component {c['id']}" for c in cs)+'.',''])
        requirements=cs[0]['requirements']
        lines.extend(['- [ ] '+text(x['check']) for x in requirements] or ['No curated checklist yet; review the definition and interfaces.'])
        channels=cs[0]['data_channels']
        if channels:
            lines.extend(['','Data channels: '+', '.join(text(x['name'])+' ('+x['direction']+')' for x in channels)+'.'])
        lines.extend(['','Direct saved links by instance:',''])
        for c in cs:
            counts=Counter(x['type'] for x in c['direct_saved_links'])
            links=', '.join(f'{text(k)}: {n}' for k,n in sorted(counts.items())) or 'none recorded directly on this component'
            lines.append(f"- Vehicle {c['vehicle']}, component {c['id']}: {links}.")
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    for name in ('inspect','audit','view'):
        p=sub.add_parser(name); p.add_argument('file'); p.add_argument('--out')
    p=sub.add_parser('systems'); p.add_argument('file'); p.add_argument('--markdown',action='store_true'); p.add_argument('--out')
    p=sub.add_parser('catalog'); p.add_argument('query',nargs='?',default=''); p.add_argument('--full',action='store_true'); p.add_argument('--items',action='store_true'); p.add_argument('--out')
    p=sub.add_parser('diff'); p.add_argument('before'); p.add_argument('after'); p.add_argument('--out')
    p=sub.add_parser('clone'); p.add_argument('file'); p.add_argument('--out',required=True)
    p=sub.add_parser('draft'); p.add_argument('base'); p.add_argument('plan'); p.add_argument('--out',required=True)
    p=sub.add_parser('snapshot'); p.add_argument('file'); p.add_argument('--out',required=True)
    p=sub.add_parser('scan'); p.add_argument('directory'); p.add_argument('--out')
    p=sub.add_parser('interfaces'); p.add_argument('definition'); p.add_argument('--with-definition',dest='other'); p.add_argument('--out')
    args=parser.parse_args(); result=None; code=0
    if args.command=='catalog':
        cat=load(HOME/'reference/inventory_definitions.json')['definitions'] if args.items else list(definitions().values())
        found=[d for d in cat if args.query.lower() in (' '.join(str(d.get(k,'')) for k in ('id','name','class','description'))).lower()]
        result=found if args.full else [{k:d[k] for k in ('id','name','class','description','data_descriptors') if k in d} for d in found]
    elif args.command in ('inspect','audit'):
        doc=load(args.file); check=audit(doc)
        result=check if args.command=='audit' else {'source':str(Path(args.file).resolve()), 'summary':check['vehicles'], 'issues':check['issues'], 'limits':check['limits']}
        if args.command=='inspect' and not shape_errors(doc):
            refs=references(doc); cat=definitions()
            result['component_details']=[{'vehicle':v['id'],'id':c['id'],'definition':refs[c['def']] if 0<=c['def']<len(refs) else None,'saved_fields':c,'data_channels':cat.get(refs[c['def']],{}).get('data_descriptors',[]) if 0<=c['def']<len(refs) else []} for v in vehicles(doc) for c in components(v)]
        code=0 if check['ok'] else 2
    elif args.command=='systems':
        result=systems_review(load(args.file)); result['source']=str(Path(args.file).resolve())
        code=0 if result['structural_audit']['ok'] else 2
        if args.markdown: result=systems_markdown(result)
    elif args.command=='view': result=schematic(load(args.file))
    elif args.command=='diff': result={'comparison':'JSON pointers; array indexes are positional, not stable identities', 'changes':differences(load(args.before),load(args.after))}
    elif args.command=='clone':
        doc=load(args.file)
        if not audit(doc)['ok']: raise ValueError('Source has audit errors; no draft written')
        result=doc
    elif args.command=='draft':
        base=load(args.base)
        doc,check=draft(base,load(args.plan))
        # Preflight all outputs so an existing report cannot produce a partial bundle.
        for name in (args.out,args.out+'.audit.json',args.out+'.changes.json'): destination(name)
        save(args.out+'.audit.json',check); save(args.out+'.changes.json',{'changes':differences(base,doc)})
        result=doc
    elif args.command=='snapshot':
        doc=load(args.file); raw=json.dumps(doc,ensure_ascii=False,allow_nan=False).encode()
        for name in (args.out,args.out+'.snapshot.json'): destination(name)
        save(args.out+'.snapshot.json',{'source':str(Path(args.file).resolve()),'captured_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'serialized_content_sha256':hashlib.sha256(raw).hexdigest()})
        result=doc
    elif args.command=='scan':
        cat=definitions(); result=[]
        for path in sorted(Path(args.directory).glob('*.data')):
            try:
                check=audit(load(path),cat)
                result.append({'file':str(path.resolve()),'ok':check['ok'],'vehicles':check['vehicles'],'issues':check['issues']})
            except (OSError,ValueError,KeyError,TypeError,IndexError) as error:
                result.append({'file':str(path.resolve()),'ok':False,'read_error':str(error)})
        if not result: raise ValueError('No .data creation files found')
        code=0 if all(r['ok'] for r in result) else 2
    elif args.command=='interfaces':
        cat=definitions(); d=cat[args.definition]
        result={k:d.get(k,[]) for k in ('surfaces','logic_nodes','data_descriptors')}
        result['definition']=args.definition
        if args.other:
            other=cat[args.other]; candidates=[]
            for i,a in enumerate(d.get('surfaces',[])):
                for j,b in enumerate(other.get('surfaces',[])):
                    if a.get('type') is None or a.get('type')!=b.get('type'): continue
                    if 'gender' in a and 'gender' in b and a['gender']==b['gender']: continue
                    candidates.append({'a_surface':i,'b_surface':j,'type':a['type'],'a':a,'b':b})
            result['candidate_surfaces']=candidates
            result['limit']='Type/gender candidates only. Size coverage, spatial alignment, rotation, gender defaults and game mating semantics require verification.'
    if args.out: print(save(args.out,result))
    elif isinstance(result,str): print(result)
    else: print(json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False))
    return code


if __name__=='__main__':
    try: sys.exit(main())
    except (OSError,ValueError,KeyError,IndexError,TypeError) as error:
        print(f'Error: {error}',file=sys.stderr); sys.exit(1)
