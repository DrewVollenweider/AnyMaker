"""Preserve user-exported running state and compare by component identity."""
import archive_paths as ap
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import anymaker as a

root = Path(__file__).resolve().parent
source = ap.creation('Petrol_Pedestal_Test_01.data')
base = a.load(root/'Petrol_Pedestal_Test_01.data')
current = a.load(source)
raw = source.read_bytes()
assert a.load(source) == current
hash_ = hashlib.sha256(raw).hexdigest()
target = a.destination('pedestal-engine-test-01/running-result/running.data')
target.parent.mkdir(parents=True, exist_ok=True)
with target.open('xb') as stream: stream.write(raw)
meta = source.with_suffix('.meta')
with a.destination('pedestal-engine-test-01/running-result/running.meta').open('xb') as stream:
    stream.write(meta.read_bytes())
image = Path(r'C:\Program Files (x86)\Steam\userdata\STEAM_ACCOUNT\760\remote\4435340\screenshots\20261014094038_1.jpg')
with a.destination('pedestal-engine-test-01/running-result/user-screenshot.jpg').open('xb') as stream:
    stream.write(image.read_bytes())

def by_id(doc):
    refs = a.references(doc)
    return {c['id']: dict(c, definition=refs[c['def']]) for v in a.vehicles(doc) for c in a.components(v)}

initial = by_id(base)
saved = by_id(current)
engine = saved[1]
v0 = a.vehicles(base)[0]
v1 = a.vehicles(current)[0]
geometry_fields = ('pos','rot','ext')
same_components = set(initial) == set(saved) and all(
    initial[i]['definition'] == saved[i]['definition'] and
    all(initial[i].get(k) == saved[i].get(k) for k in geometry_fields)
    for i in initial)
same_structure = all(v0.get(k) == v1.get(k) for k in ('nodes','edges','plates'))
same_links = all(v0.get(k) == v1.get(k) for k in a.LINKS)
report = {
    'captured_utc': datetime.now(timezone.utc).isoformat(),
    'source': str(source), 'source_sha256': hash_,
    'source_mtime_utc': datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
    'test_evidence': 'User reported success, supplied screenshot and exported the running creation.',
    'component_geometry_unchanged': same_components,
    'frame_geometry_unchanged': same_structure,
    'links_unchanged': same_links,
    'saved_vehicle_id': v1['id'], 'original_vehicle_id': v0['id'],
    'engine': {'rps':engine['rps'], 'rpm':engine['rps']*60,
               'temperature_C':engine['temperature'],
               'damage_factor':engine['damage_factor'],
               'damage_factor_times_100':engine['damage_factor']*100,
               'oil_L':engine['content_lubricant']['oil'],
               'water_L':engine['content_coolant']['water']},
    'controls': {'run':saved[51]['value'], 'throttle_slider':saved[52]['value'],
                 'run_relay_on':saved[72].get('is_on'),
                 'starter_relay_saved_fields':saved[71]},
    'petrol_remaining_L':saved[42]['content']['petrol'],
    'battery_energy_J':saved[67]['acc']['item']['energy'],
    'battery_fraction_of_4kWh':saved[67]['acc']['item']['energy']/14400000,
    'fluid_distribution': {str(i):{'definition':saved[i]['definition'],
                                     'state':{k:saved[i][k] for k in ('content','content_0','content_1','content_lubricant','content_coolant') if k in saved[i]}}
                           for i in (1,8,9,26,32,35,42)},
    'concern': 'Radiator 35 content has temperature only and no water field; oil reservoir 26 likewise has no oil field. Under the observed omission of zero-valued fluid quantities, this indicates empty stores. Fluid moved into engine/filter/pump chambers, but sustained closed-loop cooling is not demonstrated.',
    'screenshot_readings': {'speed_Hz':10.1, 'temperature_C':20.7, 'throttle_percent':15, 'power_kW':2.4,
                            'oil_L':3.4, 'coolant_L':3.4, 'oil_quality_percent':100},
    'limits': ['Screenshot and exported save represent different moments; saved throttle is now 100%.',
               'No measured run duration, time-series thermal test, loaded output test or alternator charging measurement.',
               'Nonzero damage cause is not established.',
               'Native re-export reordered definition indexes, remapped body/item IDs and omitted several defaults; identity comparison avoids false geometry changes.'],
    'audit': a.audit(current),
    'component_state_changes_by_id': {str(i):a.differences({k:v for k,v in initial[i].items() if k!='def'}, {k:v for k,v in saved[i].items() if k!='def'})
                                      for i in initial if initial[i] != saved[i]},
}
assert hashlib.sha256(source.read_bytes()).hexdigest() == hash_
assert same_components and same_structure and same_links
print(a.save('pedestal-engine-test-01/running-result/report.json',report))
print('RPM:',report['engine']['rpm'],'Temperature:',report['engine']['temperature_C'])
print('Component/frame/link geometry unchanged:',same_components,same_structure,same_links)
