"""Selected build-25904830 native primitive mass and inertia models.

Lengths are explicit metre inputs, density is the native shape coefficient.
Results describe the primitive about its own centre in its local axes.
Compiled f32 constants are retained, but arithmetic uses Python floats: this
is not bit-exact native f32 execution, a solver, or a creation mass estimator.
No game process, installation, or creation files are accessed.
"""
from dataclasses import dataclass
import math
import struct

VERSION = '1.0.0'


def _f32(bits):
    return struct.unpack('<f',struct.pack('<I',bits))[0]


PI = _f32(0x40490fdb)
TWO_PI_OVER_THREE = _f32(0x40060a92)
FOUR_PI_OVER_THREE = _f32(0x40860a92)
TWO_FIFTHS = _f32(0x3ecccccd)


@dataclass(frozen=True)
class MassProperties:
    mass: float
    inertia_diagonal: tuple


IDENTITY = ((1.,0.,0.),(0.,1.,0.),(0.,0.,1.))


@dataclass(frozen=True)
class Child:
    properties: MassProperties
    center: tuple = (0.,0.,0.)
    rotation: tuple = IDENTITY


@dataclass(frozen=True)
class CompoundProperties:
    mass: float
    center: tuple
    inertia: tuple


def _scalar(value,allow_zero=False):
    value = float(value)
    if not math.isfinite(value) or (value < 0 if allow_zero else value <= 0):
        raise ValueError('Model requires finite positive dimensions/density; length may be zero')
    return value


def _result(mass,xx,yy,zz):
    if not all(math.isfinite(v) for v in (mass,xx,yy,zz)):
        raise ValueError('Model excludes overflow')
    return MassProperties(mass,(xx,yy,zz))


def box(dimensions,density):
    """Full x/y/z side lengths, matching the wrapper's half-extents conversion.

    Positive input guards are model scope, not a complete native validity rule.
    Native convex margins and collision behaviour are outside this calculation.
    """
    dimensions = tuple(dimensions)
    if len(dimensions) != 3:
        raise ValueError('Expected three full side lengths')
    x,y,z = (_scalar(v) for v in dimensions)
    density = _scalar(density)
    mass = x*y*z*density
    scale = mass/12
    return _result(mass,scale*(y*y+z*z),scale*(x*x+z*z),scale*(x*x+y*y))


def sphere(radius,density):
    """Native sphere mass and isotropic inertia about its centre."""
    radius,density = _scalar(radius),_scalar(density)
    mass = radius*FOUR_PI_OVER_THREE*radius*radius*density
    inertia = mass*TWO_FIFTHS*radius*radius
    return _result(mass,inertia,inertia,inertia)


def capsule_y(radius,cylinder_length,density):
    """Y-axis capsule: cylinder length excludes the two hemispherical ends.

    For explicitly zero cylinder length the reviewed native settings factory
    creates a sphere with density 1000, even when a different density was
    supplied. Normal game reachability of this factory boundary is unproven.
    This model does not emulate f32 input narrowing/underflow into that branch.
    """
    radius = _scalar(radius)
    length = _scalar(cylinder_length,allow_zero=True)
    density = _scalar(density)
    if length == 0:
        return sphere(radius,1000)
    r2 = radius*radius
    hemisphere_mass = r2*TWO_PI_OVER_THREE*radius*density
    cylinder_mass = length*PI*r2*density
    caps_axial = hemisphere_mass*4*r2/5
    cylinder_axial = cylinder_mass*r2*.5
    transverse = ((.75*length*radius+.5*length*length)*hemisphere_mass
                  +caps_axial+length*length*cylinder_mass/12+.25*cylinder_mass*r2)
    return _result(2*hemisphere_mass+cylinder_mass,transverse,
                   caps_axial+cylinder_axial,transverse)


def _vector(values):
    values = tuple(float(x) for x in values)
    if len(values) != 3 or not all(math.isfinite(x) for x in values):
        raise ValueError('Expected a finite three-coordinate vector')
    return values


def combine(children):
    """Combine explicit primitive properties about the mass-weighted centre.

    Child.center is the already transformed child COM, not a creation origin.
    Rotation is an explicit row-major proper orthonormal local-to-parent 3x3
    matrix. The native quaternion packing and creation transforms are outside
    this API. Each supplied child contributes independently, including overlap.
    Guards/tolerance are model choices, not native placement restrictions.
    """
    checked = []
    for child in children:
        mass = _scalar(child.properties.mass)
        diagonal = _vector(child.properties.inertia_diagonal)
        if any(x < 0 for x in diagonal):
            raise ValueError('Expected nonnegative principal inertia')
        center = _vector(child.center)
        rotation = tuple(_vector(row) for row in child.rotation)
        if len(rotation) != 3:
            raise ValueError('Expected a three-row rotation')
        for i in range(3):
            for j in range(3):
                if abs(sum(rotation[i][k]*rotation[j][k] for k in range(3))-(i==j)) > 1e-9:
                    raise ValueError('Model requires an orthonormal rotation')
        a,b,c = rotation
        determinant = a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
        if abs(determinant-1) > 1e-9:
            raise ValueError('Model requires a proper rotation')
        checked.append((mass,diagonal,center,rotation))
    if not checked:
        raise ValueError('Supply at least one child')
    mass = sum(c[0] for c in checked)
    center = tuple(sum(m*p[i] for m,_,p,_ in checked)/mass for i in range(3))
    inertia = [[0.]*3 for _ in range(3)]
    for m,diagonal,p,r in checked:
        d = tuple(p[i]-center[i] for i in range(3))
        d2 = sum(x*x for x in d)
        for i in range(3):
            for j in range(3):
                rotated = sum(r[i][k]*diagonal[k]*r[j][k] for k in range(3))
                inertia[i][j] += rotated+m*((d2 if i==j else 0)-d[i]*d[j])
    values = (mass,*center,*(x for row in inertia for x in row))
    if not all(math.isfinite(x) for x in values):
        raise ValueError('Model excludes overflow')
    return CompoundProperties(mass,center,tuple(tuple(row) for row in inertia))
