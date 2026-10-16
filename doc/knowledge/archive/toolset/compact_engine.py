"""Package the user-tested petrol engine in a compact native mounting cradle."""
from copy import deepcopy
from collections import defaultdict
from itertools import product
import hashlib
import heapq
import json
import math
from pathlib import Path
import sys
import anymaker as a

OUT = 'compact-petrol-engine-01-complete'
NAME = 'Compact_Petrol_Engine_01'
BASE = a.HOME/'output/pedestal-engine-test-01/Petrol_Pedestal_Test_01.data'
NORMALS = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
CAT = a.definitions()
RX_MINUS = [1,0,0,0,0,-1,0,1,0]
RY_PLUS = [0,0,-1,0,1,0,1,0,0]
LEFT_MOUNT_FORWARD_OUT = [0,-1,0,-1,0,0,0,0,-1]
LEFT_MOUNT_UP_OUT = [0,0,1,-1,0,0,0,-1,0]
RIGHT_PORT = [0,-1,0,1,0,0,0,0,1]
BACK_PORT = [-1,0,0,0,0,1,0,1,0]

def add(p,q): return tuple(x+y for x,y in zip(p,q))
def sub(p,q): return tuple(x-y for x,y in zip(p,q))
def rot(r,p): return tuple(sum(r[3*k+j]*p[k] for k in range(3)) for j in range(3))
def mul(r,s): return [sum(r[3*k+j]*s[3*i+k] for k in range(3)) for i in range(3) for j in range(3)]

def cells(c, definition, include_visual=True):
    result=set()
    for z in definition['zones']:
        if not include_visual and z.get('is_physics') is False: continue
        low=z.get('bounds_min',[0,0,0]); high=z.get('bounds_max',[0,0,0])[:]
        ext=c.get('ext',[0,0,0])
        high=[high[i]+ext[i] for i in range(3)]
        for p in product(*(range(low[i],high[i]+1) for i in range(3))):
            result.add(add(c['pos'],rot(c.get('rot',a.IDENTITY),p)))
    return result

def make_layout():
    doc=a.load(BASE); v=a.vehicles(doc)[0]; refs=a.references(doc)
    cs={c['id']:c for c in a.components(v)}
    originals=deepcopy(cs)
    # Preserve block, manifolds, and crank wheel as one proven relative assembly.
    for ident in (1,2,14,15,16,17,18,19,20,21,22,23):
        cs[ident]['pos']=list(add(cs[ident]['pos'],(0,-10,0)))
    groups=[(6,(3,4,6),(6,10,77)), (7,(-3,4,6),(7,13,78)),
            (8,(-3,1,6),(8,12,30,31)), (9,(3,1,6),(9,11,40,41)),
            (26,(-5,1,0),(26,27,28,29)), (32,(-5,4,7),(32,33,34)),
            (42,(3,1,0),(42,43,45,81)), (67,(5,1,4),(67,68,69,70))]
    for anchor,pos,members in groups:
        delta=sub(pos,originals[anchor]['pos'])
        for ident in members: cs[ident]['pos']=list(add(originals[ident]['pos'],delta))
    # Rotate the whole radiator/fan/port assembly together, preserving mating.
    for ident in (35,36,37,38,39,80):
        cs[ident]['pos']=list(add((-6,3,3),rot(RY_PLUS,sub(originals[ident]['pos'],originals[35]['pos']))))
        cs[ident]['rot']=mul(RY_PLUS,originals[ident].get('rot',a.IDENTITY))
    cs[24].update(pos=[4,6,3],rot=RX_MINUS)
    cs[25]['pos']=[-4,8,3]
    cs[46]['pos']=[7,5,3]
    cs[51]['pos']=[3,2,-1]
    cs[52]['pos']=[4,2,-2]
    cs[53]['pos']=[6,2,-1]
    cs[59]['pos']=[2,1,4]
    cs[71]['pos']=[7,6,0]
    cs[72]['pos']=[7,6,2]
    cs[73].update(pos=[7,6,-1],rot=RX_MINUS)
    cs[74].update(pos=[8,6,0],rot=RIGHT_PORT)
    cs[75].update(pos=[7,6,3],rot=BACK_PORT)
    cs[76].update(pos=[8,6,2],rot=RIGHT_PORT)
    # Rotate only about the mating normal; put the two hose exits into open space.
    cs[17]['rot']=LEFT_MOUNT_FORWARD_OUT
    cs[19]['rot']=LEFT_MOUNT_UP_OUT
    v['id']=1; v['transform']={'m':a.IDENTITY[:],'t':[0,0,0]}
    v['nodes']=[]; v['edges']=[]; v['plates']=[]; v['plate_paint']=[]; v['buoyancy_fill']=[]
    return doc,v,cs,refs

