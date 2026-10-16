"""Build a separate native test vehicle around the user-tested giant engine."""
import archive_paths as ap
from copy import deepcopy
from itertools import product
from pathlib import Path
from datetime import datetime
import hashlib
import json
import math
import sys
import anymaker as a

NAME = 'Giant_Engine_Test_Vehicle_01'
SOURCE = Path(sys.argv[1]) if len(sys.argv)>1 else ap.creation('giantenginetest.data')
OUT = a.OUTPUT / 'giant-engine-vehicle-01' / datetime.now().strftime('%Y%m%d-%H%M%S')
OUT.mkdir()
raw = SOURCE.read_bytes()
before = a.load(SOURCE)
assert before == json.loads(raw) and raw == SOURCE.read_bytes()
(OUT/'source-giantenginetest.data').write_bytes(raw)
for suffix in ['meta','png']:
    (OUT/('source-giantenginetest.'+suffix)).write_bytes(SOURCE.with_suffix('.'+suffix).read_bytes())
doc = deepcopy(before)
v = a.vehicles(doc)[0]
assert len(a.vehicles(doc)) == 1 and len(v['grids']) == 1
refs = a.references(doc)
grid = v['grids'][0]
cs = {c['id']:c for c in a.components(v)}
assert refs[cs[105]['def']] == 'oil_filter' and cs[105]['acc']['item']['_type']=='oil_filter'
assert not cs[17].get('is_reverse',False) and cs[20].get('is_reverse',False)
CAT = a.definitions()
I = a.IDENTITY
RY180 = [-1,0,0,0,1,0,0,0,-1]
RY90 = [0,0,-1,0,1,0,1,0,0]
RYNEG90 = [0,0,1,0,1,0,-1,0,0]
RZ90 = [0,1,0,-1,0,0,0,0,1]
RZNEG90 = [0,-1,0,1,0,0,0,0,1]
shift = [-61,0,-130]

def plus(p,q): return [p[i]+q[i] for i in range(3)]
for c in cs.values(): c['pos'] = plus(c.get('pos',[0,0,0]),shift)
for n in v['nodes']: n['pos'] = plus(n.get('pos',[0,0,0]),shift)
for kind in a.LINKS:
    for link in v.get(kind,[]):
        if 'points' in link: link['points']=[plus(p,shift) for p in link['points']]
# Remove only the long pedestal legs, retaining the engine cradle and guards.
removed_nodes = {128,129,131,133,134,135,136,137}
assert not any(removed_nodes & set(p['nodes']) for p in v['plates'])
v['nodes']=[n for n in v['nodes'] if n['id'] not in removed_nodes]
v['edges']=[e for e in v['edges'] if not {e['n0'],e['n1']} & removed_nodes]
v['transform']={'m':I,'t':[0,0,0]}
v.pop('motion_type',None)
v['id']=1
engine_geometry_ids=set(cs)-{75,83}
assert cs[1]['pos']==[0,16,23]
cs[1]['rps']=0.0
cs[75].update(pos=[7,11,-24],rot=I,value=.2,user_defined_alias='Idle throttle 20 percent')
cs[83].update(pos=[5,11,-24],rot=I,value=0.0,user_defined_alias='Starter key')
cs[79]['is_on']=False
v['mechanical_links']=[x for x in v['mechanical_links'] if x['p0']['comp']!=75]

ids={}
next_component=max(cs)
def add(name,kind,pos,rot=None,**fields):
    global next_component
    if kind not in refs: refs.append(kind)
    next_component+=1
    c={'def':refs.index(kind),'id':next_component,'pos':list(pos),'colors':[79]*10}
    if rot is not None: c['rot']=rot
    c.update(fields)
    grid['components'].append(c);cs[c['id']]=c;ids[name]=c['id']
    return c['id']

gb=add('gearbox','gearbox_c',[0,16,30],RY180,
       user_defined_alias='Two speed transmission',current=0,target=0,clutch=1.0,
       ratio=2,gear_ratio_1=8,gear_ratio_2=4,reverse=True,
       content_shift_up={'air':.5350928151034376,'exhaust':.0010723302924253,'temp':20.0},
       content_shift_down={'air':.5350928151034376,'exhaust':.0010723302924253,'temp':20.0})
track=add('drop','gear_track',[0,7,35],ext=[0,8,0])
prop=add('prop','drive_shaft_c',[0,7,36],ext=[0,0,3])
diff=add('axle','differential_gearbox_a',[0,7,43],RY180,input=2,output=1,
         user_defined_alias='Rear axle disconnect')
