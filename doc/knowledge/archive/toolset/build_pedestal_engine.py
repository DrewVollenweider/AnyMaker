"""Generate a separately named petrol engine test stand from native saved geometry."""
import archive_paths as ap
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import anymaker as a

NAME = 'Petrol_Pedestal_Test_01'
FOLDER = 'pedestal-engine-test-01'
SOURCE = ap.creation('Pedestal_Inline4_v3.data')
CATALOG = {'definitions': list(a.definitions().values())}


def build():
    source_hash = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    original = a.load(SOURCE)
    doc = deepcopy(original)
    refs = a.references(doc)
    v = a.vehicles(doc)[0]
    assert len(a.vehicles(doc)) == 1 and len(v['grids']) == 1
    assert not v['grids'][0].get('origin') and not v['grids'][0].get('dir')
    remove = {3, 4, 5, 47, 48, 49, 50, 54, 55, 56, 57, 58,
              60, 61, 62, 63, 64, 65, 66, 79}
    v['grids'][0]['components'] = [c for c in a.components(v) if c['id'] not in remove]
    by_id = {c['id']: c for c in a.components(v)}
    # Preserve engine/manifold/mounting geometry; replace only panel controls.
    for ident, definition, alias in ((51, 'switch', 'RUN'),
                                      (53, 'button_push_round', 'START')):
        if definition not in refs:
            refs.append(definition)
        c = by_id[ident]
        for key in list(c):
            if key not in ('id', 'pos', 'rot', 'colors'):
                del c[key]
        c.update({'def': refs.index(definition), 'user_defined_alias': alias})
    by_id[51]['value'] = False  # Observed native switch uses boolean value.
    by_id[52].update(user_defined_alias='THROTTLE', value=0.15)
    by_id[59]['user_defined_alias'] = 'Run_Throttle_Gate'
    by_id[1].update(rps=0.0, temperature=20.0, damage_factor=0.0,
                    content_lubricant={'oil': 0.75, 'temp': 20.0},
                    content_coolant={'water': 1.0, 'temp': 20.0})
    by_id[6].update(target_rps=30.0, power_factor=1.0, is_reverse=False)
    for ident in (8, 9):
        liquid = 'oil' if ident == 8 else 'water'
        by_id[ident].update(is_reverse=False,
                            content_0={liquid: 0.1, 'temp': 20.0},
                            content_1={liquid: 0.1, 'temp': 20.0})
    # Match engine wheel and starter pulley orientation for positive pump drive.
    # Crank rotation and pump delivery still require the requested in-game test.
    for ident in (2, 10, 11, 12, 13):
        by_id[ident]['reverse'] = True
    by_id[26]['content'] = {'oil': 8.0, 'temp': 20.0}
    by_id[32].update(content_0={'oil': 0.1, 'temp': 20.0},
                     content_1={'oil': 0.1, 'temp': 20.0})
    by_id[32]['acc']['item']['condition'] = 1.0
    by_id[35]['content'] = {'water': 7.5, 'temp': 20.0}
    by_id[42]['content'] = {'petrol': 8.0, 'temp': 20.0}
    by_id[15]['liquid'] = {'petrol': 0.05, 'temp': 20.0}
    for ident in (14, 24, 25, 46):
        # Remove stale gas temperature (including a saved null) and let the
        # game initialize ambient intake/exhaust state for the fresh test.
        by_id[ident].pop('gas', None)
    by_id[67]['acc']['item']['energy'] = 14400000.0  # Documented 4 kWh.
    by_id[71]['is_on'] = False
    by_id[72]['is_on'] = False
    for family in a.LINKS:
        v[family] = [link for link in v.get(family, [])
                     if link['p0']['comp'] not in remove and link['p1']['comp'] not in remove]

    def link(c0, n0, c1, n1, points, color):
        return {'p0': dict(comp=c0, **({'pos': n0} if n0 else {})),
                'p1': dict(comp=c1, **({'pos': n1} if n1 else {})),
                'points': points, 'color': color}

    v['mechanical_links'] = [
        link(51, 0, 59, 1, [[-3, 8, -12], [5, 8, -12]], 73),
        link(52, 0, 59, 0, [[-1, 8, -13], [5, 8, -13]], 71),
        link(59, 2, 14, 0, [[3, 6, -10], [3, 19, 4]], 71),
        link(51, 0, 72, 0, [[-3, 8, -14], [8, 8, -14], [8, 14, -4]], 73),
        link(53, 0, 71, 0, [[3, 8, -14], [6, 8, -14], [6, 14, -4]], 74),
    ]
    # Engine manifold draws petrol itself: retain the observed tank port 81.
    v['liquid_links'].append(link(81, 0, 15, 0,
                                  [[10, 10, 0], [10, 18, 0], [10, 18, 3]], 34))
    v['transform'] = {'m': a.IDENTITY[:], 't': [0, 0, 0]}
    # Drop unused catalog entries while retaining native index references.
    used = sorted({c['def'] for c in a.components(v)})
    mapping = {old: new for new, old in enumerate(used)}
    doc['definitions']['components'] = [refs[index] for index in used]
    for c in a.components(v):
        c['def'] = mapping[c['def']]

    catalog = {d['id']: d for d in CATALOG['definitions']}
    check = a.audit(doc, catalog)
    if check['issues']:
        raise ValueError('Resolve every static audit issue before delivery: ' + json.dumps(check['issues']))
    assert len(check['vehicles'][0]['frame_groups']) == 1
    assert not any(catalog[doc['definitions']['components'][c['def']]]['id'] == 'microcontroller'
                   for c in a.components(v))
    assert len(v['mechanical_links']) == 5 and len(v['belt_links']) == 5
    assert len(v['liquid_links']) == 8
    assert all(c.get('damage_factor', 0) == 0 for c in a.components(v))
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == source_hash
    meta = a.load(SOURCE.with_suffix('.meta'))
    meta['vehicles']['vehicles'][0]['transform'] = deepcopy(v['transform'])
    # Geometry only shrinks. Original native bounds contain the new build.
    report = {
        'name': NAME, 'source': str(SOURCE), 'source_sha256': source_hash,
        'source_unchanged': True, 'components': len(a.components(v)),
        'removed_component_ids': sorted(remove),
        'structural_audit': check,
        'systems': {
            'fuel': 'Tank 42 / port 81 -> fuel manifold 15; self-drawn by engine.',
            'air': 'Filter 24 with fitted item -> large air manifold 14.',
            'exhaust': 'Four exhaust manifolds 20–23 -> vent 25.',
            'oil': 'Tank 26 / pickup 28 -> pump inlet port 30 -> pump outlet port 31 -> filter 32 ports 33/34 -> manifold 16 -> engine -> manifold 17 -> return port 29 -> tank.',
            'coolant': 'Engine outlet manifold 19 -> radiator inlet port 38 -> radiator 35 -> outlet port 39 -> pump inlet port 40 -> pump outlet port 41 -> engine inlet manifold 18.',
            'starter': 'Battery 67 / port 69 -> relay 71 ports 73/74 -> starter port 77 -> motor 6 -> pulley 10 -> belt -> engine wheel 2.',
            'charging': 'Alternator 7 / port 78 -> battery port 68.',
            'fan': 'Battery port 70 -> relay 72 ports 75/76 -> fan port 80 -> radiator fan 36.',
            'run': 'Switch 51 -> gate 59 input 1 and fan relay 72. Slider 52 -> gate input 0. min output 2 -> intake throttle 14.',
            'start': 'Momentary button 53 -> starter relay 71.',
        },
        'initial_state': 'RUN off, START released, throttle 0.15; no saved rotation/damage.',
        'fluids': {'petrol_L': 8.05, 'oil_L': 9.15, 'water_L': 8.7},
        'pump_order': 'Pump 8 ports 30 then 31; pump 9 ports 40 then 41 retained in source component order.',
        'belt_signs': 'Engine wheel, starter pulley and accessory pulleys all reverse=true; positive accessory drive is a deduction from matching reversal settings.',
        'limits': ['Not game-tested in this session.',
                   'Saved/template geometry and static audits do not establish runtime mounting or circulation.',
                   'Engine oil/coolant inlet roles are inherited from the template and must be checked during testing.',
                   'No output load, gearbox or instrumentation is added.'],
    }
    readme = '''# Petrol Pedestal Test 01

Small inline-four petrol engine on a pedestal, with a belt starter, alternator,
oil/filter circuit, radiator/coolant pump, 8 L petrol supply and charged battery.
One physical body; no microcontroller or gearbox.

Controls on the front shelf (Properties Tool aliases):
- Left: RUN. Tap once to enable intake throttle and the radiator fan.
- Middle: THROTTLE. Starts at 15%; hold either end to adjust.
- Right: START. Hold to crank, then release when the engine continues running.
  The documented engine starting threshold is 6 rps. RUN must be on for combustion.
- Tap RUN off to shut the intake throttle and stop the engine.

First test: spawn upright on flat ground, find these controls, turn RUN on and
hold START. Release START once it catches. Start with the preset throttle;
increase only if it will not sustain running. Check that the accessory belt and
both pumps turn, and inspect engine temperature and lubricant/coolant quantities.
If quantities rapidly disappear, stop and report the affected circuit so its
flow direction or manifold role can be corrected. Turn RUN off after the test.

The structural audit has no errors or warnings. Functionality has not been
tested in-game in this session. The preview is a schematic, not a game screenshot.
Original creations remain unchanged; this is a separately named test revision.
'''
    for filename in (NAME + '.data', NAME + '.meta', NAME + '.png', 'validation.json',
                     'README.md', 'changes.json', 'schematic.html'):
        a.destination(FOLDER + '/' + filename)
    a.save(FOLDER + '/' + NAME + '.data', json.dumps(doc, separators=(',', ':'), allow_nan=False))
    a.save(FOLDER + '/' + NAME + '.meta', json.dumps(meta, separators=(',', ':'), allow_nan=False))
    a.save(FOLDER + '/validation.json', report)
    a.save(FOLDER + '/README.md', readme)
    a.save(FOLDER + '/changes.json', a.differences(original, doc))
    a.save(FOLDER + '/schematic.html', a.schematic(doc))
    thumbnail(doc)
    print(json.dumps({'name': NAME, 'components': report['components'],
                      'audit': check['counts'], 'folder': str(a.OUTPUT / FOLDER)}, indent=2))


