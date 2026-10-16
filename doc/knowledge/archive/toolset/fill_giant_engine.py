"""Prepare a fluid-only refill from the latest user save; never install it here."""
import archive_paths as ap
from copy import deepcopy
from datetime import datetime
import hashlib
import json
from pathlib import Path
import anymaker as a

source = ap.creation('giantenginetest.data')
stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
out = a.OUTPUT / 'giant-engine-diagnosis' / ('refill-' + stamp)
out.mkdir()
raw = source.read_bytes()
before = a.load(source)
assert raw == source.read_bytes(), 'Source changed during snapshot'
assert json.loads(raw.decode('utf-8-sig')) == before
(out / 'giantenginetest.before.data').write_bytes(raw)
meta = source.with_suffix('.meta').read_bytes()
(out / 'giantenginetest.before.meta').write_bytes(meta)
after = deepcopy(before)
components = {c['id']: c for v in a.vehicles(after) for c in a.components(v)}
assert a.references(after)[components[1]['def']] == 'opposed_engine_c'
assert components[1].get('ext') == [0, 0, 20]
assert components[42]['ext'] == [9, 1, 8]
assert components[43]['ext'] == [9, 4, 10]
assert components[14]['ext'] == [9, 9, 0]

def top_up(content, liquid, capacity):
    # Retain existing contaminants, temperature and any naturally overshot volume.
    occupied = sum(content.get(k, 0) for k in ('water', 'petrol', 'oil', 'pollutant') if k != liquid)
    content[liquid] = max(content.get(liquid, 0), capacity - occupied)

# Native tank/radiator capacity: stretched inspection-box voxels * 0.5 L.
top_up(components[43]['content'], 'petrol', 11 * 6 * 12 * .5)
top_up(components[42]['content'], 'oil', 11 * 3 * 10 * .5)
top_up(components[14]['content'], 'water', 15 * 11 * 2 * .5)
# Static engine.create passes 0.24 to both volume constructors. The selected
# inspection boxes span 7 * 1 * 26 voxels after stretching; g_litres_per_voxel=.5.
engine_capacity = 7 * 1 * 26 * .24 * .5
top_up(components[1]['content_lubricant'], 'oil', engine_capacity)
top_up(components[1]['content_coolant'], 'water', engine_capacity)

changes = a.differences(before, after)
assert changes
assert all(x['path'].endswith(('/content/petrol', '/content/oil', '/content/water',
                              '/content_lubricant/oil', '/content_coolant/water')) for x in changes)
catalog = a.definitions()
old_audit, new_audit = a.audit(before, catalog), a.audit(after, catalog)
assert old_audit['issues'] == new_audit['issues']
assert not any(i['severity'] == 'error' for i in new_audit['issues'])
target = out / 'giantenginetest.data'
target.write_text(json.dumps(after, separators=(',', ':'), ensure_ascii=False, allow_nan=False), encoding='utf-8')
assert a.load(target) == after
report = {
    'source': str(source), 'source_sha256': hashlib.sha256(raw).hexdigest(),
    'meta_sha256': hashlib.sha256(meta).hexdigest(),
    'output_sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
    'engine_chamber_nominal_capacity_l': engine_capacity,
    'changes': changes, 'audit': new_audit,
    'notes': [
        'Fluid-only refill. Wheel, motor direction, pump directions, links, damage and geometry unchanged.',
        'Latest save has medium engine wheel torque_engine_b on opposed_engine_c torque_engine_c.',
        'Both latest fuel manifolds and both fuel pump chambers contain no petrol.',
        'Motor direction was reversed; oil/coolant pump reverse flags changed, fuel flags did not.',
        'Engine coolant already exceeds nominal capacity slightly; existing amount preserved.',
        'No in-game test performed.'
    ]
}
(out / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({'output': str(target), 'report': str(out / 'report.json'),
                  'source_sha256': report['source_sha256'], 'meta_sha256': report['meta_sha256'],
                  'output_sha256': report['output_sha256'], 'changes': changes}, indent=2))
