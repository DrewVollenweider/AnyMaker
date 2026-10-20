"""Selected build-25904830 sensing arithmetic and eligibility predicates.

Ordinary finite inputs only. This does not simulate perception timers, native
casts/angles, random-number generation, spawn placement, state machines or AI.
"""
from powertrain_models import number,unit,clamp

VERSION='1.0.0'


def daylight(day):
    day=unit(day)
    return clamp((day-.4)/.3,0,1) if day<.7 else 1


def actor_ranges(visible,audible,speed,fog,day,light,*,crouched=False,sleeping=False,zombie_factor=1):
    visible,audible,speed=number(visible),number(audible),number(speed)
    if min(visible,audible,speed)<0:raise ValueError('Nonnegative ordinary ranges/speed required')
    if type(crouched) is not bool or type(sleeping) is not bool:raise ValueError('Boolean states required')
    s=clamp((speed-1)/3,0,1);d=max(daylight(day),unit(light));fog=unit(fog);zombie_factor=unit(zombie_factor)
    visible*= (.8+.2*s)*(1-.7*fog)*(.4+.6*d)*(.5 if crouched else 1)
    audible*=s*(.02 if crouched else 1)
    visible,audible=max(visible,3),max(audible,1)
    if sleeping:visible*=.1;audible*=.4
    return visible*zombie_factor,audible*zombie_factor


def vehicle_ranges(visible,audible,fog,day,*,sleeping=False,zombie_factor=1):
    visible,audible=number(visible),number(audible)
    if min(visible,audible)<0:raise ValueError('Nonnegative ordinary ranges required')
    if type(sleeping) is not bool:raise ValueError('Boolean model state required')
    # The reviewed vehicle helper accepts but does not apply observer sleep.
    visible=max(visible*(1-.7*unit(fog))*(.2+.8*daylight(day)),3)
    return visible*unit(zombie_factor),max(audible,1)*unit(zombie_factor)


def actor_eligible(kind,flags,own_team,target_team,*,behavior='prey',incapacitated=False,invisible=False):
    if kind not in ['character','creature','zombie']:raise ValueError('Known model actor kind required')
    if any(type(v) is not int for v in [flags,own_team,target_team]) or flags<0:raise ValueError('Integer flags/team IDs required')
    if behavior not in ['prey','predator','monster']:raise ValueError('Known behavior required')
    if type(incapacitated) is not bool or type(invisible) is not bool:raise ValueError('Boolean states required')
    if own_team!=0 and own_team==target_team:return False
    if incapacitated and not flags&(1<<4):return False
    if not flags&(1<<['character','creature','zombie'].index(kind)):return False
    if kind=='creature' and behavior=='prey':return False
    return not invisible


def zombie_factor(actor_id):
    if type(actor_id) is not int or actor_id<0:raise ValueError('Nonnegative ordinary actor ID required')
    return .8+(actor_id%9)/8*.2


def weighted_selection(weights,draw):
    """Selected zombie cumulative-choice step for a supplied draw, not an RNG.

    Equality stays with the current bucket. Native zero-width draw generation
    and endpoint inclusion are not inferred from this model.
    """
    weights=[number(w) for w in weights];draw=number(draw)
    if not weights or min(weights)<0 or not 0<=draw<=number(sum(weights)):raise ValueError('Valid supplied draw and nonnegative weights required')
    index=0
    while index<len(weights)-1 and draw>weights[index]:draw-=weights[index];index+=1
    return index
