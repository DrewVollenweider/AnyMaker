"""Selected build-25904830 hull seed and face-reference calculations.

Explicit finite points only; compiled f32 constants, Python float arithmetic.
This is not point-cloud hull generation, bit-exact native execution, complete
validity checking, or a guarantee that a supplied shape will load in the game.
"""
import math
from mass_properties import _f32,_scalar,_vector

VERSION = '1.0.0'
ROUNDING_FACTOR = _f32(0x34c00000)
TRIANGLE_CROSS_SQUARED_MIN = _f32(0x2b8cbccc)
PLANAR_SQUARED_FACTOR = _f32(0x42100000)
DEFAULT_BUILD_TOLERANCE = _f32(0x3a83126f)


def _dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def _sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def _finite(value):
    if not math.isfinite(value):
        raise ValueError('Model excludes overflow')
    return value


def hull_tolerances(points,requested=DEFAULT_BUILD_TOLERANCE):
    """Reviewed 3D seed rounding scale and point-assignment squared tolerance.

    The scale uses max absolute input coordinates, not bounding-box extents.
    Input coordinates are native shape inputs; moving a vehicle in world space
    does not necessarily change them. No f32 input narrowing is emulated here.
    """
    points = tuple(_vector(p) for p in points)
    requested = _scalar(requested,allow_zero=True)
    scale = sum(max((abs(p[i]) for p in points),default=0.) for i in range(3))
    rounding = _finite(scale*ROUNDING_FACTOR)
    squared = _finite(rounding*rounding)
    return dict(rounding=rounding,assignment_squared=_finite(max(requested*requested,squared)),
                planar_squared=_finite(PLANAR_SQUARED_FACTOR*squared))


def initial_hull_seed(points,requested=DEFAULT_BUILD_TOLERANCE):
    """Trace the selected first-triangle and planar/3D seed decisions only.

    Stable first-maximum ties model the reviewed scans. Subsequent assignment,
    face merging, 2D boundary extraction and vertex caps are not implemented.
    """
    points = tuple(_vector(p) for p in points)
    result = hull_tolerances(points,requested)
    result['point_count'] = len(points)
    if len(points)<3:
        return dict(result,seed_path='too_few_points',triangle=None,fourth=None)
    def choose(indices,score):
        values = [(i,_finite(score(i))) for i in indices]
        return max(values,key=lambda item:item[1])[0]
    first = choose(range(len(points)),lambda i:_dot(points[i],points[i]))
    second = choose((i for i in range(len(points)) if i!=first),
                    lambda i:_dot(_sub(points[i],points[first]),_sub(points[i],points[first])))
    def cross(i):
        return _cross(_sub(points[first],points[i]),_sub(points[second],points[i]))
    third = choose((i for i in range(len(points)) if i not in (first,second)),
                   lambda i:_dot(cross(i),cross(i)))
    normal = cross(third)
    area_squared = _finite(_dot(normal,normal))
    result.update(triangle=(first,second,third),triangle_cross_squared=area_squared,fourth=None)
    if area_squared<TRIANGLE_CROSS_SQUARED_MIN:
        return dict(result,seed_path='triangle_too_small')
    if len(points)==3:
        return dict(result,seed_path='triangle_pair')
    normal = tuple(v/math.sqrt(area_squared) for v in normal)
    centre = tuple(sum(points[j][i] for j in (first,second,third))/3 for i in range(3))
    distance = lambda i:_finite(_dot(_sub(points[i],centre),normal))
    fourth = choose((i for i in range(len(points)) if i not in (first,second,third)),
                    lambda i:abs(distance(i)))
    signed = distance(fourth)
    result.update(fourth=fourth,plane_distance=signed)
    return dict(result,seed_path='three_dimensional' if signed*signed>result['planar_squared']
                else 'planar_pair')


def face_geometry(points):
    """Return a polygon's vertex mean and unnormalized fan normal (2*area).

    The mean is neither an area-weighted polygon centroid nor a volume COM.
    Exact native accumulation order/short-edge choice and rounding differ.
    """
    points = tuple(_vector(p) for p in points)
    if len(points)<3:
        raise ValueError('Supply at least three face vertices')
    mean = tuple(_finite(sum(p[i] for p in points)/len(points)) for i in range(3))
    normal = [0.]*3
    for b,c in zip(points[1:-1],points[2:]):
        term = _cross(_sub(b,points[0]),_sub(c,points[0]))
        normal = [_finite(x+y) for x,y in zip(normal,term)]
    return mean,tuple(normal)


def hull_reference(faces):
    """Unweighted mean of the supplied faces' vertex means, as traced natively."""
    means = [face_geometry(face)[0] for face in faces]
    if not means:
        raise ValueError('Supply at least one face')
    return tuple(_finite(sum(p[i] for p in means)/len(means)) for i in range(3))
