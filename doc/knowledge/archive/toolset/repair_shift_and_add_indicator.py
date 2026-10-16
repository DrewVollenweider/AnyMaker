"""Fix native pneumatic valve endpoint IDs and add an actual-gear display."""
import archive_paths as ap
from copy import deepcopy
from pathlib import Path
from datetime import datetime
from itertools import product
import hashlib,json,math
import anymaker as a
import structural_mounts as sm

NAME='Giant_Engine_Test_Vehicle_01'
SOURCE=ap.creation('')/(NAME+'.data')
OUT=a.OUTPUT/'shift-repair'/datetime.now().strftime('%Y%m%d-%H%M%S');OUT.mkdir()
raw=SOURCE.read_bytes();doc=a.load(SOURCE);before=deepcopy(doc)
assert json.loads(raw)==doc
(OUT/'before.data').write_bytes(raw)
for ext in ['meta','png']:(OUT/('before.'+ext)).write_bytes(SOURCE.with_suffix('.'+ext).read_bytes())
v=a.vehicles(doc)[0];refs=a.references(doc);cs={c['id']:c for c in a.components(v)}
cat=a.definitions()
assert len(cs)==95 and len(v['grids'])==1
old_audit=a.audit(before,cat)
assert not any(x['severity']=='error' for x in old_audit['issues'])

# Constructor gas ordinals 0/1/2 convert to saved logic indexes 1/2/3.
# Saved node 1 common joins 3 at rest and 2 when selected.
fixed=[]
for l in v['gas_links']:
    for end in ['p0','p1']:
        e=l[end]
        if e['comp'] not in [130,131]:continue
        other=l['p1' if end=='p0' else 'p0']['comp']
        wanted=2 if other==129 else 3 if other in [132,133] else 1 if other in [125,126] else None
        assert wanted is not None
        old=e.get('pos',0)
        if wanted:e['pos']=wanted
        else:e.pop('pos',None)
        fixed.append({'valve':e['comp'],'other':other,'before':old,'after':wanted})
cs[108]['user_defined_alias']='DriveGearbox'
cs[108].update(current=0,target=0,clutch=1.0,shift_up_triggered=False,shift_down_triggered=False)
chamber_capacity=(math.pi*2+4/3*math.pi)*.512*.1
for key in ['content_shift_up','content_shift_down']:cs[108][key]={'air':chamber_capacity*.998,'exhaust':chamber_capacity*.002,'temp':20.0}
cs[127]['content']={'air':79.84,'exhaust':.16,'temp':20.0}
for i in [130,131]:cs[i]['is_output_left']=False

I=a.IDENTITY;RX90=[1,0,0,0,0,1,0,-1,0]
RZ90=[0,1,0,-1,0,0,0,0,1];RZNEG90=[0,-1,0,1,0,0,0,0,1]
ids={};nextid=max(cs)
def add(name,kind,pos,rot=None,**kw):
    global nextid
    if kind not in refs:refs.append(kind)
    nextid+=1;c={'id':nextid,'def':refs.index(kind),'pos':pos,'colors':[79]*10}
    if rot is not None:c['rot']=rot
    c.update(kw);v['grids'][0]['components'].append(c);cs[nextid]=c;ids[name]=nextid
    return nextid
script='''on_tick
{
    in Gear.display_value = to_fractional (out DriveGearbox.current_gear)
    in Gear.is_illuminated = true
    in Reverse.is_illuminated = out DriveGearbox.current_gear < 0
}
'''
mc=add('controller','microcontroller',[-7,9,-25],script=script,global_inputs=[],global_outputs=[],global_private=[],user_defined_alias='GearDisplayController')
power=add('controller_power','electric_port_straight',[-8,9,-25],RZ90)
data=add('controller_data','data_port_straight',[-6,9,-25],RZNEG90)
gbdata=add('gearbox_data','data_port_straight',[0,20,27])
digit=add('gear_digit','7_segment_lcd_display_backlight_1',[5,14,-28],RX90,user_defined_alias='Gear')
rev=add('reverse_light','light_indicator_round_b',[7,14,-28],RX90,user_defined_alias='Reverse')
cs[rev]['colors'][0]=25
def link(kind,x,y,xp=0,yp=0,points=None):
    l={'p0':{'comp':x},'p1':{'comp':y},'points':points or []}
    if xp:l['p0']['pos']=xp
    if yp:l['p1']['pos']=yp
    v.setdefault(kind,[]).append(l)
