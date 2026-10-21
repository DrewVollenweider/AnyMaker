"""Read-only plate reconstruction checks for Anymaker build 25904830.

Models selected node/edge/plate loader gates, not a complete loader, renderer,
polygon validator or attachment certificate. Python arithmetic does not wrap
as native s32. Later duplicate edges are ignored by the reviewed load path.
Additional geometry warnings are tool diagnostics.
"""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import math
from pathlib import Path

from component_geometry import integer3

VERSION='1.0.0'
LIMITS=('Selected reference gates and direction/size reconstruction only; '
        'not full native load, polygon validity, rendering or structural acceptance. '
        'Python arithmetic does not reproduce s32 overflow.')


def _integer(value):
    if type(value) is not int:raise ValueError('Model requires integer native IDs/sizes')
    return value


def _list(value):
    if not isinstance(value,list):raise ValueError('Expected a native JSON array')
    return value


def _sub(a,b):return tuple(x-y for x,y in zip(a,b))


def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def calculate_direction(points):
    """63379396: fixed first segment, first nonparallel later segment, X+ fallback."""
    points=[integer3(p) for p in points]
    if len(points)>=3:
        first=_sub(points[1],points[0])
        for a,b in zip(points[1:-1],points[2:]):
            normal=_cross(first,_sub(b,a))
            if normal!=(0,0,0):return normal
    return (1,0,0)


def canonical_loop(points):
    """Diagnostic key for coincident loops, independent of start and winding."""
    points=tuple(map(tuple,points))
    if not points:return ()
    reverse=points[::-1]
    smallest=min(points)
    return min(sequence[i:]+sequence[:i] for sequence in (points,reverse)
               for i,point in enumerate(sequence) if point==smallest)


def audit_body(body,body_index=0):
    nodes=_list(body.get('nodes',[]));edges=_list(body.get('edges',[]));plates=_list(body.get('plates',[]))
    node_counts=Counter(_integer(n.get('id',0)) for n in nodes)
    positions={_integer(n.get('id',0)):integer3(n.get('pos',[0,0,0])) for n in nodes}
    pairs=defaultdict(list);ignored_edges=[]
    for index,edge in enumerate(edges):
        a,b=_integer(edge.get('n0',0)),_integer(edge.get('n1',0))
        if a in positions and b in positions:
            key=tuple(sorted((a,b)))
            if pairs[key]:ignored_edges.append(index)
            pairs[key].append((index,_integer(edge.get('size',0))))
    rows=[];loops=defaultdict(list)
    for index,plate in enumerate(plates):
        ids=[_integer(x) for x in _list(plate.get('nodes',[]))]
        row=dict(plate_index=index,plate_id=_integer(plate.get('id',0)),status='references_available',warnings=[])
        rows.append(row)
        if len(ids)<3:row.update(status='not_created',reason='fewer_than_three_nodes');continue
        missing=sorted(set(ids)-positions.keys())
        if missing:row.update(status='not_created',reason='missing_nodes',missing_node_ids=missing);continue
        duplicates=sorted({x for x in ids if node_counts[x]>1})
        if duplicates:row.update(status='unresolved',reason='duplicate_node_ids',duplicate_node_ids=duplicates);continue
        boundary=[pairs.get(tuple(sorted((a,b))),[]) for a,b in zip(ids,ids[1:]+ids[:1])]
        absent=[i for i,candidates in enumerate(boundary) if not candidates]
        if absent:row.update(status='not_created',reason='missing_boundary_edges',missing_boundary_indices=absent);continue
        if any(len(candidates)>1 for candidates in boundary):
            row['warnings'].append('later_duplicate_boundary_edges_ignored')
        points=[positions[x] for x in ids];normal=calculate_direction(points)
        first=points[0];size=boundary[0][0][1];saved_size=_integer(plate.get('size',0))
        coplanar=all(sum(n*d for n,d in zip(normal,_sub(p,first)))==0 for p in points)
        row.update(calculated_direction=normal,calculated_position=first,
                   boundary_edge_indices=[c[0][0] for c in boundary],
                   inferred_size=size,saved_size=saved_size,coplanar=coplanar)
        if size!=saved_size:row['warnings'].append('saved_size_differs_from_first_boundary_edge')
        if len(set(ids))!=len(ids):row['warnings'].append('repeated_node_id_in_loop')
        if len(set(points))!=len(points):row['warnings'].append('repeated_coordinate_in_loop')
        # These do not turn into claimed game rejection conditions.
        if not coplanar:row['warnings'].append('noncoplanar_loop')
        if not any(_cross(_sub(points[1],points[0]),_sub(b,a))!=(0,0,0)
                   for a,b in zip(points[1:-1],points[2:])):
            row['warnings'].append('direction_helper_uses_x_positive_fallback')
        loops[canonical_loop(points)].append(index)
    shared=[indices for indices in loops.values() if len(indices)>1]
    same_facing=[]
    for indices in shared:
        facing=defaultdict(list)
        for i in indices:
            direction=rows[i]['calculated_direction'];divisor=math.gcd(*direction)
            facing[(tuple(x//divisor for x in direction),rows[i]['inferred_size'])].append(i)
        same_facing.extend(group for group in facing.values() if len(group)>1)
    for indices in same_facing:
        for i in indices:rows[i]['warnings'].append('same_facing_same_size_node_loop')
    return dict(body_index=body_index,body_id=_integer(body.get('id',0)),
                plates=len(rows),reference_failures=sum(r['status']=='not_created' for r in rows),
                unresolved=sum(r['status']=='unresolved' for r in rows),
                warning_count=sum(len(r['warnings']) for r in rows),
                shared_node_loop_groups=shared,same_facing_loop_groups=same_facing,
                ignored_duplicate_edge_indices=ignored_edges,plate_results=rows)


def audit_document(document):
    if not isinstance(document,dict) or not isinstance(document.get('vehicles'),dict):
        raise ValueError('Expected a native creation with vehicles.vehicles')
    bodies=_list(document['vehicles'].get('vehicles',[]))
    results=[audit_body(body,i) for i,body in enumerate(bodies)]
    return dict(schema=1,tool_version=VERSION,build=25904830,limits=LIMITS,
                summary=dict(bodies=len(results),plates=sum(x['plates'] for x in results),
                             reference_failures=sum(x['reference_failures'] for x in results),
                             unresolved=sum(x['unresolved'] for x in results),
                             warning_count=sum(x['warning_count'] for x in results)),bodies=results)


def audit_file(path):
    raw=Path(path).read_bytes();report=audit_document(json.loads(raw))
    report['input_sha256']=hashlib.sha256(raw).hexdigest()
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('creation',type=Path);parser.add_argument('--output',type=Path)
    args=parser.parse_args();text=json.dumps(audit_file(args.creation),indent=2)+'\n'
    if args.output:
        with args.output.open('x',encoding='utf-8') as out:out.write(text)
    else:print(text,end='')