def thumbnail(doc):
    from PIL import Image, ImageDraw, ImageFont
    image = Image.new('RGB', (1200, 900), '#edf1f4')
    draw = ImageDraw.Draw(image)
    font_path = Path('C:/Windows/Fonts/arial.ttf')
    title = ImageFont.truetype(str(font_path), 38)
    label = ImageFont.truetype(str(font_path), 22)
    small = ImageFont.truetype(str(font_path), 18)
    draw.text((38, 28), 'PETROL PEDESTAL TEST 01', fill='#1e2938', font=title)
    draw.text((40, 82), 'Inline-four engine | RUN / START / THROTTLE', fill='#536277', font=label)
    v = a.vehicles(doc)[0]
    nodes = {n['id']: n['pos'] for n in v['nodes']}
    def xy(p):
        x, y, z = p
        return (600 + (x - z) * 17, 650 - y * 20 + (x + z) * 7)
    for edge in sorted(v['edges'], key=lambda e: sum(nodes[e['n0']][::2])):
        draw.line([xy(nodes[edge['n0']]), xy(nodes[edge['n1']])], fill='#718392', width=4)
    for plate in v['plates']:
        draw.polygon([xy(nodes[n]) for n in plate['nodes']], fill='#ccd4db', outline='#637584')
    by_id = {c['id']: c for c in a.components(v)}
    boxes = [(42, [0,0,0], [3,2,3], '#b89450'),
             (26, [0,0,0], [1,1,5], '#665a76'),
             (67, [0,0,0], [1,1,1], '#293440'),
             (1, [-1,-1,0], [1,4,7], '#c86b3a'),
             (35, [-1,0,0], [3,4,0], '#55849c')]
    for ident, low, high, color in boxes:
        pos = by_id[ident]['pos']
        def p(x,y,z): return xy([pos[0]+x, pos[1]+y, pos[2]+z])
        x0,y0,z0 = low; x1,y1,z1 = high
        for face in ([p(x0,y0,z1),p(x1,y0,z1),p(x1,y1,z1),p(x0,y1,z1)],
                     [p(x1,y0,z0),p(x1,y0,z1),p(x1,y1,z1),p(x1,y1,z0)],
                     [p(x0,y1,z0),p(x1,y1,z0),p(x1,y1,z1),p(x0,y1,z1)]):
            draw.polygon(face, fill=color, outline='#243746', width=2)
    for ident in (2,10,11,12,13):
        x,y = xy(by_id[ident]['pos'])
        radius = 18 if ident==2 else 8
        draw.ellipse((x-radius,y-radius,x+radius,y+radius), fill='#d8dfe5', outline='#172b38', width=3)
    for link in v['belt_links']:
        draw.line([xy(by_id[link[end]['comp']]['pos']) for end in ('p0','p1')], fill='#273744', width=3)
    for ident, text, at in [(1,'PETROL ENGINE',(60,180)),
                           (35,'RADIATOR + FAN',(60,270)),
                           (42,'8 L PETROL',(925,340)),
                           (67,'STARTER BATTERY',(925,445)),
                           (51,'RUN',(925,580)),
                           (52,'THROTTLE',(925,625)),
                           (53,'START',(925,670))]:
        target = xy(by_id[ident]['pos'])
        draw.line([target, (at[0]-10 if at[0]>600 else at[0]+220,at[1]+12)], fill='#8796a4', width=2)
        draw.text(at, text, font=small, fill='#1e2938')
    draw.text((40, 825), 'Schematic preview — in-game testing required', fill='#536277', font=label)
    path = a.destination(FOLDER + '/' + NAME + '.png')
    with path.open('xb') as stream:
        image.save(stream, format='PNG')


if __name__ == '__main__':
    build()