link('electric_links',power,82,points=[[-9,9,-25],[-11,9,-25],[-11,20,-25],[-11,20,8],[-3,20,8]])
link('data_links',data,gbdata,points=[[-6,10,-25],[11,10,-25],[11,23,-25],[11,23,27],[0,23,27]])
link('data_links',data,digit,points=[[-6,7,-25],[5,7,-25],[5,7,-30],[5,14,-30]])
link('data_links',data,rev,yp=1,points=[[-6,7,-25],[7,7,-25],[7,7,-30],[7,14,-30]])

# Front instrument panel faces the driver (+Z), with direct beam mounts for
# both instruments and an explicit floor mount below the controller.
positions={n['id']:tuple(n['pos']) for n in v['nodes']};bypos={p:i for i,p in positions.items()};nextnode=max(positions);added=[]
def node(p):
    global nextnode
    p=tuple(p)
    if p not in bypos:
        nextnode+=1;bypos[p]=nextnode;positions[nextnode]=p;v['nodes'].append({'id':nextnode,'pos':list(p)})
    return bypos[p]
def chain(points):
    ns=[node(p) for p in points]
    for x,y in zip(ns,ns[1:]):added.append({'n0':x,'n1':y})
node((-7,8,-25))
for x in [4,8]:chain([(x,10,-25),(x,10,-29),(x,13,-29),(x,14,-29),(x,16,-29)])
chain([(4,13,-29),(8,13,-29)])
chain([(4,14,-29),(5,14,-29),(7,14,-29),(8,14,-29)])
chain([(4,16,-29),(8,16,-29)])
v['plates'].append({'id':max(p['id'] for p in v['plates'])+1,'nodes':[node(p) for p in [(4,13,-29),(8,13,-29),(8,16,-29),(4,16,-29)]],'glass_impacts':[]})
def along(p,q,r):
    d=tuple(q[i]-p[i] for i in range(3));x=tuple(r[i]-p[i] for i in range(3))
    return all(d[i]*x[j]==d[j]*x[i] for i,j in [(0,1),(0,2),(1,2)]) and all(min(p[i],q[i])<=r[i]<=max(p[i],q[i]) for i in range(3))
def ordered(p,q):return sorted([i for i,r in positions.items() if along(p,q,r)],key=lambda i:sum((positions[i][j]-p[j])**2 for j in range(3)))
pairs=set();edges=[]
for e in v['edges']+added:
    hits=ordered(positions[e['n0']],positions[e['n1']])
    for x,y in zip(hits,hits[1:]):
        key=tuple(sorted((x,y)))
        if key in pairs:continue
        pairs.add(key);item=deepcopy(e);item.update(n0=x,n1=y);edges.append(item)
v['edges']=edges
for p in v['plates']:
    ns=p['nodes'];loop=[]
    for x,y in zip(ns,ns[1:]+ns[:1]):loop.extend(ordered(positions[x],positions[y])[:-1])
    p['nodes']=loop

def cells(c):
    d=cat[refs[c['def']]];res=set()
    for z in d.get('zones',[]):
        if z.get('is_physics',True) is False:continue
        lo=sm.stretch(c,d,z.get('bounds_min',(0,0,0)));hi=sm.stretch(c,d,z.get('bounds_max',(0,0,0)))
        res.update(sm.world(c,p) for p in product(*(range(lo[i],hi[i]+1) for i in range(3))))
    return res
occupied={i:cells(c) for i,c in cs.items()}
for i in ids.values():
    for j in cs:
        if j!=i:assert not occupied[i]&occupied[j],(i,j,occupied[i]&occupied[j])
