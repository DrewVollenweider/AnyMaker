"""Correct gas ordinal -> saved logic-index conversion after the failed test."""
import archive_paths as ap
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import hashlib,json,math,struct
import anymaker as a
import structural_mounts as sm

NAME='Giant_Engine_Test_Vehicle_01'
SOURCE=ap.creation('')/(NAME+'.data')
ROOT=a.OUTPUT/'shift-repair';OUT=ROOT/datetime.now().strftime('%Y%m%d-%H%M%S');OUT.mkdir()
raw=SOURCE.read_bytes();doc=a.load(SOURCE);before=deepcopy(doc);assert json.loads(raw)==doc
(OUT/'before.data').write_bytes(raw)
for ext in ['meta','png']:(OUT/('before.'+ext)).write_bytes(SOURCE.with_suffix('.'+ext).read_bytes())
v=a.vehicles(doc)[0];refs=a.references(doc);cs={c['id']:c for c in a.components(v)}
cat=a.definitions()
assert len(cs)==101
# The constructor passes gas ordinals; gas-node-create converts them using
# definition.get_logic_node_index(type=gas, ordinal). Save links use that result.
b=(ROOT/'valve-create.bin').read_bytes()
ordinals=[struct.unpack_from('<i',b,p)[0] for p in [0x200,0x210,0x214]]
assert ordinals==[0,1,2]
gas_indices=[i for i,n in enumerate(cat['gas_valve_t']['logic_nodes']) if n.get('type')=='gas']
common,active,rest=[gas_indices[o] for o in ordinals]
assert [common,active,rest]==[1,2,3]
changes=[]
for l in v['gas_links']:
    for end in ['p0','p1']:
        e=l[end]
        if e['comp'] not in [130,131]:continue
        other=l['p1' if end=='p0' else 'p0']['comp']
        target=active if other==129 else rest if other in [132,133] else common if other in [125,126] else None
        assert target is not None
        changes.append({'valve':e['comp'],'other':other,'before':e.get('pos',0),'after':target});e['pos']=target
# Actual capsule volumes from gas_content.create, not its scale argument alone.
def capsule(definition,layer,scale):
    g=next(g for g in cat[definition]['inspection_geometry'] if g.get('layer',0)==layer and g.get('shape')==1)
    r=g['radius']/.08;length=math.dist(g.get('p0',[0,0,0]),g.get('p1',[0,0,0]))
    return (math.pi*r*r*length+4/3*math.pi*r**3)*.512*scale
chamber=capsule('gearbox_c',2,.1);tank=capsule('gas_tank_a',0,1)
for field in ['content_shift_up','content_shift_down']:
    cs[108][field]={'air':chamber*.998,'exhaust':chamber*.002,'temp':20.0}
cs[108].update(current=0,target=0,clutch=1.0,shift_up_triggered=False,shift_down_triggered=False)
cs[127]['content']={'air':79.84,'exhaust':.16,'temp':20.0}
for i in [130,131]:cs[i]['is_output_left']=False

def states(selected):
    graph={}
    def join(x,y):graph.setdefault(x,set()).add(y);graph.setdefault(y,set()).add(x)
    for l in v['gas_links']:
        if min(l['p0']['comp'],l['p1']['comp'])<125:continue
        join((l['p0']['comp'],l['p0'].get('pos',0)),(l['p1']['comp'],l['p1'].get('pos',0)))
    for n in [1,2]:join((129,0),(129,n))
    for valve in [130,131]:join((valve,common),(valve,active if selected==valve else rest))
    def flood(port):
        seen={(port,0)};queue=list(seen)
        while queue:
            for x in graph.get(queue.pop(),set())-seen:seen.add(x);queue.append(x)
        return seen
    result=[]
    for valve,port,vent in [(130,125,132),(131,126,133)]:
        seen=flood(port);supplied=(128,0) in seen;vented=(vent,0) in seen
        assert supplied==(selected==valve) and vented==(selected!=valve)
        result.append({'port':port,'supplied':supplied,'vented':vented})
    return result
truth=[{'active_valve':selected,'circuits':states(selected)} for selected in [None,130,131]]
audit=a.audit(doc,cat);assert not any(i['severity']=='error' for i in audit['issues']),audit['issues']
physical=sm.audit(doc,cat);assert len(physical['islands'])==1
oldcs={c['id']:c for c in a.components(a.vehicles(before)[0])}
assert all(c==cs[i] for i,c in oldcs.items() if i not in [108,127,130,131])
assert SOURCE.read_bytes()==raw
for ext,obj in [('data',doc),('meta',a.load(SOURCE.with_suffix('.meta')))]:
    (OUT/(NAME+'.'+ext)).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf-8')
(OUT/(NAME+'.png')).write_bytes(SOURCE.with_suffix('.png').read_bytes())
report={'before_sha256':hashlib.sha256(raw).hexdigest(),'saved_valve_nodes':{'common':common,'active':active,'rest':rest},
        'endpoint_changes':changes,'native_capsule_capacity':{'gearbox_chamber':chamber,'tank':tank},
        'original_failed_chamber_pressure':(1.2346293937706678+.002474207201945227)/chamber,
        'trigger_pressure':3,'reset_pressure':2,'tank_charge':80,'initial_tank_pressure':80/tank,
        'truth_table':truth,'audit':audit,'physical_audit':physical,
        'validation':'Native ordinal conversion and valve flooding traced; revised runtime test pending.'}
(OUT/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
(OUT/'hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob(NAME+'.*')},indent=2))
print(json.dumps({'output':str(OUT),'mapping':[common,active,rest],'chamber_capacity':chamber,'tank_capacity':tank,'truth_table':truth},indent=2))
