"""Restore parts lost on spawn and give them explicit chassis mounts."""
import archive_paths as ap
from copy import deepcopy
from datetime import datetime
from pathlib import Path
import hashlib
import json
import math
from itertools import product
import anymaker as a
import structural_mounts as sm

ROOT=a.OUTPUT/'mount-repair'
ORIGINAL=a.OUTPUT/'giant-engine-vehicle-01'/'20261016-090752'
NAME='Giant_Engine_Test_Vehicle_01'
INSTALLED=ap.creation('')/(NAME+'.data')
OUT=ROOT/datetime.now().strftime('%Y%m%d-%H%M%S');OUT.mkdir()
raw=INSTALLED.read_bytes();current=a.load(INSTALLED);original=a.load(ORIGINAL/(NAME+'.data'))
assert current==json.loads(raw)
(OUT/'before.data').write_bytes(raw)
for ext in ['meta','png']:(OUT/('before.'+ext)).write_bytes(INSTALLED.with_suffix('.'+ext).read_bytes())
cat=a.definitions()
v=a.vehicles(current)[0];ov=a.vehicles(original)[0]
refs=a.references(current);orefs=a.references(original)
cs={c['id']:c for c in a.components(v)};ocs={c['id']:c for c in a.components(ov)}
missing=set(ocs)-set(cs)
assert missing=={75,83,124,127,128,130,131,132,133},missing
oldcheck=sm.audit(original,cat)
assert {c['id'] for c in oldcheck['disconnected_components']}==missing
for i in sorted(missing):
    c=deepcopy(ocs[i]);kind=orefs[c['def']]
    if kind not in refs:refs.append(kind)
    c['def']=refs.index(kind);v['grids'][0]['components'].append(c);cs[i]=c
restored_links={}
for kind in a.LINKS:
    oldlinks=[deepcopy(l) for l in ov.get(kind,[]) if l['p0']['comp'] in missing or l['p1']['comp'] in missing]
    assert not any(l['p0']['comp'] in missing or l['p1']['comp'] in missing for l in v.get(kind,[]))
    v.setdefault(kind,[]).extend(oldlinks);restored_links[kind]=len(oldlinks)
v['transform']=deepcopy(ov['transform'])
for p in v['plates']:
    if p['id'] in [13,14,15,16]:p['nodes'].reverse()

# Every repaired base gets a frame-node centre exactly one voxel below its
# downward mounting surface; each supporting crossmember joins existing rails.
positions={n['id']:tuple(n['pos']) for n in v['nodes']};bypos={p:i for i,p in positions.items()}
nextid=max(positions);mounts=[];added=[]
def node(p):
    global nextid
    p=tuple(p)
    if p not in bypos:
        nextid+=1;positions[nextid]=p;bypos[p]=nextid
        v['nodes'].append({'id':nextid,'pos':list(p)})
    return bypos[p]
def beam(points):
    ids=[node(p) for p in points]
    for x,y in zip(ids,ids[1:]):added.append({'n0':x,'n1':y})
beam([(4,10,-24),(5,10,-24),(7,10,-24),(8,10,-24)])
beam([(-10,8,-16),(-6,8,-16),(10,8,-16)])
beam([(-12,4,38),(-8,4,38),(-5,4,38)])
for z in [30,33]:beam([(-12,4,z),(-11,4,z),(-8,4,z),(-5,4,z)])
for i in sorted(missing-{128}):
    s=next(s for s in sm.surfaces(cs[i],cat[refs[cs[i]['def']]]) if s['normal']==(0,-1,0))
    # Choose the base origin voxel rather than the corner of the larger slider.
    pos=list(cs[i]['pos']);pos[1]=s['lo'][1]-1
    assert tuple(pos) in bypos
    assert sm.endpoint(s,tuple(pos))
    mounts.append({'component':i,'definition':refs[cs[i]['def']],'surface':s['index'],'node':bypos[tuple(pos)],'pos':pos})

