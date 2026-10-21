"""Selected build-25904830 vector-angle and plate turn-consistency models.

Finite ordinary inputs only. Python libm is not a bit-exact emulation of the
game's native acos implementation. No game process or creation file access.
"""
import math

VERSION = '1.0.0'


def _vec3(value):
    result = tuple(float(x) for x in value)
    if len(result) != 3 or not all(math.isfinite(x) for x in result):
        raise ValueError('Expected a finite three-coordinate vector')
    return result


def _dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def _unit(value):
    length = math.sqrt(_dot(value,value))
    if not math.isfinite(length) or length <= 0:
        raise ValueError('Model requires a finite nonzero basis vector')
    return tuple(x/length for x in value)


def dot_angle3(first,second):
    """Two-argument native vec3 angle: acos(clamp(raw dot,-1,+1)).

    The native wrapper does not normalize either input. The usual geometric
    angle interpretation therefore requires unit inputs from the caller.
    """
    first,second = _vec3(first),_vec3(second)
    value = _dot(first,second)
    if not math.isfinite(value):
        raise ValueError('Model excludes overflow')
    return math.acos(min(1.0,max(-1.0,value)))


def projected_angle3(first,second,axis_x,axis_y):
    """Four-argument native vec3 angle, in radians and with native sign.

    Project onto the supplied axes, normalize each resulting vec2, and use
    fallback (0,1) for zero projected length. The axes themselves are not
    normalized or made orthogonal by the native wrapper.
    """
    axis_x,axis_y = _vec3(axis_x),_vec3(axis_y)
    def project(vector):
        vector = _vec3(vector)
        x,y = _dot(vector,axis_x),_dot(vector,axis_y)
        length = math.sqrt(x*x+y*y)
        if not math.isfinite(length):
            raise ValueError('Model excludes overflow')
        return (x/length,y/length) if length > 0 else (0.0,1.0)
    a,b = project(first),project(second)
    magnitude = math.acos(min(1.0,max(-1.0,_dot(a,b))))
    return magnitude if b[0]*a[1]-a[0]*b[1] > 0 else -magnitude


def consistent_plate_turns(points,normal):
    """Model test_is_convex's signed-turn check, not complete plate validity.

    Returns True for fewer than three points, matching this helper; upstream
    placement rejects that case. Accepts zero turns, but rejects mixed nonzero
    turn signs. It does not independently check coplanarity, simple polygons,
    winding count, boundary references, duplicates, or type-specific frames.
    """
    points = [_vec3(p) for p in points]
    normal = _vec3(normal)
    if len(points) < 3:
        return True
    reference = (0.0,1.0,0.0) if abs(normal[1]) <= .99 else (1.0,0.0,0.0)
    axis_x = _unit(_cross(reference,normal))
    axis_y = _unit(_cross(normal,axis_x))
    sign = 0
    for i,a in enumerate(points):
        b,c = points[(i+1)%len(points)],points[(i+2)%len(points)]
        edge_a = tuple(y-x for x,y in zip(a,b))
        edge_b = tuple(y-x for x,y in zip(b,c))
        angle = projected_angle3(edge_a,edge_b,axis_x,axis_y)
        current = (angle > 0)-(angle < 0)
        if sign == 0:
            sign = current
        elif current and current != sign:
            return False
    return True