ls=add('left_shaft','drive_shaft_c',[-2,7,43],RYNEG90,ext=[0,0,9])
rs=add('right_shaft','drive_shaft_c',[2,7,43],RY90,ext=[0,0,9])
for name,x,z,rot in [('front_left',-13,-22,RYNEG90),('front_right',13,-22,RY90),
                      ('rear_left',-13,43,RYNEG90),('rear_right',13,43,RY90)]:
    w=add(name,'wheel',[x,7,z],rot,stiffness=1.0,damping=.5,
          element={'acc':{'item':{'_type':'wheel4x4','id':100000+next_component+1}}})
seat=add('seat','high_back_car_seat',[0,10,-16],RY180,element={})
steer=add('controls','steering_wheel',[0,12,-24],RY180)
shifter=add('shifter','short_shifter',[-4,9,-16],RY180,input_negative=42,input_positive=43,
            user_defined_alias='Gear up down')
hb=add('handbrake','handbrake',[4,9,-16],RY180,is_on=True,value=1.0,input=41,
       user_defined_alias='Brake and driveline disconnect')
th=add('throttle_max','mechanical_junction_max',[5,9,-21])
br=add('brake_max','mechanical_junction_max',[7,9,-21])
inv=add('shift_invert','mechanical_junction_invert',[-6,9,-16])
# Small ports are deliberately created in UP then DOWN order: the native pair
# sorts fitted port component IDs before assigning the shift chambers.
up=add('shift_up_port','gas_port_straight',[-4,16,27],RZ90)
down=add('shift_down_port','gas_port_straight',[4,16,27],RZNEG90)
tank=add('shift_air','gas_tank_a',[-8,6,38],content={'air':79.84,'exhaust':.16,'temp':20.0},
         user_defined_alias='Precharged shift air')
tp=add('shift_air_port','gas_port_straight',[-8,9,38])
jt=add('shift_air_split','junction_t_gas_pipe_a',[-8,5,35])
vu=add('up_valve','gas_valve_t',[-8,5,30])
vd=add('down_valve','gas_valve_t',[-8,5,33])
ventu=add('up_vent','gas_vent',[-11,5,30])
ventd=add('down_vent','gas_vent',[-11,5,33])
up_positive=add('shift_up_positive','mechanical_junction_max',[-6,9,-20],user_defined_alias='UpPositiveOnly')
down_positive=add('shift_down_positive','mechanical_junction_max',[-8,9,-20],user_defined_alias='DownPositiveOnly')
for n in ['shift_up_port','shift_down_port','shift_air','shift_air_port','shift_air_split',
          'up_valve','down_valve','up_vent','down_vent']:
    cs[ids[n]]['colors'][0]=7

def link(kind,x,y,xp=0,yp=0,points=None,color=None):
    l={'p0':{'comp':x},'p1':{'comp':y},'points':points or []}
    if xp: l['p0']['pos']=xp
    if yp: l['p1']['pos']=yp
    if color is not None:l['color']=color
    v[kind].append(l)
def mech(x,y,xp=0,yp=0):link('mechanical_links',x,y,xp,yp)
mech(83,79)
mech(75,th)
mech(steer,th,2,1)
mech(th,2,2)
mech(th,3,2)
mech(hb,br)
mech(steer,br,1,1)
for name in ['front_left','front_right','rear_left','rear_right']:mech(br,ids[name],2,2)
mech(br,diff,2)
for name in ['front_left','front_right']:mech(steer,ids[name])
mech(shifter,up_positive)
mech(shifter,inv)
mech(inv,down_positive,1)
# Native thresholded_input activates for either sign outside +/-0.75.
# Unconnected second max input is 0, giving independent positive half-waves.
mech(up_positive,vu,2)
mech(down_positive,vd,2)
# Route the long control cables around the engine/radiator perimeter.
for l in v['mechanical_links']:
    x,y=l['p0']['comp'],l['p1']['comp']
    if x==83:l['points']=[[5,7,-24],[11,7,-24],[11,7,19],[10,20,19]]
    elif x==th and y==2:l['points']=[[11,9,-20],[11,22,-20],[11,22,3],[7,22,3]]
    elif x==th and y==3:l['points']=[[11,9,-20],[11,22,-20],[11,22,-7],[-11,22,-7],[-11,22,3],[-7,22,3]]
    elif x==steer and y==th:l['points']=[[-1,9,-30],[-9,9,-30],[-9,9,-20]]
    elif x==steer and y==br:l['points']=[[1,9,-30],[9,9,-30],[9,9,-20]]
    elif x==br and y==diff:l['points']=[[11,9,-20],[11,9,39],[0,9,39],[0,8,39]]
    elif x==br and y in [ids['front_left'],ids['front_right'],ids['rear_left'],ids['rear_right']]:
        side=-11 if 'left' in next(k for k,j in ids.items() if j==y) else 11
        z=cs[y]['pos'][2];l['points']=[[side,9,-20],[side,9,z]]
    elif x==steer and y in [ids['front_left'],ids['front_right']]:
        side=-11 if y==ids['front_left'] else 11
        z=-24 if side<0 else -20
        l['points']=[[side,14,-26],[side,7,-26],[side,7,z]]
    elif x==shifter and y==up_positive:l['points']=[[-6,7,-16],[-6,7,-20]]
    elif x==inv and y==down_positive:l['points']=[[-6,7,-17],[-8,7,-17],[-8,7,-20]]
    elif x==up_positive and y==vu:l['points']=[[-6,7,-19],[-11,7,-19],[-11,7,30],[-8,6,30]]
    elif x==down_positive and y==vd:l['points']=[[-8,7,-19],[-11,7,-19],[-11,7,33],[-8,6,33]]