def along(p,q,r):
    d=tuple(q[i]-p[i] for i in range(3));x=tuple(r[i]-p[i] for i in range(3))
    return all(d[i]*x[j]==d[j]*x[i] for i,j in [(0,1),(0,2),(1,2)]) and all(min(p[i],q[i])<=r[i]<=max(p[i],q[i]) for i in range(3))
def ordered(p,q):
    hits=[i for i,r in positions.items() if along(p,q,r)]
    return sorted(hits,key=lambda i:sum((positions[i][j]-p[j])**2 for j in range(3)))
edges=[];pairs=set()
for e in v['edges']+added:
    hits=ordered(positions[e['n0']],positions[e['n1']])
    for x,y in zip(hits,hits[1:]):
        pair=tuple(sorted((x,y)))
        if pair in pairs:continue
        pairs.add(pair);item=deepcopy(e);item.update(n0=x,n1=y);edges.append(item)
v['edges']=edges
for plate in v['plates']:
    nodes=plate['nodes'];loop=[]
    for x,y in zip(nodes,nodes[1:]+nodes[:1]):loop.extend(ordered(positions[x],positions[y])[:-1])
    plate['nodes']=loop

# Check new beams do not cross a component's occupied physical voxel core.
def cells(c):
    d=cat[refs[c['def']]];res=set()
    for z in d.get('zones',[]):
        if z.get('is_physics',True) is False:continue
        lo=sm.stretch(c,d,z.get('bounds_min',(0,0,0)));hi=sm.stretch(c,d,z.get('bounds_max',(0,0,0)))
        res.update(sm.world(c,p) for p in product(*(range(lo[i],hi[i]+1) for i in range(3))))
    return res
solid=set().union(*(cells(c) for c in cs.values()))
for e in added:
    p,q=positions[e['n0']],positions[e['n1']];steps=max(abs(q[i]-p[i]) for i in range(3))*4
    for step in range(steps+1):
        sample=[p[i]+(q[i]-p[i])*step/max(steps,1) for i in range(3)];voxel=tuple(round(x) for x in sample)
        assert voxel not in solid or not all(abs(sample[i]-voxel[i])<.45 for i in range(3)),(e,voxel)
check=sm.audit(current,cat);assert not check['disconnected_components'],check['disconnected_components']
assert len(check['islands'])==1
for m in mounts:
    assert any('edge' in c and m['node'] in c['edge'] and c['surface']==m['surface'] for c in check['contacts'][m['component']])
native=a.audit(current,cat);assert not any(i['severity']=='error' for i in native['issues'])
# All surviving component records, including user runtime state, remain intact.
snapshot=a.load(OUT/'before.data');scs={c['id']:c for c in a.components(a.vehicles(snapshot)[0])}
assert all(cs[i]==c for i,c in scs.items())
assert INSTALLED.read_bytes()==raw,'Source changed during repair'
for ext,obj in [('data',current),('meta',a.load(ORIGINAL/(NAME+'.meta')))]:
    (OUT/(NAME+'.'+ext)).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf-8')
(OUT/(NAME+'.png')).write_bytes(ORIGINAL.joinpath(NAME+'.png').read_bytes())
report={'before_sha256':hashlib.sha256(raw).hexdigest(),'restored_components':sorted(missing),'restored_links':restored_links,
        'panel_windings_corrected':[13,14,15,16],'direct_mounts':mounts,'before_attachment_audit':oldcheck,'after_attachment_audit':check,
        'file_audit':native,'all_surviving_component_records_preserved':True,
        'validation':'Attachment checker predicts exactly the nine components absent from the user spawn/save. Revised creation has one static structural island. Revised spawn not yet tested.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob(NAME+'.*')}
(OUT/'hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps({'output':str(OUT),'restored':sorted(missing),'mounts':mounts,'structural_islands':len(check['islands']),'hashes':hashes},indent=2))
