"""Selected joint scheduling, ballscrew and winch arithmetic; build 25904830.

No native collision/constraint/rope physics, structural mounting or dynamic
dispatch is simulated. Guards describe an ordinary model domain, not game
validation. Brake writes and chamber/shaft updates retain their own order.
"""
from math import pi
from powertrain_models import number,positive,unit,clamp

VERSION='1.0.0'


def constraint_pair_tiers(links):
    """Return highest nonnegative tier by peer-body ID, as in the local pass.

    Each link is (component_id, peer_body_id, tier). This does not construct
    the actual dynamic-component vector or infer a whole constraint graph.
    """
    result={}
    for component,peer,tier in links:
        if any(type(x) is not int for x in [component,peer,tier]):raise ValueError('Integer model IDs/tiers required')
        result[peer]=max(result.get(peer,0),tier)
    return result


def hinge_angle_limits(definition_min,definition_max,fraction_min,fraction_max):
    low,high=number(definition_min),number(definition_max)
    a=low+(high-low)*unit(fraction_min);b=low+(high-low)*unit(fraction_max)
    if b<=a:
        midpoint=(a+b)*.5;a,b=midpoint-.01,midpoint+.01
    return a,b


def ballscrew_step(position,lower,upper,rps,dt,slider_body_mass,*,constraint_added=True):
    """One slider's target, brake and native torque-argument calculation.

    The parent writes node mass/brake for each listed slider. The final list
    entry's mass/brake wins; apply_torque accumulates separate pending deltas.
    """
    if type(constraint_added) is not bool:raise ValueError('Boolean added state required')
    position,lower,upper=number(position),number(lower),number(upper)
    if lower>=upper:raise ValueError('Ordered model bounds required')
    mass=number(slider_body_mass)
    if mass<0:raise ValueError('Nonnegative ordinary body mass required')
    advance=number(rps)*positive(dt)*2*pi;node_mass=1+mass;proposed=position+advance
    brake=0 if lower<proposed<upper else .99
    target=clamp(proposed,lower,upper) if constraint_added else position
    return dict(target=target,advance=advance,node_mass=node_mass,brake=brake,
                torque_argument=-node_mass*10*advance,pending_speed_delta=-10*advance)


def winch_step(rps,dt,release,ropes):
    """Return nominal length writes and brake for (length, stretch) inputs.

    Each rope is evaluated with the already-computed same advance. A blocked
    rope sets brake .99; a later valid rope does not reset it and can still
    change its nominal length in this update. Native pressure/tension absent.
    """
    release=number(release)
    if abs(release)>1:raise ValueError('Ordinary release input must be -1..1')
    clutch=1-abs(release);dt=positive(dt);rps=number(rps)
    advance=rps*dt*2*pi if clutch>0 else 0
    lengths=[];brake=0
    for length,stretch in ropes:
        length,stretch=positive(length),number(stretch)
        if stretch<0:raise ValueError('Nonnegative ordinary stretch required')
        candidate=length+advance
        blocked=not .5<candidate<20 or (stretch>1.2 and advance<0)
        if blocked:brake=.99;lengths.append(length)
        else:lengths.append(clamp(candidate,.5,20))
    return dict(clutch=clutch,advance=advance,node_mass=10,torque_argument=-10*advance,
                brake=brake,lengths=lengths)
