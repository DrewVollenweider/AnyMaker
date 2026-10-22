"""Build-25904830 hull mass integration from an explicit closed boundary.

This models the reviewed positive-volume integration stage. It does not create
the game's convex hull from a point cloud, reproduce f32 arithmetic, validate
all self-intersections/convexity, model degenerate native fallback, or read saves.
Faces must describe an outward-oriented, closed, non-self-intersecting surface.
"""
from collections import Counter
import math

from mass_properties import CompoundProperties,_scalar,_vector,_f32
from hull_geometry import hull_reference

VERSION = '1.1.0'
DIAGONAL_MOMENT = _f32(0x3c888889)
CROSS_MOMENT = _f32(0x3c088889)
CENTER_SUM_THRESHOLD = _f32(0x34000000)


def _sub(a,b):
    return tuple(x-y for x,y in zip(a,b))


def _dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def _cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])


def surface_mass_properties(vertices,faces,density):
    """Mass, centre and COM inertia for a supplied polygonal boundary.

    Faces are index loops, triangulated as fans. Each undirected boundary edge
    must occur twice with opposite directions. These checks are model guards,
    not a complete topology/convexity certificate or native validity rules.
    The native centre fallback at determinant sum <= f32 epsilon is excluded.
    """
    vertices = tuple(_vector(p) for p in vertices)
    density = _scalar(density)
    if len(vertices)<4:
        raise ValueError('Model requires at least four supplied vertices')
    edges = Counter()
    triangles = []
    face_loops = []
    for face in faces:
        face = tuple(face)
        if len(face)<3 or any(type(i) is not int or not 0<=i<len(vertices) for i in face):
            raise ValueError('Expected face loops of at least three valid vertex indices')
        if len(set(face))!=len(face):
            raise ValueError('Repeated face vertex')
        face_loops.append(face)
        for a,b in zip(face,face[1:]+face[:1]):
            edges[(a,b)] += 1
        triangles.extend((face[0],face[i],face[i+1]) for i in range(1,len(face)-1))
    if not triangles or any(count!=1 or edges[(b,a)]!=1 for (a,b),count in list(edges.items())):
        raise ValueError('Model requires opposite pairs of oriented boundary edges')
    # The native face field is the mean of that face's vertices; the hull helper
    # averages these face fields without area weights. Accumulation still uses
    # Python floats rather than native f32 operations.
    reference = hull_reference(tuple(tuple(vertices[i] for i in face) for face in face_loops))
    determinants = []
    weighted = [0.]*3
    for indices in triangles:
        a,b,c = (vertices[i] for i in indices)
        det = _dot(_sub(a,reference),_cross(_sub(b,reference),_sub(c,reference)))
        determinants.append(det)
        for i in range(3):
            weighted[i] += det*(a[i]+b[i]+c[i]+reference[i])
    volume6 = sum(determinants)
    if not math.isfinite(volume6) or volume6<=CENTER_SUM_THRESHOLD:
        raise ValueError('Model requires a finite positive determinant sum above the native centre fallback')
    center = tuple(x/(4*volume6) for x in weighted)
    second = [[0.]*3 for _ in range(3)]
    for indices in triangles:
        points = tuple(_sub(vertices[i],center) for i in indices)
        det = _dot(points[0],_cross(points[1],points[2]))
        for i in range(3):
            for j in range(i,3):
                value = det*sum(
                    (DIAGONAL_MOMENT if k==l else CROSS_MOMENT)*points[k][i]*points[l][j]
                    for k in range(3) for l in range(3))
                second[i][j] += value
                if i!=j:
                    second[j][i] += value
    trace = sum(second[i][i] for i in range(3))
    inertia = tuple(tuple(density*((trace if i==j else 0)-second[i][j])
                          for j in range(3)) for i in range(3))
    mass = density*volume6/6
    if not all(math.isfinite(x) for x in (mass,*center,*(x for row in inertia for x in row))):
        raise ValueError('Model excludes overflow')
    return CompoundProperties(mass,center,inertia)