def cradle(v):
    segments=[]
    def line(p,q): segments.append((tuple(p),tuple(q)))
    # Low open cradle, with rails directly under tanks and pumps.
    for z in (-2,0,6,8): line((-7,0,z),(7,0,z))
    for x in (-7,-5,0,2,3,5,7): line((x,0,-2),(x,0,8))
    line((0,2,0),(0,2,7)); line((0,0,0),(0,2,0)); line((0,0,7),(0,2,7))
    line((-4,0,6),(-4,4,6))
    line((-5,0,7),(-5,3,7))
    line((-6,2,0),(-6,2,4)); line((-6,0,0),(-6,2,0)); line((-6,0,4),(-6,2,4))
    line((-3,0,3),(-3,8,3)); line((-5,0,3),(-3,0,3))
    line((7,0,2),(7,5,2)); line((7,5,0),(7,5,2))
    line((6,0,8),(6,6,8)); line((6,6,3),(6,6,8))
    line((4,0,5),(4,4,5)); line((4,4,5),(4,4,7)); line((4,0,5),(5,0,5))
    # Front control shelf remains small and outside the output shaft corridor.
    for x in (3,6): line((x,1,-2),(x,1,-1)); line((x,0,-2),(x,1,-2))
    for z in (-2,-1): line((3,1,z),(6,1,z))
    occupied=set(); pairs=set()
    for p,q in segments:
        direction=sub(q,p); changing=[i for i,x in enumerate(direction) if x]
        assert len(changing)==1
        axis=changing[0]; step=1 if direction[axis]>0 else -1
        points=[tuple(p[j]+(n*step if j==axis else 0) for j in range(3)) for n in range(abs(direction[axis])+1)]
        occupied.update(points)
        pairs.update(tuple(sorted((x,y))) for x,y in zip(points,points[1:]))
    ids={p:i+1 for i,p in enumerate(sorted(occupied))}
    v['nodes']=[{'id':ident,'pos':list(p)} for p,ident in ids.items()]
    v['edges']=[{'n0':ids[p],'n1':ids[q],'col':49} for p,q in sorted(pairs)]
    # Include every boundary node so exact-edge plate validation stays meaningful.
    boundary=[(x,1,-2) for x in range(3,7)]+[(6,1,-1)]+[(x,1,-1) for x in range(5,2,-1)]
    v['plates']=[{'id':1,'nodes':[ids[p] for p in boundary], 'col_front':49,'col_back':49,'glass_impacts':[]}]
    v['buoyancy_fill']=[0.0]
    return occupied

def node(cs,refs,endpoint):
    c=cs[endpoint['comp']]; n=CAT[refs[c['def']]]['logic_nodes'][endpoint.get('pos',0)]
    normal=rot(c.get('rot',a.IDENTITY),NORMALS[n.get('direction',0)])
    origin=add(c['pos'],rot(c.get('rot',a.IDENTITY),n.get('pos',[0,0,0])))
    return origin,normal,n

