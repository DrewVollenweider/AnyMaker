"""Remove temporary trace hardware after live shifting acceptance."""
import archive_paths as ap
from pathlib import Path
from datetime import datetime
import json,math,hashlib
import anymaker as a
import structural_mounts as sm

NAME='Giant_Engine_Test_Vehicle_01'
SOURCE=ap.creation('')/(NAME+'.data')
OUT=a.OUTPUT/'shift-repair'/datetime.now().strftime('%Y%m%d-%H%M%S');OUT.mkdir()
raw=SOURCE.read_bytes();doc=a.load(SOURCE);v=a.vehicles(doc)[0];cs={c['id']:c for c in a.components(v)}
assert len(cs)==106
flags={x['name']:x['data_value'].get('data_value',False) for x in cs[134]['global_private']}
assert flags['SawGear'] and flags['SawUpValve'] and flags['SawDownValve'] and not flags['SawBothValves'],flags
(OUT/'before.data').write_bytes(raw)
for ext in ['meta','png']:(OUT/('before.'+ext)).write_bytes(SOURCE.with_suffix('.'+ext).read_bytes())
removed={140,141,142}
for g in v['grids']:g['components']=[c for c in g['components'] if c['id'] not in removed]
v['data_links']=[l for l in v['data_links'] if not {l['p0']['comp'],l['p1']['comp']}&removed]
cs[134]['script']='''on_tick
{
    in Gear.display_value = to_fractional (out DriveGearbox.current_gear)
    in Gear.is_illuminated = true
    in Reverse.is_illuminated = out DriveGearbox.current_gear < 0
}
'''
cs[134]['global_private']=[]
# A fresh test spawn starts parked and neutral, with the finite air tank charged.
cs[108].update(current=0,target=0,clutch=1.0,shift_up_triggered=False,shift_down_triggered=False)
cap=(math.pi*2+4/3*math.pi)*.512*.1
for key in ['content_shift_up','content_shift_down']:cs[108][key]={'air':cap*.998,'exhaust':cap*.002,'temp':20.0}
cs[127]['content']={'air':79.84,'exhaust':.16,'temp':20.0}
cs[121].update(is_on=True,value=1.0)
cat=a.definitions()
audit=a.audit(doc,cat);assert not any(x['severity']=='error' for x in audit['issues']),audit['issues']
physical=sm.audit(doc,cat);assert len(physical['islands'])==1
assert len(a.components(v))==103
assert SOURCE.read_bytes()==raw
for ext,obj in [('data',doc),('meta',a.load(SOURCE.with_suffix('.meta')))]:
    (OUT/(NAME+'.'+ext)).write_text(json.dumps(obj,separators=(',',':'),allow_nan=False),encoding='utf-8')
(OUT/(NAME+'.png')).write_bytes(SOURCE.with_suffix('.png').read_bytes())
(OUT/'report.json').write_text(json.dumps({'before_sha256':hashlib.sha256(raw).hexdigest(),'live_trace':flags,'removed_diagnostic_ports':sorted(removed),'parts':103,'audit':audit,'physical_audit':physical,'status':'User verified gears 1 and 2 and reverse indicator; diagnostic trace records engagement with no simultaneous valve activation.'},indent=2))
(OUT/'CONTROL-GUIDE.md').write_text('''Giant Engine Test Vehicle 01

The creation starts with the handbrake ON and the gearbox in neutral.
Start the engine, tap 3 to shift up to first, then press 1 to RELEASE THE HANDBRAKE.
Right pedal/W applies throttle. Left pedal/S brakes and disconnects the rear axle.
3 shifts up; 2 shifts down. Release each shift key between changes.
Display 0 = neutral, 1/2 = forward gears. Red lamp = reverse.
Press 1 again to park. The handbrake locks the wheels and disconnects the drive.
Shift air is precharged and finite.
''',encoding='utf-8')
print(json.dumps({'output':str(OUT),'parts':103,'live_trace':flags},indent=2))
