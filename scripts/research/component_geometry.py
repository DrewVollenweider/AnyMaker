"""Explanatory current-build component arithmetic, without game execution.

Inputs are explicit: no unverified native vector/enum defaults are supplied.
Guards are model constraints, not recovered game validation. Python integers
do not reproduce native s32 overflow. No collision/mounting certificate results.
"""
import json
import math


def integer3(values):
    if len(values)!=3 or any(type(value) is not int for value in values):
        raise ValueError('Model requires three integers')
    return tuple(values)


def finite3(values):
    if len(values)!=3 or any(type(value) not in (int,float) or not math.isfinite(value) for value in values):
        raise ValueError('Model requires three finite coordinates')
    return tuple(values)


def upper_extension(requested, maximum):
    """The traced helper uses min per axis; it does not implement a lower clamp."""
    return tuple(min(a,b) for a,b in zip(integer3(requested),integer3(maximum)))


def point_extended(position, extension, center):
    position,extension,center=integer3(position),integer3(extension),finite3(center)
    return tuple(p+(e if p>c else 0) for p,e,c in zip(position,extension,center))


def zone_extended(lower, upper, extension, center):
    lower,upper=integer3(lower),integer3(upper)
    extension,center=integer3(extension),finite3(center)
    if any(a>b for a,b in zip(lower,upper)):
        raise ValueError('Model requires ordered inclusive bounds')
    lo=tuple(p+(e if p-0.5>c else 0) for p,e,c in zip(lower,extension,center))
    hi=tuple(p+(e if p+0.5>c else 0) for p,e,c in zip(upper,extension,center))
    return lo,hi


def zone_volume_sum(zones, extension, center):
    """Sum inclusive zone box counts, including overlaps and nonphysics zones."""
    total=0
    for lower,upper in zones:
        lo,hi=zone_extended(lower,upper,extension,center)
        total+=math.prod(b-a+1 for a,b in zip(lo,hi))
    return total


def port_size_offset(size, direction):
    # Byte-checked native pairs are 0/1 (X), 2/3 (Y), 4/5 (Z).
    if type(size) is not int or size<0 or type(direction) is not int or direction not in range(6):
        raise ValueError('Model requires nonnegative size and cardinal direction 0..5')
    if size%2==0:
        return (0.0,0.0,0.0)
    axis=0 if direction in (0,1) else 1 if direction in (2,3) else 2
    return tuple(0.0 if i==axis else 0.5 for i in range(3))


def node_index(nodes, node_type, ordinal):
    if type(ordinal) is not int:
        raise ValueError('Model requires an integer ordinal')
    count=0
    for index,node in enumerate(nodes):
        if node['type']==node_type:
            if count==ordinal:
                return index
            count+=1
    return -1


if __name__=='__main__':
    print(json.dumps(dict(
        mixed_node_gas_ordinals=[node_index([{'type':'mechanical'},{'type':'gas'},{'type':'gas'},{'type':'gas'}],'gas',i) for i in range(3)],
        point_at_origin=point_extended((0,0,0),(6,6,6),(.1,.1,.1)),
        single_zone_with_same_center=zone_extended((0,0,0),(0,0,0),(6,6,6),(.1,.1,.1)),
        odd_size_y_normal_offset=port_size_offset(1,2),
        limits='Explicit arithmetic examples, not native save validation, builtin default recovery or a game simulation.'),indent=2))