link('gas_links',tp,jt,points=[[-8,9,36],[-8,5,36]],color=7)
link('gas_links',jt,vu,1,2,points=[[-6,5,35],[-6,5,29],[-7,5,29]],color=7)
link('gas_links',jt,vd,2,2,points=[[-8,5,36],[-6,5,36],[-6,5,33]],color=7)
link('gas_links',vu,ventu,3,points=[[-9,5,30],[-11,5,30]],color=7)
link('gas_links',vd,ventd,3,points=[[-9,5,33],[-11,5,33]],color=7)
link('gas_links',vu,up,1,points=[[-8,5,31],[-6,5,31],[-6,16,31],[-6,16,27]],color=7)
link('gas_links',vd,down,1,points=[[-8,5,34],[5,5,34],[5,16,34],[5,16,27]],color=7)

# Build an open chassis, cabin floor, small console and rear pneumatic shelf.
by_pos={tuple(n['pos']):n['id'] for n in v['nodes']}
node_positions={n['id']:tuple(n['pos']) for n in v['nodes']}
next_node=max(node_positions)
new_edges=[]
def node(p):
    global next_node
    p=tuple(p)
    if p not in by_pos:
        next_node+=1;by_pos[p]=next_node;node_positions[next_node]=p
        v['nodes'].append({'id':next_node,'pos':list(p)})
    return by_pos[p]
def beam(p,q):
    if tuple(p)!=tuple(q): new_edges.append((node(p),node(q)))
def rectangle(x0,x1,y,z0,z1,plate=False):
    # Native panels attach components on the front side. Upward floors need +Y.
    pts=[(x0,y,z0),(x0,y,z1),(x1,y,z1),(x1,y,z0)]
    for p,q in zip(pts,pts[1:]+pts[:1]):beam(p,q)
    if plate:new_plates.append(pts)
new_plates=[]
stations=[-33,-29,-11,0,12,25,29,35,41,49]
for x in [-12,12]:
    for p,q in zip(stations,stations[1:]):beam((x,4,p),(x,4,q))
for z in stations:beam((-12,4,z),(12,4,z))
rectangle(-7,7,4,0,25,True)
rectangle(-10,10,8,-29,-11,True)
for x in [-10,10]:
    for z in [-29,-11]:beam((x,8,z),(x,4,z))
for x in [-12,12]:
    for axle_z in [-22,43]:
        for z in [axle_z-3,axle_z+3]:beam((x,4,z),(x,12,z))
        beam((x,10,axle_z-3),(x,10,axle_z+3))
for z in [-22,43]:
    beam((-12,5,z),(12,5,z))
    for x in [-12,12]:beam((x,4,z),(x,5,z))
for x in [-8,8]:
    for z in [0,25]:beam((x,12,z),(12 if x>0 else -12,4,z))
rectangle(4,8,10,-25,-21,True)
for z in [-25,-21]:beam((-10,8,z),(10,8,z))
for x in [4,8]:
    for z in [-25,-21]:beam((x,8,z),(x,10,z))
rectangle(-12,-5,4,29,41,True)
# Supports under the drop box and rear axle, avoiding their rotating shafts.
beam((-3,5,35),(3,5,35))
for x in [-3,3]:beam((x,4,35),(x,5,35))

