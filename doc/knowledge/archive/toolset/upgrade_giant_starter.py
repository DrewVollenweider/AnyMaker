"""Build a native geared starter revision from the user's latest creation."""
import archive_paths as ap
from copy import deepcopy
from datetime import datetime
import hashlib
from itertools import product
import json
from pathlib import Path
import anymaker as a

source = ap.creation('giantenginetest.data')
out = a.OUTPUT / 'giant-engine-starter-02' / datetime.now().strftime('%Y%m%d-%H%M%S')
out.mkdir()
raw, meta_raw = source.read_bytes(), source.with_suffix('.meta').read_bytes()
before = a.load(source)
assert before == json.loads(raw.decode('utf-8-sig'))
assert raw == source.read_bytes()
(out / 'giantenginetest.before.data').write_bytes(raw)
(out / 'giantenginetest.before.meta').write_bytes(meta_raw)
after, meta = deepcopy(before), json.loads(meta_raw.decode('utf-8-sig'))
assert len(a.vehicles(after)) == 1
v = a.vehicles(after)[0]
assert len(v['grids']) == 1 and not v['grids'][0].get('pos')
grid = v['grids'][0]
cs = {c['id']: c for c in a.components(v)}
refs = a.references(after)
assert refs[cs[1]['def']] == 'opposed_engine_c'
assert refs[cs[103]['def']] == 'engine_wheel_c'
assert cs[62]['pos'] == [61, 20, 131] and cs[64]['pos'] == [61, 20, 129]
assert cs[62].get('is_reverse', False) is False
cat = a.definitions()
rotation = [-1, 0, 0, 0, 1, 0, 0, 0, -1]

def ref(name):
    if name not in refs:
        refs.append(name)
    return refs.index(name)

# Retain the working shaft direction. The new gearbox sits behind its relocated
# belt pulley, with an offset input shaft and directly fitted motor.
cs[62]['def'] = ref('electric_motor_b')
cs[62]['pos'] = [59, 24, 132]
cs[62]['user_defined_alias'] = '60kW Starter'
cs[64]['pos'] = [61, 24, 129]
cs[77]['pos'] = [59, 24, 134]
gear_id = max(cs) + 1
gear = {'def': ref('gearbox_fixed_ratio'), 'id': gear_id,
        'colors': deepcopy(cs[62]['colors']), 'pos': [60, 24, 130], 'rot': rotation,
        'input': 1, 'output': 3, 'reverse': True,
        'user_defined_alias': 'Starter 3x Speed'}
grid['components'].append(gear)
cs[gear_id] = gear

for link in v['electric_links']:
    if link['p0']['comp'] == 77:
        assert link['p1']['comp'] == 81
        link['points'] = [[59,24,135], [57,24,135], [57,22,133],
                          [62,22,133], [62,20,133], [62,20,147]]

# Join the support to both existing radiator-frame uprights. All new bars stay
# behind the belt plane and below the starter bodies.
nodes = {n['id']: n for n in v['nodes']}
assert nodes[11]['pos'] == [53,19,129] and nodes[9]['pos'] == [69,19,129]
node_id = max(nodes)
new_nodes = []
for pos in ([53,23,129], [69,23,129], [53,23,132], [69,23,132],
            [60,23,132], [60,23,130]):
    node_id += 1
    new_nodes.append({'id': node_id, 'pos': list(pos)})
v['nodes'].extend(new_nodes)
n0,n1,n2,n3,n4,n5 = [n['id'] for n in new_nodes]
new_edges = [{'n0':x,'n1':y} for x,y in
             [(11,n0),(9,n1),(n0,n2),(n1,n3),(n2,n4),(n4,n3),(n4,n5)]]
v['edges'].extend(new_edges)

# Load stopped; measured speed is not a design setting.
cs[1]['rps'] = 0.0
cs[79]['is_on'] = False
cs[83]['value'] = 0.0

def transform(c, p):
    r = c.get('rot', a.IDENTITY)
    origin = c.get('pos', [0,0,0])
    return tuple(origin[i] + sum(r[j*3+i] * p[j] for j in range(3)) for i in range(3))