def astar(start,end,blocked,reserved,bounds):
    todo=[(sum(abs(x-y) for x,y in zip(start,end)),0,start,None)]
    parent={}; best={(start,None):0}; found=None
    while todo:
        _,cost,p,direction=heapq.heappop(todo)
        state=(p,direction)
        if cost>best.get(state,float('inf'))+1e-8: continue
        if p==end: found=state; break
        for delta in NORMALS:
            q=add(p,delta)
            if not all(bounds[i][0]<=q[i]<=bounds[i][1] for i in range(3)): continue
            if q in blocked and q not in (start,end): continue
            if q in reserved and q not in (start,end): continue
            extra=1+(0.18 if direction is not None and direction!=delta else 0)
            nxt=(q,delta); value=cost+extra
            if value+1e-8>=best.get(nxt,float('inf')): continue
            best[nxt]=value; parent[nxt]=state
            heuristic=sum(abs(x-y) for x,y in zip(q,end))
            heapq.heappush(todo,(value+heuristic,value,q,delta))
    if found is None: raise ValueError(f'No clear route: {start} -> {end}')
    points=[]
    while found is not None:
        points.append(found[0]); found=parent.get(found)
    return list(reversed(points))

def routes(v,cs,refs,component_cells,frame):
    reserved={}; records=[]
    # Large intake pipe gets space first; other lines then avoid its swept cells.
    jobs=[(family,index,link) for family in ('gas_links','liquid_links','electric_links','mechanical_links')
          for index,link in enumerate(v[family])]
    def priority(job):
        if job[0]=='gas_links' and job[2]['p0']['comp']==14: return 0
        if job[0]=='mechanical_links' and job[2]['p1']['comp']==14: return 1
        return 2
    jobs.sort(key=priority)
    bounds=[(-9,9),(0,10),(-3,10)]
    terminals=defaultdict(set)
    for family,index,link in jobs:
        for end in ('p0','p1'):
            origin,normal,n=node(cs,refs,link[end])
            terminals[add(origin,normal)].add((family,link[end]['comp'],link[end].get('pos',0)))
    if any(len(keys)>1 for keys in terminals.values()):
        raise ValueError('Unrelated terminals share a routing cell: '+str({p:ks for p,ks in terminals.items() if len(ks)>1}))
    for family,index,link in jobs:
        ends=[node(cs,refs,link[p]) for p in ('p0','p1')]
        start,end=[add(origin,normal) for origin,normal,n in ends]
        keys=[(family,link[p]['comp'],link[p].get('pos',0)) for p in ('p0','p1')]
        excluded={link['p0']['comp'],link['p1']['comp']}
        solid=set().union(*component_cells.values()) | frame
        clearance=1 if family=='gas_links' and any(n.get('size',0)==1 for _,_,n in ends) else 0
        if clearance:
            unrelated=set().union(*(points for ident,points in component_cells.items() if ident not in excluded)) | frame
            solid.update(add(p,offset) for p in unrelated for offset in product(range(-1,2),repeat=3))
        terminal_exceptions=[]
        for terminal in (start,end):
            if terminal in solid:
                if family=='mechanical_links' and terminal in frame:
                    # Buttons' control terminal shares the structural mounting face.
                    terminal_exceptions.append(terminal)
                else:
                    raise ValueError(f'{family}[{index}] blocked terminal {terminal}')
        blocked_routes={p for p,owners in reserved.items() if not owners.intersection(keys)}
        blocked_routes.update(p for p,owners in terminals.items() if not owners.intersection(keys))
        if clearance:
            # Do not reserve the large tube's halo over another circuit's
            # terminal, which would trap its later wire or hose.
            blocked_routes.update(add(p,offset) for p,owners in terminals.items()
                                  if not owners.intersection(keys)
                                  for offset in product(range(-1,2),repeat=3))
        points=astar(start,end,solid,blocked_routes,bounds)
        compact=[points[0]]
        for i in range(1,len(points)-1):
            if sub(points[i],points[i-1])!=sub(points[i+1],points[i]): compact.append(points[i])
        if points[-1]!=compact[-1]: compact.append(points[-1])
        link['points']=[list(p) for p in compact]
        # Allow only a short necessary branch near a shared physical terminal.
        # All unrelated route cells, including later jobs' terminals, are reserved.
        for p in points:
            owners={key for key,terminal in zip(keys,(start,end))
                    if sum(abs(x-y) for x,y in zip(p,terminal))<=2}
            reserved.setdefault(p,set()).update(owners)
            if clearance:
                for offset in product(range(-1,2),repeat=3):
                    reserved.setdefault(add(p,offset),set())
        records.append({'family':family,'index':index,'endpoints':[link[p] for p in ('p0','p1')],
                        'route_cells':points,'mount_contact_exceptions':terminal_exceptions,
                        'clearance_expansion_cells':clearance})
    return records