# Direct node mounts prevent components relying solely on panel attachment.
for chain in [[(4,10,-24),(5,10,-24),(7,10,-24),(8,10,-24)],
              [(-10,8,-16),(-6,8,-16),(10,8,-16)],
              [(-12,4,38),(-8,4,38),(-5,4,38)]]:
    for p,q in zip(chain,chain[1:]):beam(p,q)
for z in [30,33]:
    chain=[(-12,4,z),(-11,4,z),(-8,4,z),(-5,4,z)]
    for p,q in zip(chain,chain[1:]):beam(p,q)
chain=[(-10,8,-20),(-8,8,-20),(-6,8,-20),(10,8,-20)]
for p,q in zip(chain,chain[1:]):beam(p,q)

def along(p,q,r):
    d=[q[i]-p[i] for i in range(3)];a0=[r[i]-p[i] for i in range(3)]
    if any(d[i]*a0[j]!=d[j]*a0[i] for i,j in [(0,1),(0,2),(1,2)]):return False
    return all(min(p[i],q[i])<=r[i]<=max(p[i],q[i]) for i in range(3))
edge_pairs={tuple(sorted((e['n0'],e['n1']))) for e in v['edges']}
for n0,n1 in new_edges:
    p,q=node_positions[n0],node_positions[n1]
    hits=[i for i,r in node_positions.items() if along(p,q,r)]
    hits.sort(key=lambda i:sum((node_positions[i][k]-p[k])**2 for k in range(3)))
    for x,y in zip(hits,hits[1:]):
        pair=tuple(sorted((x,y)))
        if pair not in edge_pairs:edge_pairs.add(pair);v['edges'].append({'n0':x,'n1':y})
plate_id=max([p['id'] for p in v['plates']],default=0)
for pts in new_plates:
    loop=[]
    for p,q in zip(pts,pts[1:]+pts[:1]):
        hits=[i for i,r in node_positions.items() if along(p,q,r)]
        hits.sort(key=lambda i:sum((node_positions[i][k]-p[k])**2 for k in range(3)))
        loop.extend(hits[:-1])
    plate_id+=1;v['plates'].append({'id':plate_id,'nodes':loop,'glass_impacts':[]})

def rot(r,p):return [sum(r[3*j+i]*p[j] for j in range(3)) for i in range(3)]
def world(c,p):return plus(c['pos'],rot(c.get('rot',I),p))
DIRS=[[-1,0,0],[1,0,0],[0,-1,0],[0,1,0],[0,0,-1],[0,0,1]]
def face(c,which):
    d=CAT[refs[c['def']]]
    surf=next(s for s in d['surfaces'] if s.get('id')==which)
    normal=rot(c.get('rot',I),DIRS[surf.get('dir',0)])
    p=surf.get('pos',[0,0,0]);ext=c.get('ext',[0,0,0]);center=d.get('center_stretch',[.5,.5,.5])
    p=world(c,[p[i]+(ext[i] if p[i]>center[i] else 0) for i in range(3)])
    return [p[i]+.5*normal[i] for i in range(3)],normal,surf['type']
def mate(x,xf,y,yf):
    p,n,t=face(cs[x],xf);q,m,u=face(cs[y],yf)
    assert p==q and n==[-z for z in m] and t==u,(x,xf,p,n,y,yf,q,m)
    return {'a':[x,xf],'b':[y,yf],'center':p,'type':t}
torque_mates=[]
# Engine surfaces lack string IDs; select its unstretched rear torque surface.
engine_surface=CAT['opposed_engine_c']['surfaces'][0]
ep=world(cs[1],engine_surface.get('pos',[0,0,0]));en=rot(cs[1]['rot'],DIRS[engine_surface['dir']])
ep=[ep[i]+.5*en[i] for i in range(3)]
gp,gn,gt=face(cs[gb],'torque_engine')
assert ep==gp and en==[-z for z in gn] and gt=='torque_engine_c',(ep,gp,en,gn)
torque_mates.append({'a':[1,'surface0'],'b':[gb,'torque_engine'],'center':ep,'type':gt})
for args in [(gb,'torque',track,'upper_1'),(track,'lower_0',prop,'torque_1'),
             (prop,'torque_0',diff,'in'),(diff,'left',rs,'torque_1'),
             (diff,'right',ls,'torque_1'),(ls,'torque_0',ids['rear_left'],'torque'),
             (rs,'torque_0',ids['rear_right'],'torque')]:
    torque_mates.append(mate(*args))

