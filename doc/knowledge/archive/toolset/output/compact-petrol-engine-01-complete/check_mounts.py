"""Static face checks for this specific template-derived test assembly."""

import sys

from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import anymaker as a



root = Path(__file__).resolve().parent

doc = a.load(root/'Compact_Petrol_Engine_01.data')

refs = a.references(doc)

catalog = {d['id']: d for d in a.load(a.HOME/'output/research-20261014/vehicle_component_definitions.json')['definitions']}

components = {c['id']: c for v in a.vehicles(doc) for c in a.components(v)}

normals = [[-1,0,0],[1,0,0],[0,-1,0],[0,1,0],[0,0,-1],[0,0,1]]



def rotate(c, p):

    r = c.get('rot', a.IDENTITY)

    return [sum(r[3*k+j]*p[k] for k in range(3)) for j in range(3)]



def world(c, p):

    return [x+y for x,y in zip(c.get('pos',[0,0,0]), rotate(c,p))]



def patches(c):

    d = catalog[refs[c['def']]]

    ext = c.get('ext',[0,0,0])

    for surface in d.get('surfaces',[]):

        s = dict(surface)

        n = normals[s.get('dir',0)]

        normal_axis = next(i for i,x in enumerate(n) if x)

        # Installed side rectangles use width along Z, height along Y;

        # top/bottom use X/Z and front/back use X/Y.

        tangent_axes = [[2,1],[0,2],[0,1]][normal_axis]

        size = s.get('size',[1,1])[:]

        pos = s.get('pos',[0,0,0])[:]

        if n[normal_axis] > 0:

            pos[normal_axis] += ext[normal_axis]

        for j,axis in enumerate(tangent_axes):

            size[j] += ext[axis]

        local_center = [pos[i]+.5*n[i] for i in range(3)]

        yield {'type':s.get('type'), 'center':world(c,local_center),

               'normal':rotate(c,n), 'tangents':[rotate(c,[int(i==axis) for i in range(3)]) for axis in tangent_axes],

               'sizes':size}



def check_mount(mounted, receiver, kind):

    found=[]

    for p in patches(components[mounted]):

        if p['type'] != kind: continue

        for q in patches(components[receiver]):

            if q['type'] != kind: continue

            if sum(x*y for x,y in zip(p['normal'],q['normal'])) != -1: continue

            for u in range(p['sizes'][0]):

                for w in range(p['sizes'][1]):

                    point = [p['center'][i]+u*p['tangents'][0][i]+w*p['tangents'][1][i] for i in range(3)]

                    delta = [x-y for x,y in zip(point,q['center'])]

                    if abs(sum(x*y for x,y in zip(delta,q['normal']))) > 1e-8: continue

                    projections = [sum(x*y for x,y in zip(delta,t)) for t in q['tangents']]

                    if all(-1e-8 <= x <= size-1+1e-8 for x,size in zip(projections,q['sizes'])):

                        found.append(point)

    if not found: raise ValueError(f'No facing {kind} patch: {mounted} -> {receiver}')

    return {'mounted_component':mounted,'receiving_component':receiver,'type':kind,'face_center_cells':found[0]}



pairs = [(14,1),(15,1),(16,1),(17,1),(18,1),(19,1),

         (20,1),(21,1),(22,1),(23,1),

         (27,26),(28,26),(29,26),(30,8),(31,8),

         (33,32),(34,32),(37,35),(38,35),(39,35),(40,9),(41,9),

         (43,42),(45,42),(81,42),

         (68,67),(69,67),(70,67),(73,71),(74,71),(75,72),(76,72),

         (77,6),(78,7),(80,36)]

results = [check_mount(x,y,'port') for x,y in pairs]

results.append(check_mount(36,35,'radiator_fan'))

print(a.save('compact-petrol-engine-01-complete/mount-face-check.json', {

    'checks':results,

    'limits':['Geometric face checks under inherited direction/column-major conventions.',

              'Surface overlap only, not complete footprint coverage; receiver sizes extended along native stretch axes.',

              'Semantic fluid inlet roles and game attachment are not certified.']}))

print(len(results), 'mount face checks passed')