def validate_solids(cs,refs,frame):
    occupied={ident:cells(c,CAT[refs[c['def']]]) for ident,c in cs.items()}
    clashes=[]
    ids=sorted(cs)
    for i,ident in enumerate(ids):
        for other in ids[i+1:]:
            overlap=occupied[ident]&occupied[other]
            if overlap: clashes.append({'a':ident,'b':other,'cells':sorted(overlap)})
        overlap=occupied[ident]&frame
        if overlap: clashes.append({'component':ident,'frame_cells':sorted(overlap)})
    if clashes: raise ValueError('Solid overlap: '+json.dumps(clashes))
    return occupied

def preview(doc, cs, refs, occupied, frame, route_records):
    from PIL import Image,ImageDraw,ImageFont
    img=Image.new('RGB',(1500,1050),'#edf1f4'); draw=ImageDraw.Draw(img)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26)
    small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    draw.text((30,24),'COMPACT PETROL ENGINE 01 — CLEARANCE PLAN',font=font,fill='#203044')
    groups={'engine':'#ca6738','liquid_tank':'#b9a377','radiator':'#48849e','radiator_fan_b':'#347c8f',
            'battery_a':'#4d5867','electric_motor_a':'#588064','liquid_pump':'#738b74','alternator_motor':'#847851'}
    for index,(axes,title) in enumerate([((0,2),'TOP: width / length'),((0,1),'FRONT: width / height'),((2,1),'SIDE: length / height')]):
        ox=30+(index%2)*750; oy=85+(index//2)*460; scale=22
        left=ox+100; top=oy+300
        draw.text((ox,oy),title,font=font,fill='#203044')
        project=lambda p:(left+(p[axes[0]]+9)*scale,top-p[axes[1]]*scale)
        for p in frame:
            x,y=project(p); draw.rectangle((x-8,y-8,x+8,y+8),fill='#b3bec8')
        for record in route_records:
            color={'gas_links':'#598879','liquid_links':'#4d80b5','electric_links':'#c19230','mechanical_links':'#9a73a6'}[record['family']]
            points=[project(p) for p in record['route_cells']]
            if len(points)>1: draw.line(points,fill=color,width=2)
        for ident in sorted(cs):
            kind=refs[cs[ident]['def']]; points=occupied[ident]; projected=[project(p) for p in points]
            x0=min(x for x,y in projected)-10; x1=max(x for x,y in projected)+10
            y0=min(y for x,y in projected)-10; y1=max(y for x,y in projected)+10
            draw.rectangle((x0,y0,x1,y1),outline='#53677a',width=1)
            if kind in groups:
                draw.rectangle((x0,y0,x1,y1),fill=groups[kind],outline='#203044')
                draw.text((x0+2,y0+2),str(ident),font=small,fill='#ffffff')
        draw.text((ox,oy+410),'Grid spacing: 8 cm. Projections may obscure depth; 3D occupancy checks are separate.',font=small,fill='#53677a')
    draw.text((790,635),'1 Engine   6 Starter   7 Alternator',font=font,fill='#203044')
    draw.text((790,680),'8 / 9 Pumps   26 Oil tank   35 Radiator',font=font,fill='#203044')
    draw.text((790,725),'42 Petrol tank   67 Battery',font=font,fill='#203044')
    draw.text((790,785),'RUN / THROTTLE / START on front shelf',font=small,fill='#53677a')
    draw.text((790,825),'Static envelopes and routing, not game meshes.',font=small,fill='#53677a')
    with a.destination(OUT+'/'+NAME+'.png').open('xb') as stream: img.save(stream,'PNG')

def main():
    doc,v,cs,refs=make_layout()
    frame=cradle(v)
    occupied=validate_solids(cs,refs,frame)
    assert cs[2]['pos'][1] == cs[10]['pos'][1] == cs[13]['pos'][1], 'Preserve the proven upper belt-wheel alignment'
    route_records=routes(v,cs,refs,occupied,frame)
    check=a.audit(doc,CAT)
    if check['issues']: raise ValueError(json.dumps(check['issues']))
    all_points=set().union(frame,*occupied.values(),*(set(r['route_cells']) for r in route_records))
    low=[min(p[i] for p in all_points)-.5 for i in range(3)]
    high=[max(p[i] for p in all_points)+.5 for i in range(3)]
    # Include the larger intake tube's conservative full swept radius in the
    # fit envelope, rather than treating it as a one-voxel solid part.
    for record in route_records:
        radius=1.0 if record['clearance_expansion_cells'] else .5
        for i in range(3):
            low[i]=min(low[i],min(p[i] for p in record['route_cells'])-radius)
            high[i]=max(high[i],max(p[i] for p in record['route_cells'])+radius)
    dimensions=[round((high[i]-low[i])*.08,3) for i in range(3)]
    meta={'vehicles':{'vehicles':[{'id':v['id'],'transform':deepcopy(v['transform']),
                                   'bounds':{'min':[x*.08 for x in low],'max':[x*.08 for x in high]}}]}}
    report={'name':NAME,'reference':str(BASE),'reference_sha256':hashlib.sha256(BASE.read_bytes()).hexdigest(),
            'components':len(cs),'bounding_dimensions_m_xyz':dimensions,
            'solid_component_overlaps':[], 'component_frame_overlaps':[],
            'audit':check,'routing':route_records,
            'limits':['Native zone-based static clearance; exact meshes and hose diameters are not fully decoded.',
                      'Large intake route uses one cell extra clearance; small pipes/wires use free cells.',
                      'Mechanical terminals intentionally share a control mounting face.',
                      'Compact layout needs a fresh in-game test; sustained oil/coolant circulation remains unresolved from the pedestal test.']}
    for file in (NAME+'.data',NAME+'.meta',NAME+'.png','validation.json','README.md','schematic.html'):
        a.destination(OUT+'/'+file)
    a.save(OUT+'/'+NAME+'.data',json.dumps(doc,separators=(',',':'),allow_nan=False))
    a.save(OUT+'/'+NAME+'.meta',json.dumps(meta,separators=(',',':'),allow_nan=False))
    a.save(OUT+'/validation.json',report)
    a.save(OUT+'/schematic.html',a.schematic(doc))
    a.save(OUT+'/README.md',f'''# Compact Petrol Engine 01

Vehicle-sized packaging of the user-tested four-cylinder petrol pedestal engine.
Static envelope (width × height × length): {dimensions[0]} × {dimensions[1]} × {dimensions[2]} m.
The original pedestal and the user-exported running version remain intact.

All 60 components, fluid circuits, fitted items, belt reversal settings and control
logic are retained. Initial state uses the original fresh build: RUN off, throttle
15%, starter released, charged battery and replenished fluids. No gearbox is added;
the engine's forward torque face is left accessible for a matching small gearbox.

RUN, THROTTLE and START are on the small front control shelf. Turn RUN on, then hold
START until the engine catches; release START. RUN off shuts the intake throttle.

Static checks find no overlapping component-zone cells, including decorative zones,
and no component/frame intersections. Adjacent mating faces are intentional. Hose
and wire paths avoid unrelated occupied cells, with terminal mounting exceptions.
This is a compact test revision, not a certified in-game vehicle installation.
The earlier exported running state left the radiator empty; long-duration cooling
and oil return flow must still be checked. Packaging does not claim to fix that.
''')
    preview(doc,cs,refs,occupied,frame,route_records)
    print(json.dumps({'name':NAME,'dimensions_xyz_m':dimensions,'components':len(cs),'nodes':len(v['nodes']),'edges':len(v['edges'])}))

if __name__=='__main__': main()
