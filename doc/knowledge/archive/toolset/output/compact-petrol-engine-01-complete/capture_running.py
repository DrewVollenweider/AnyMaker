"""Preserve the user-tested CPE1Running export; never write the creation folder."""
import archive_paths as ap
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import anymaker as a

root=Path(__file__).resolve().parent
source=ap.creation('cpe1running.data')
doc=a.load(source); initial=a.load(root/'Compact_Petrol_Engine_01.data')
manifest=[]
for extension in ('.data','.meta','.png'):
    path=source.with_suffix(extension); raw=path.read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    target=a.destination('compact-petrol-engine-01-complete/running-result/CPE1Running'+extension)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream: stream.write(raw)
    assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    manifest.append({'source':str(path),'copy':str(target),'sha256':digest})
assert a.load(source)==doc

def indexed(document):
    refs=a.references(document)
    return {c['id']:dict(c,definition=refs[c['def']]) for v in a.vehicles(document) for c in a.components(v)}
before=indexed(initial); after=indexed(doc)
v0=a.vehicles(initial)[0]; v1=a.vehicles(doc)[0]
component_geometry_unchanged=set(before)==set(after) and all(
    before[i].get(k)==after[i].get(k) for i in before for k in ('definition','pos','rot','ext'))
node_geometry=lambda v:{n['id']:n.get('pos',[0,0,0]) for n in v['nodes']}
frame_unchanged=node_geometry(v0)==node_geometry(v1) and v0['edges']==v1['edges'] and v0['plates']==v1['plates']
links_unchanged=all(v0.get(k)==v1.get(k) for k in a.LINKS)
engine=after[1]
meta=a.load(source.with_suffix('.meta'))
bounds=meta['vehicles']['vehicles'][0]['bounds']
report={'captured_utc':datetime.now(timezone.utc).isoformat(),
        'evidence':'User reports compact engine working; supplied CPE1Running native export and game-generated preview.',
        'copies':manifest,'body_count':len(a.vehicles(doc)),'components':len(after),
        'component_geometry_unchanged':component_geometry_unchanged,
        'frame_geometry_unchanged_with_omitted_origin_default':frame_unchanged,
        'links_unchanged':links_unchanged,
        'export_default_note':'Node 70 at [0,0,0] omits pos on re-export; normalize this default before comparing frame geometry.',
        'engine':{'rps':engine['rps'],'rpm':engine['rps']*60,
                  'temperature_C':engine['temperature'],'damage_factor':engine['damage_factor'],
                  'oil_L':engine['content_lubricant']['oil'],
                  'water_L':engine['content_coolant']['water']},
        'run_switch':after[51]['value'],'throttle':after[52]['value'],
        'run_relay_on':after[72]['is_on'],
        'petrol_tank_L':after[42]['content']['petrol'],
        'battery_energy_J':after[67]['acc']['item']['energy'],
        'battery_percent_of_initial':after[67]['acc']['item']['energy']/14400000*100,
        'game_saved_component_bounds_m_xyz':[round(bounds['max'][i]-bounds['min'][i],3) for i in range(3)],
        'conservative_full_routing_envelope_m_xyz':[1.36,.92,1.04],
        'fluid_distribution':{str(i):{k:after[i][k] for k in ('content','content_0','content_1','content_lubricant','content_coolant') if k in after[i]} for i in (1,8,9,26,32,35)},
        'coolant_accounted_for_L':engine['content_coolant']['water']+after[9]['content_0']['water']+after[9]['content_1']['water'],
        'audit':a.audit(doc),
        'limits':['One saved operating point, not measured run duration or loaded output performance.',
                  'Radiator and oil reservoir again contain temperature only; sustained circulation remains unresolved.',
                  'Component bounds in native meta are smaller than the full routed-line clearance envelope.',
                  'Damage factor is nonzero; cause not established.']}
assert component_geometry_unchanged and frame_unchanged and links_unchanged
print(a.save('compact-petrol-engine-01-complete/running-result/report.json',report))
print('Preserved compact engine running at',round(report['engine']['rpm']),'RPM;',round(report['engine']['temperature_C'],1),'C')