def cells(c,visual=False):
    d=CAT[refs[c['def']]];ext=c.get('ext',[0,0,0]);center=d.get('center_stretch',[.5,.5,.5]);res=set()
    for z in d.get('zones',[]):
        if not visual and z.get('is_physics',True) is False:continue
        lo=z.get('bounds_min',[0,0,0]);hi=z.get('bounds_max',[0,0,0])
        lo=[int(lo[i]+(ext[i] if lo[i]>center[i] else 0)) for i in range(3)]
        hi=[int(hi[i]+(ext[i] if hi[i]>center[i] else 0)) for i in range(3)]
        res.update(tuple(world(c,p)) for p in product(*(range(lo[i],hi[i]+1) for i in range(3))))
    return res
occupied={i:cells(c) for i,c in cs.items()}
new_ids=set(cs)-engine_geometry_ids
overlaps=[]
for x in sorted(new_ids):
    for y in cs:
        if x==y or (y in new_ids and y<x):continue
        overlap=occupied[x]&occupied[y]
        if overlap:overlaps.append({'components':[x,y],'voxels':sorted(overlap)})
assert not overlaps,overlaps

frame_conflicts=[]
all_solid=set().union(*occupied.values())
for n0,n1 in new_edges:
    p,q=node_positions[n0],node_positions[n1]
    steps=math.ceil(max(abs(q[i]-p[i]) for i in range(3))*4)
    for j in range(steps+1):
        sample=[p[i]+(q[i]-p[i])*j/max(1,steps) for i in range(3)]
        near=tuple(round(t) for t in sample)
        if near in all_solid and all(abs(sample[i]-near[i])<.45 for i in range(3)):
            frame_conflicts.append({'edge':[p,q],'sample':sample,'component_voxel':near});break
assert not frame_conflicts,frame_conflicts

audit=a.audit(doc,CAT)
assert not any(i['severity']=='error' for i in audit['issues']),audit['issues']
import structural_mounts
structural_audit=structural_mounts.audit(doc,CAT)
assert not structural_audit['disconnected_components'],structural_audit['disconnected_components']
all_bounds=[]
for c in cs.values():
    all_bounds.extend(cells(c,True))
    d=CAT[refs[c['def']]]
    if 'bounds_override_min' in d:
        all_bounds.extend(world(c,p) for p in product(*zip(d['bounds_override_min'],d['bounds_override_max'])))
all_bounds.extend(n['pos'] for n in v['nodes'])
low=[(min(p[i] for p in all_bounds)-.5)*.08 for i in range(3)]
high=[(max(p[i] for p in all_bounds)+.5)*.08 for i in range(3)]
meta={'vehicles':{'vehicles':[{'id':1,'transform':deepcopy(v['transform']),'bounds':{'min':low,'max':high}}]}}
for suffix,obj in [('data',doc),('meta',meta)]:
    path=OUT/(NAME+'.'+suffix);path.write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf-8');assert a.load(path)==obj