def physical_voxels(c):
    d = cat[refs[c['def']]]
    center = d.get('center_stretch', [.5,.5,.5])
    ext = c.get('ext', [0,0,0])
    result = set()
    for z in d.get('zones', []):
        if z.get('is_physics', True) is False:
            continue
        lo, hi = z.get('bounds_min', [0,0,0]), z.get('bounds_max', [0,0,0])
        lo = [lo[i] + (ext[i] if lo[i] > center[i] else 0) for i in range(3)]
        hi = [hi[i] + (ext[i] if hi[i] > center[i] else 0) for i in range(3)]
        result.update(transform(c, p) for p in product(*(range(lo[i],hi[i]+1) for i in range(3))))
    return result

occupied = {i: physical_voxels(c) for i,c in cs.items()}
changed_bodies = [62,77,gear_id]
collisions = []
for i in changed_bodies:
    for j in cs:
        if i == j:
            continue
        overlap = occupied[i] & occupied[j]
        if overlap:
            collisions.append({'components':[i,j], 'voxels':sorted(overlap)})
assert not collisions, collisions

# Check opposed, coincident torque faces using actual component definitions.
dirs = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
def face(c, face_id):
    surface = next(s for s in cat[refs[c['def']]]['surfaces'] if s.get('id') == face_id)
    p = surface.get('pos', [0,0,0]); normal = dirs[surface.get('dir', 0)]
    origin = transform(c, [0,0,0])
    wn = tuple(transform(c, normal)[i] - origin[i] for i in range(3))
    wp = transform(c, p)
    return tuple(wp[i] + wn[i]*.5 for i in range(3)), wn, surface['type']

mates = []
for x,xf,y,yf in [(62,'torque',gear_id,'torque_0'), (gear_id,'torque_1',64,'torque')]:
    p,n,t = face(cs[x],xf); q,m,u = face(cs[y],yf)
    assert p == q and n == tuple(-a for a in m) and t == u == 'torque', (x,p,n,y,q,m)
    mates.append({'a':[x,xf], 'b':[y,yf], 'face_center':p})

all_nodes = {n['id']:n['pos'] for n in v['nodes']}
for edge in new_edges:
    p,q = all_nodes[edge['n0']], all_nodes[edge['n1']]
    delta = [q[i]-p[i] for i in range(3)]
    assert sum(x!=0 for x in delta) == 1
    length = max(abs(x) for x in delta)
    for step in range(1,length):
        voxel = tuple(p[i] + delta[i]*step//length for i in range(3))
        assert not any(voxel in vox for vox in occupied.values()), ('frame intersects component',voxel)

audit = a.audit(after,cat)
assert not any(i['severity']=='error' for i in audit['issues']), audit['issues']
# This support/motor revision only increases the upper Y extent.
mv = meta['vehicles']['vehicles'][0]
assert mv['id'] == v['id']
mv['bounds']['max'][1] = max(mv['bounds']['max'][1], 25.5*.08)

for suffix,doc in [('data',after),('meta',meta)]:
    target = out / ('giantenginetest.' + suffix)
    target.write_text(json.dumps(doc,separators=(',',':'),ensure_ascii=False,allow_nan=False),encoding='utf-8')
    assert a.load(target) == doc
hashes = {f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}
report = {'source':str(source), 'hashes':hashes, 'starter_kw':60,
          'motor_rps':30, 'speed_increase':3, 'nominal_engine_rps':30*3/6.7,
          'torque_mates':mates,'new_component_collision_checks':collisions,
          'changes':a.differences(before,after), 'audit':audit,
          'notes':['User save confirms 3.024138 engine rps with the old 10kW direct belt starter.',
                   'Native ratio serialization and torque propagation statically inspected.',
                   'Gear link output/input = 3/1. Reverse=true preserves the original belt direction across the added opposed-face connections.',
                   'All saved fluids, damage, battery energy, engine/fuel/pump geometry and belt links preserved.',
                   'Starter is stopped on load. Hold existing key switch to crank.',
                   'Calculated nominal speed is not an in-game test result.']}
(out/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'output_directory':str(out),'hashes':hashes,'torque_mates':mates,
                  'nominal_engine_rps':report['nominal_engine_rps'],
                  'audit_issues':audit['issues']},indent=2))
