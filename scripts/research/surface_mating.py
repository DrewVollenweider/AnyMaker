"""Current-build functional mating for resolved cardinal surface bounds.

Inputs are already in the same mounting grid. No octree, placement/collision,
save parser, rotation authority, integer overflow or native bitset ABI is modeled.
Explicit masks use ordinary bit intersection as an analytical assumption.
"""
from dataclasses import dataclass
from component_geometry import integer3
from attachment_geometry import voxel_overlap

VERSION='1.0.0'
NORMALS=((-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1))
NONE,MALE,FEMALE=0,1,2


@dataclass(frozen=True)
class Surface:
    lower: tuple
    upper: tuple
    direction: int
    interface: str
    gender: int
    port_mask: int=0

    def __post_init__(self):
        object.__setattr__(self,'lower',integer3(self.lower))
        object.__setattr__(self,'upper',integer3(self.upper))
        if any(a>b for a,b in zip(self.lower,self.upper)):raise ValueError('Ordered bounds required')
        if type(self.direction) is not int or self.direction not in range(6):raise ValueError('Cardinal direction required')
        if self.lower[self.direction//2]!=self.upper[self.direction//2]:raise ValueError('Planar cardinal bounds required')
        if type(self.interface) is not str:raise ValueError('Explicit interface string required')
        if type(self.gender) is not int or self.gender not in (NONE,MALE,FEMALE):raise ValueError('Declared gender required')
        if type(self.port_mask) is not int or self.port_mask<0:raise ValueError('Nonnegative model mask required')


def compatible(a,b):
    """Type/gender predicate; excludes spatial tests."""
    if not isinstance(a,Surface) or not isinstance(b,Surface):raise ValueError('Explicit surfaces required')
    if a.interface=='port' and a.gender==MALE:
        return ((b.interface=='' and b.gender==NONE) or (b.interface=='port' and b.gender==FEMALE)) and bool(a.port_mask&b.port_mask)
    if b.interface=='port' and b.gender==MALE:
        return ((a.interface=='' and a.gender==NONE) or (a.interface=='port' and a.gender==FEMALE)) and bool(a.port_mask&b.port_mask)
    return a.interface==b.interface and ((a.gender,b.gender) in ((NONE,NONE),(MALE,FEMALE),(FEMALE,MALE)))


def _contains(a,b,c,d):
    return all(x<=u and v<=y for x,y,u,v in zip(a,b,c,d))


def matable(a,b):
    """Caller has established same grid and resolved transformed bounds."""
    if not compatible(a,b) or a.direction^1!=b.direction:return False
    n=NORMALS[a.direction]
    lo=tuple(x+y for x,y in zip(a.lower,n));hi=tuple(x+y for x,y in zip(a.upper,n))
    if not voxel_overlap(lo,hi,b.lower,b.upper):return False
    if a.gender==b.gender==NONE:return True
    if a.gender==MALE and b.gender==FEMALE:return _contains(b.lower,b.upper,lo,hi)
    if a.gender==FEMALE and b.gender==MALE:return _contains(lo,hi,b.lower,b.upper)
    if a.interface=='port' and a.gender==MALE and b.gender==NONE:return _contains(b.lower,b.upper,lo,hi)
    if b.interface=='port' and b.gender==MALE and a.gender==NONE:return _contains(lo,hi,b.lower,b.upper)
    raise ValueError('Outside reviewed ordinary gender branches')
