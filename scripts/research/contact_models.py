"""Selected ordinary wheel-contact arithmetic from build 25904830.

No raycast, support ordering, moving support, tyre lookup, topology or native
physics implementation is simulated. Guards are this model's input domain,
not game validation. 'load' preserves native arithmetic without SI claims.
"""
from math import sqrt
from powertrain_models import clamp,number,positive

VERSION='1.0.0'


def nonnegative(value):
    value=number(value)
    if value<0:raise ValueError('Nonnegative model input required')
    return value


def suspension_load(distance,radius,travel,stiffness,damping,stiffness_setting,
                    damping_setting,previous_compression,bump_stop,body_mass,
                    roll_term=0.0):
    """Return compression, base load and mass-scaled nonnegative normal load.

    roll_term supplies the separately computed roll-damping/velocity term,
    before multiplication by K. The grip path uses base load separately.
    """
    distance=nonnegative(distance);radius=positive(radius);travel=positive(travel)
    k=nonnegative(stiffness)*4*nonnegative(stiffness_setting)**2
    d=nonnegative(damping)*8*nonnegative(damping_setting)**2
    previous_compression=number(previous_compression);bump_stop=nonnegative(bump_stop)
    compression=clamp(1-max(0,distance-radius)/travel,0,1)
    base=k*(compression+compression**3*bump_stop)+d*(compression-previous_compression)
    normal=max(0,base+k*number(roll_term))*clamp(positive(body_mass),1,1000)
    return compression,base,normal


def load_sensitive_grip(base_load,previous_average,sensitivity):
    """Return updated base-load average and sensitivity-scaled grip load."""
    load=max(0,number(base_load));average=nonnegative(previous_average)
    sensitivity=nonnegative(sensitivity)
    average=average+(load-average)*0.003 if average>0 else load
    variation=clamp(load/max(.0001,average)-1,-1,3)
    factor=max(.2,1-sensitivity*variation)
    return average,load*factor


def friction_circle(vector,normal,capacity):
    """Project away the supplied unit normal, then cap tangential magnitude."""
    vector=tuple(map(number,vector));normal=tuple(map(number,normal))
    if len(vector)!=3 or len(normal)!=3:raise ValueError('Three-coordinate model vectors required')
    if abs(sum(x*x for x in normal)-1)>1e-9:raise ValueError('Unit normal required')
    capacity=nonnegative(capacity)
    dot=sum(a*b for a,b in zip(vector,normal))
    tangent=tuple(a-dot*b for a,b in zip(vector,normal))
    length=sqrt(sum(x*x for x in tangent))
    factor=min(1,capacity/length) if length>0 else 1
    return tuple(x*factor for x in tangent)


def pneumatic_brake(pressure):
    """Hydraulic-wheel component's gas-brake fraction; pressure units native."""
    return 1-clamp((number(pressure)-4)/2,0,1)


def support_reaction_scale(support_mass,vehicle_mass):
    return clamp(nonnegative(support_mass)/positive(vehicle_mass),0,1)