report={'source_sha256':hashlib.sha256(raw).hexdigest(),'component_ids':ids,'torque_mates':torque_mates,'structural_audit':structural_audit,
        'component_overlap_checks':overlaps,'new_frame_intersections':frame_conflicts,'audit':audit,'envelope_m':[high[i]-low[i] for i in range(3)],
        'gearbox':{'base_ratio':2,'gear_ratios':[8,4],'axle_reduction':2,'overall_forward_reductions':[32,16],
                   'initial':'neutral','shift':'two pneumatic valve pulses from seat short shifter'},
        'engine_circuits':'All saved component positions relative to each other and every fluid/gas/belt link retained, including filter.',
        'source_modified':False,'test_status':'Static validation only; requires in-game driving test.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'CONTROL-GUIDE.md').write_text('''# Giant Engine Test Vehicle 01

An open test chassis around the latest user-tested giant engine, including its installed oil filter. The engine test stand is preserved separately.

1. Enter the seat. The handbrake starts ON and the transmission starts in neutral.
2. Hold the console starter key to crank. Once the engine runs, tap it OFF to release the starter relay.
3. Use the seat-mounted short shifter: pulse toward up to select first gear; let it centre between shifts. A second upshift selects second gear. Downshift back through first and neutral to reverse.
4. Release the handbrake. Right pedal supplies throttle; left pedal brakes and disconnects the rear drive. Releasing the right pedal returns to the console idle-slider setting (20%). The pedals provide on/off inputs.
5. Use the steering wheel to steer the front wheels. Apply the handbrake to park and disconnect the rear drive.

The gearbox has two forward gears, neutral and reverse. Overall forward reductions are 32:1 and 16:1. The small pneumatic shift reservoir is precharged; it has a finite air supply and is intended for this initial driving test.

The engine, starter, liquid circulation, oil filter and system colors are retained. Only the idle slider and starter key moved to the console. The original tall pedestal legs were replaced by the chassis supports. No extra controller or bodywork was added.

Shaft mating, link endpoints and component clearances are checked offline. Ignition/circulation are based on the user-tested engine; the complete vehicle has not yet been driven in game. Driving, suspension loading and shift response require that first game test.
''',encoding='utf-8')

# Technical orthographic preview, not a rendered in-game screenshot.
from PIL import Image,ImageDraw,ImageFont
im=Image.new('RGB',(1600,1050),'#111923');draw=ImageDraw.Draw(im)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',28)
draw.text((28,18),'GIANT ENGINE TEST VEHICLE 01',font=title,fill='#eef3fa')
draw.text((28,58),'Layout preview · 2-speed gearbox · rear-wheel drive · original engine circuits retained',font=font,fill='#b7c7d9')
palette={25:'#ee5253',47:'#3998ee',20:'#ef9a32',7:'#e6edf5'}
for axes,origin,scale,label in [((2,0),(85,355),14,'TOP — front at left'),((2,1),(85,950),14,'SIDE — front at left')]:
    ax,ay=axes
    def project(p):return (origin[0]+(p[ax]+34)*scale,origin[1]-p[ay]*scale)
    draw.text((28,110 if ax==2 and ay==0 else 580),label,font=font,fill='#b7c7d9')
    for plate in v['plates']:
        pts=[project(node_positions[i]) for i in plate['nodes']]
        if len(set(pts))>=3:draw.polygon(pts,fill='#1d2c3c')
    for c in sorted(cs.values(),key=lambda c:c['pos'][1]):
        vox=cells(c)
        if not vox:continue
        xx=[p[ax] for p in vox];yy=[p[ay] for p in vox]
        p=project([min(xx) if i==ax else max(yy) if i==ay else 0 for i in range(3)])
        q=project([max(xx) if i==ax else min(yy) if i==ay else 0 for i in range(3)])
        color=palette.get(c['colors'][0],'#718599')
        draw.rectangle([p[0]-5,p[1]-5,q[0]+5,q[1]+5],fill=color,outline='#0d141c',width=1)
    for e in v['edges']:
        draw.line([project(node_positions[e['n0']]),project(node_positions[e['n1']])],fill='#71879b',width=2)
    for name in ['front_left','front_right','rear_left','rear_right']:
        c=cs[ids[name]];p=c['pos'];sgn=-1 if 'left' in name else 1
        if ay==0:
            center=project([p[0]+sgn*5,p[1],p[2]])
            draw.rounded_rectangle([center[0]-5.375*scale,center[1]-1.1*scale,center[0]+5.375*scale,center[1]+1.1*scale],radius=8,fill='#19212b',outline='#c1ccda',width=2)
        else:
            center=project([p[0],p[1]-.5,p[2]]);radius=5.375*scale
            draw.ellipse([center[0]-radius,center[1]-radius,center[0]+radius,center[1]+radius],fill='#19212b',outline='#c1ccda',width=2)
            draw.ellipse([center[0]-radius*.45,center[1]-radius*.45,center[0]+radius*.45,center[1]+radius*.45],fill='#64798e',outline='#c1ccda',width=2)
    for key,text in [('seat','Seat'),('gearbox','Gearbox'),('axle','Rear drive')]:
        p=project(cs[ids[key]]['pos']);draw.text((p[0]-25,p[1]+20),text,font=font,fill='#ffffff',stroke_width=2,stroke_fill='#111923')
im.save(OUT/'LAYOUT.png')
thumbnail=Image.new('RGB',(512,512),'#111923')
small=im.resize((512,336),Image.Resampling.LANCZOS)
thumbnail.paste(small,(0,88))
thumbnail.save(OUT/(NAME+'.png'))
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob(NAME+'.*')}
(OUT/'hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps({'directory':str(OUT),'hashes':hashes,'components':len(cs),
                  'torque_mates':len(torque_mates),'envelope_m':report['envelope_m'],'issues':audit['issues']},indent=2))
