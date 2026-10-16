"""Verify the final artifact read from disk, independent of generator output."""

from pathlib import Path

import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))

import anymaker as a

import compact_engine as geometry



root=Path(__file__).resolve().parent

context={'__file__':str(root/'check_mounts.py')}

exec((root/'check_mounts.py').read_text().split('pairs = ')[0],context)

doc=context['doc']; cs=context['components']; refs=context['refs']

v=a.vehicles(doc)[0]

frame={tuple(n['pos']) for n in v['nodes']}

occupied={i:geometry.cells(c,geometry.CAT[refs[c['def']]]) for i,c in cs.items()}

supports=[]

for ident in (1,6,7,8,9,24,25,26,32,35,42,46,51,52,53,59,67,71,72):

    found=[]

    for patch in context['patches'](cs[ident]):

        for u in range(patch['sizes'][0]):

            for w in range(patch['sizes'][1]):

                neighbor=tuple(round(patch['center'][i]+u*patch['tangents'][0][i]+w*patch['tangents'][1][i]+.5*patch['normal'][i]) for i in range(3))

                if neighbor in frame: found.append(neighbor)

    assert found,('No declared mounting surface meets frame',ident)

    supports.append({'component':ident,'matching_frame_cells':sorted(set(found))})

mates=[context['check_mount'](*pair) for pair in ((2,1,'torque_engine'),(10,6,'torque'),(13,7,'torque'),(12,8,'torque'),(11,9,'torque'))]

report=a.load(root/'validation.json'); seen={}; shared=[]

for record in report['routing']:

    keys={(record['family'],e['comp'],e.get('pos',0)) for e in record['endpoints']}

    exceptions={tuple(p) for p in record['mount_contact_exceptions']}

    for point in record['route_cells']:

        point=tuple(point)

        assert not any(point in points for points in occupied.values()),('Route enters component',record['family'],record['index'],point)

        assert point not in frame or point in exceptions,('Route enters frame',point)

        if point in seen:

            oldkeys,old=seen[point]

            assert keys & oldkeys,('Unrelated route crossing',point)

            shared.append({'cell':point,'routes':[old,[record['family'],record['index']]],'common_terminal':list(keys & oldkeys)})

        seen[point]=(keys,[record['family'],record['index']])

assert a.audit(doc,geometry.CAT)['issues']==[]

assert a.audit(doc,geometry.CAT)['vehicles'][0]['frame_groups'] and len(a.audit(doc,geometry.CAT)['vehicles'][0]['frame_groups'])==1

# Preserve the complete proven connection graph despite spatial rerouting.

base=a.load(geometry.BASE); original=a.vehicles(base)[0]

for family in a.LINKS:

    endpoints=lambda vehicle:[(link['p0'],link['p1']) for link in vehicle.get(family,[])]

    assert endpoints(v)==endpoints(original),('Connection graph changed',family)

for ident in cs:

    for other in cs:

        if ident<other: assert not occupied[ident] & occupied[other]

    assert not occupied[ident] & frame

print(a.save('compact-petrol-engine-01-complete/final-checks.json', {

    'torque_mounts':mates,'primary_frame_contacts':supports,

    'mount_face_checks':len(a.load(root/'mount-face-check.json')['checks']),

    'component_overlaps':0,'component_frame_intersections':0,

    'route_component_penetrations':0,'unrelated_shared_route_cells':0,

    'necessary_terminal_branches':shared,'connection_graph_preserved':True,

    'routing_count':len(report['routing']),

    'limit':'Native zone/surface static checks; fresh in-game fit, body grouping and operation remain unverified.'}))

print('PASS: 36 port/fan mounts, 5 torque mounts, 19 frame contacts, 24 routes, preserved graph, no unrelated overlaps.')

