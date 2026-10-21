"""Build-25904830 attachment helper arithmetic; no game execution.

Explicit inputs only. This does not gather spatial candidates, parse saves,
evaluate complete attachment predicates, or certify native creations. Guards
and work limits are model constraints. Python integers do not wrap as s32;
floating arithmetic assumes finite ordinary inputs without overflow.
"""
import math

from component_geometry import finite3,integer3

VERSION='1.0.0'


def _point2(value,integer=False):
    if len(value)!=2 or any(type(x) is not int if integer else
                           type(x) not in (int,float) or not math.isfinite(x) for x in value):
        raise ValueError('Model requires two integer or finite coordinates')
    return tuple(value)


def _bounds(lower,upper):
    if any(a>b for a,b in zip(lower,upper)):
        raise ValueError('Model requires ordered inclusive bounds')


def _cross2(a,b):
    return a[0]*b[1]-a[1]*b[0]


def _sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def voxel_overlap(lower_a,upper_a,lower_b,upper_b):
    """63709927: shared boundary coordinates count as overlap."""
    a,b,c,d=map(integer3,(lower_a,upper_a,lower_b,upper_b))
    _bounds(a,b);_bounds(c,d)
    return all(x<=w and z<=y for x,y,z,w in zip(a,b,c,d))


def surface_bounds(direction,position,size,extension,stretch_center):
    """62420550: local inclusive bounds, including the quarter-unit deadband.

    Direction enum: X-/X+/Y-/Y+/Z-/Z+ = 0..5. No component/grid transform here.
    """
    if type(direction) is not int or direction not in range(6):
        raise ValueError('Model requires cardinal direction 0..5')
    position=integer3(position);size=_point2(size,True)
    extension=integer3(extension);center=finite3(stretch_center)
    if min(size)<1 or min(extension)<0:
        raise ValueError('Model requires positive size and nonnegative extension')
    axis=direction//2
    tangents=((2,1),(0,2),(0,1))[axis]
    lo=list(position);hi=list(position)
    for dimension,index in enumerate(tangents):hi[index]+=size[dimension]-1
    physical_lo=[x-.5 for x in lo];physical_hi=[x+.5 for x in hi]
    for index in tangents:
        if physical_lo[index]>center[index]-.25:lo[index]+=extension[index]
        if physical_hi[index]>center[index]+.25:hi[index]+=extension[index]
    plane=physical_hi[axis] if direction%2 else physical_lo[axis]
    if plane>center[axis]:
        lo[axis]+=extension[axis];hi[axis]+=extension[axis]
    return tuple(lo),tuple(hi),tuple(hi[i]-lo[i]+1 for i in tangents)


def grids_equivalent(origin_a,direction_a,origin_b,direction_b):
    """63198804 helper result, not a general world-plane equivalence test."""
    a,u,b,v=map(integer3,(origin_a,direction_a,origin_b,direction_b))
    if sum(x!=0 for x in u)==sum(x!=0 for x in v)==1:return True
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    sign=lambda x:(x>0)-(x<0)
    same=all(sign(x)==sign(y) for x,y in zip(u,v)) and cross==(0,0,0)
    return same and sum(x*(y-z) for x,y,z in zip(u,b,a))==0


def sampled_line_rectangle(lower,upper,start,end,*,max_steps=1000000):
    """63682197: integer raster traversal, not continuous segment clipping."""
    lower,upper,start,end=map(lambda p:_point2(p,True),(lower,upper,start,end))
    lo=tuple(min(x,y) for x,y in zip(lower,upper));hi=tuple(max(x,y) for x,y in zip(lower,upper))
    if type(max_steps) is not int or max_steps<1:raise ValueError('Positive work limit required')
    if max(abs(x-y) for x,y in zip(start,end))+1>max_steps:raise ValueError('Model work limit exceeded')
    x,y=start;dx=abs(end[0]-x);dy=-abs(end[1]-y)
    sx=1 if x<end[0] else -1;sy=1 if y<end[1] else -1;error=dx+dy
    while True:
        if lo[0]<=x<=hi[0] and lo[1]<=y<=hi[1]:return True
        if (x,y)==end:return False
        twice=2*error
        if twice>=dy:
            if x==end[0]:return False
            error+=dy;x+=sx
        if twice<=dx:
            if y==end[1]:return False
            error+=dx;y+=sy


def sampled_triangle_rectangle(lower,upper,a,b,c,*,max_samples=1000000):
    """63692561: search rectangle lattice points with closed half-plane tests.

    This can miss a continuous overlap with no rectangle lattice point inside.
    Degenerate triangles retain the helper's half-plane behavior.
    """
    lower,upper,a,b,c=map(lambda p:_point2(p,True),(lower,upper,a,b,c))
    lo=tuple(min(x,y) for x,y in zip(lower,upper));hi=tuple(max(x,y) for x,y in zip(lower,upper))
    samples=(hi[0]-lo[0]+1)*(hi[1]-lo[1]+1)
    if type(max_samples) is not int or max_samples<1 or samples>max_samples:
        raise ValueError('Model work limit exceeded')
    for x in range(lo[0],hi[0]+1):
        for y in range(lo[1],hi[1]+1):
            point=(x,y)
            signs=[_cross2(_sub(q,p),_sub(point,p)) for p,q in ((a,b),(b,c),(c,a))]
            if all(v>=0 for v in signs) or all(v<=0 for v in signs):return True
    return False


def compiled_triangle_rectangle(lower,upper,a,b,c):
    """63685564: preserve its corner choices, including repeated corner 1.

    This intentionally models the reviewed helper, not an ideal triangle test.
    It does not prove that a particular whole-game placement reaches the case.
    """
    lo,hi,a,b,c=map(_point2,(lower,upper,a,b,c));_bounds(lo,hi)
    tri=(a,b,c)
    if any(all(p[i]>hi[i] for p in tri) or all(p[i]<lo[i] for p in tri) for i in range(2)):
        return False
    corners=(lo,(hi[0],lo[1]),hi,(lo[0],hi[1]))
    orientation=1 if _cross2(_sub(b,a),_sub(c,a))>0 else -1
    for index,(p,q) in enumerate(((a,b),(b,c),(c,a))):
        edge=_sub(q,p);normal=(edge[1]*orientation,-edge[0]*orientation)
        sampled=corners if index==0 else (corners[1],corners[1],corners[2],corners[3])
        if all(sum(n*(x-y) for n,x,y in zip(normal,point,p))>0 for point in sampled):return False
    return True