solid=set().union(*occupied.values())
for e in added:
    p,q=positions[e['n0']],positions[e['n1']];steps=max(abs(q[i]-p[i]) for i in range(3))*4
    for t in range(steps+1):
        sample=[p[i]+(q[i]-p[i])*t/max(steps,1) for i in range(3)];near=tuple(round(x) for x in sample)
        assert near not in solid or not all(abs(sample[i]-near[i])<.45 for i in range(3)),(e,near)

def mating(x,y):
    # Certified face mate, not mere neighboring occupied voxels.
    return any(s['type']=='port' and t['type']=='port' and s['normal']==tuple(-v for v in t['normal']) and sm.overlap(sm.add(s['lo'],s['normal']),sm.add(s['hi'],s['normal']),t['lo'],t['hi']) for s in sm.surfaces(cs[x],cat[refs[cs[x]['def']]]) for t in sm.surfaces(cs[y],cat[refs[cs[y]['def']]]))
for x,y in [(mc,power),(mc,data),(108,gbdata)]:assert mating(x,y),(x,y)
check=sm.audit(doc,cat);assert len(check['islands'])==1,check['disconnected_components']
audit=a.audit(doc,cat);assert not any(x['severity']=='error' for x in audit['issues']),audit['issues']

# Independently trace the native valve truth table against the saved pipes.
def reachable(shift):
    g={}
    def join(x,y):g.setdefault(x,set()).add(y);g.setdefault(y,set()).add(x)
    for l in v['gas_links']:
        if min(l['p0']['comp'],l['p1']['comp'])<125:continue
        join((l['p0']['comp'],l['p0'].get('pos',0)),(l['p1']['comp'],l['p1'].get('pos',0)))
    for n in [1,2]:join((129,0),(129,n))
    for valve in [130,131]:join((valve,1),(valve,2 if valve==shift else 3))
    def flood(start):
        seen={start};queue=[start]
        while queue:
            for x in g.get(queue.pop(),set())-seen:seen.add(x);queue.append(x)
        return seen
    return {port:flood((port,0)) for port in [125,126]}
truth=[]
for activated in [None,130,131]:
    net=reachable(activated)
    for valve,port,vent in [(130,125,132),(131,126,133)]:
        supplied=(128,0) in net[port];vented=(vent,0) in net[port]
        assert supplied==(valve==activated) and vented==(valve!=activated)
    truth.append({'active_valve':activated,'up_supplied':(128,0) in net[125],'down_supplied':(128,0) in net[126]})
assert SOURCE.read_bytes()==raw,'Source changed during build'
for ext,obj in [('data',doc),('meta',a.load(SOURCE.with_suffix('.meta')))]:
    (OUT/(NAME+'.'+ext)).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf-8')
(OUT/(NAME+'.png')).write_bytes(SOURCE.with_suffix('.png').read_bytes())
report={'before_sha256':hashlib.sha256(raw).hexdigest(),'fixed_endpoints':fixed,'added_component_ids':ids,
        'native_valve_truth_table':truth,'structural_audit':check,'audit':audit,
        'script':script,'power_source_component':82,'gear_data_component':108,
        'shift_keys':{'up':'3','down':'2','handbrake':'1'},
        'indicator':'0 neutral, 1/2 forward gears; red light indicates reverse (digit clamps negative gear to 0).',
        'test_status':'Offline wiring, face, clearance and structural checks passed. Script based on existing native gear-indicator example; not compiled or run in game.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'CONTROL-GUIDE.md').write_text('Gear up: tap 3. Gear down: tap 2. Let go between shifts. Handbrake: 1.\nFront indicator: 0 = neutral, 1/2 = forward gears, red lamp = reverse. The display reads actual gearbox state.\n',encoding='utf-8')
(OUT/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob(NAME+'.*')},indent=2))
print(json.dumps({'output':str(OUT),'parts':len(cs),'ids':ids,'native_truth_table':truth,'issues':audit['issues']},indent=2))
