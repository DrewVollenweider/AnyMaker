"""Selected native powertrain arithmetic, not a complete game simulator.

Build 25904830: torque nodes/islands, motor demand, alternator and rotor.
Inputs are explicit ordinary finite states. Guards define this model's domain;
they do not establish native validation, ABI, units, scheduling or acceptance.
The native field named mass is not asserted to be SI rotational inertia.
"""
from dataclasses import dataclass
from math import exp,isfinite,pi,prod

VERSION='1.0.0'
TORQUE_ENERGY_SCALE=0.04
TORQUE_BUILD_RETAIN=0.9998


def number(value):
    if isinstance(value,bool) or not isinstance(value,(int,float)) or not isfinite(value):
        raise ValueError('Finite real model input required')
    return float(value)


def positive(value):
    value=number(value)
    if value<=0:raise ValueError('Positive model input required')
    return value


def unit(value):
    value=number(value)
    if not 0<=value<=1:raise ValueError('Model factor outside 0..1')
    return value


def clamp(value,low,high):return min(max(value,low),high)


@dataclass(frozen=True)
class TorqueNode:
    rps:float
    mass:float
    ratio:float=1.0
    clutch:float=1.0
    brake:float=0.0
    island_ratio:float=1.0


def applied_delta(current_delta,applied,mass):
    """apply_torque adds applied / mass to pending delta, without an extra dt."""
    return number(current_delta)+number(applied)/positive(mass)


def build_rps(rps,delta):
    """The reviewed build consumes pending delta and applies native retention."""
    return (number(rps)+number(delta))*TORQUE_BUILD_RETAIN


def island_post_build(nodes):
    """Selected post_build; supplied topology/ratios are already established.

    Effective weight is mass*clutch*q^2; speed contribution contains another
    clutch factor. Brakes multiply the shared numerator before node lerps.
    This function does not build the topology or resolve inconsistent cycles.
    """
    parsed=[]
    for n in nodes:
        r=number(n.rps);m=positive(n.mass);c=unit(n.clutch);b=unit(n.brake)
        q=number(n.ratio)*number(n.island_ratio)
        if q==0:raise ValueError('Zero total ratio outside model domain')
        parsed.append((r,m,c,b,q))
    weights=[m*c*q*q for r,m,c,b,q in parsed]
    denominator=sum(weights)
    if denominator<=0:return tuple(r for r,m,c,b,q in parsed)
    numerator=sum((r*c/q)*w for (r,m,c,b,q),w in zip(parsed,weights))
    numerator*=prod(1-b for r,m,c,b,q in parsed)
    shared=numerator/denominator
    return tuple(r+(shared*q-r)*c for r,m,c,b,q in parsed)


def motor_request(actual_rps,target_rps,max_rps,wattage,output_factor,power_factor,dt,
                  reverse=False,reverse_data=False):
    """Return signed normalized demand and requested electrical energy.

    Demand beyond the target in its current direction is suppressed; this
    reviewed branch is not regenerative braking. Supply acceptance is external.
    """
    actual=number(actual_rps);limit=positive(max_rps)
    target=clamp(number(target_rps),-limit,limit)
    if type(reverse) is not bool or type(reverse_data) is not bool:raise ValueError('Boolean flags required')
    if reverse!=reverse_data:target=-target
    demand=clamp((target-actual)/limit,-1,1)
    if target>=0 and actual>target or target<=0 and actual<target:demand=0.0
    energy=positive(wattage)*unit(output_factor)*unit(power_factor)*positive(dt)*abs(demand)
    return demand,energy


def alternator_step(rps,max_output_rps,wattage,quantity,capacity,dt):
    """Ordinary non-overfull content: 75% electrical gain, full shaft debit.

    Return new content quantity, displayed electrical power and applied shaft
    quantity. Exact external electrical distribution remains outside the model.
    """
    rps=number(rps);limit=positive(max_output_rps);power=positive(wattage)
    quantity=number(quantity);capacity=positive(capacity);dt=positive(dt)
    if not 0<=quantity<=capacity:raise ValueError('Overfull/negative content outside model domain')
    candidate=min(capacity-quantity,power*clamp(abs(rps)/limit,0,1)*dt)
    gain=candidate*0.75
    sign=(rps>0)-(rps<0)
    return quantity+gain,gain/dt,-candidate*TORQUE_ENERGY_SCALE*sign


def swashplate_mix(input_pitch,roll_l,roll_r):
    """Names match the three reflected mechanical-input fields."""
    input_pitch,roll_l,roll_r=map(number,(input_pitch,roll_l,roll_r))
    roll=clamp(roll_r-roll_l,-1,1)
    collective=clamp((roll_l+roll_r)/2,-1,1)
    pitch=clamp(input_pitch-collective,-1,1)
    return collective,pitch,roll


def rotor_step(rps,length,installed_blades,dt,collective,pitch=0.0,roll=0.0):
    """Four scalar axial impulses and pending shaft input; no world solver.

    Includes the reviewed transverse-angular-velocity retention coefficient.
    Does not model collision casts, installed inventory or transforms.
    """
    rps=number(rps);length=positive(length);dt=positive(dt)
    if type(installed_blades) is not int or installed_blades<0:raise ValueError('Nonnegative blade count required')
    collective,pitch,roll=map(number,(collective,pitch,roll))
    quadrants=tuple(clamp(v,-1,1) for v in
                    (collective+roll,collective-roll,collective+pitch,collective-pitch))
    base=rps*2*pi*dt*length*32*installed_blades*0.25
    impulses=tuple(base*q for q in quadrants)
    load=-sum(abs(v) for v in impulses)*((rps>0)-(rps<0))-rps*2*pi*dt*length*32
    transverse_retain=exp(-abs(rps)*length*installed_blades*0.5*dt)
    return impulses,load,transverse_retain


def ground_effect_extra(distance):
    """Distance-only factor after native hit/attitude/mass filters succeed."""
    distance=number(distance)
    if not 0<=distance<=32:raise ValueError('Distance outside reviewed cast range')
    return (1-distance/32)**2
