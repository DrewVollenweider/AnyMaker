"""Selected build-25904830 survival arithmetic, not an actor/game simulator.

Ordinary-domain guards belong to these explanatory models. Native scheduling,
authority, physics, item lifecycle and network encoding are excluded.
"""
from powertrain_models import number,positive,unit,clamp

VERSION='1.0.0'


def condition_clock(counter):
    if type(counter) is not int or counter<0:raise ValueError('Nonnegative model counter required')
    counter+=1
    return (0,True) if counter>60 else (counter,False)


def vital_flags(value):
    value=clamp(number(value),0,1)
    return dict(value=value,warning=0<value<=.5,critical=value<=0)


def stamina_step(value,speed,dt,*,sprint=False,swim=False,jump=False,previous_jump=False):
    value=unit(value);speed=number(speed);dt=positive(dt)
    if speed<0:raise ValueError('Nonnegative ordinary movement speed required')
    if any(type(v) is not bool for v in [sprint,swim,jump,previous_jump]):raise ValueError('Boolean inputs required')
    factor=clamp((speed-2)*.5,0,1);draining=False
    if sprint and factor>0:value-=factor*dt/45;draining=True
    if swim and speed>.5:value-=dt/45;draining=True
    if jump and not previous_jump:value-=.05
    if not draining:value+=dt/90
    return dict(value=clamp(value,0,1),draining=draining,previous_jump=jump)


def clothing_wetness_step(wetness,rain,submergence,temperature,resistance):
    wetness=unit(wetness);rain=unit(rain);submergence=unit(submergence);temperature=number(temperature);resistance=number(resistance)
    if submergence>0 and submergence>=wetness:wetness=min(submergence,wetness+1/15)
    elif rain>0:wetness+=rain*(1-clamp(resistance/25,0,1))/90
    else:wetness-=1/(1200 if temperature<=15 else 600)
    return clamp(wetness,0,1)


def insulation(resistance,wetness):
    return clamp(number(resistance)/90,0,1)*30*(1-unit(wetness)*.7)


def effective_temperature(weather,insulation_degrees,wind,wetness,stamina,submergence,*,sheltered=False):
    if type(sheltered) is not bool:raise ValueError('Boolean model shelter required')
    return (number(weather)+number(insulation_degrees)-(0 if sheltered else unit(wind)*10)
            -unit(wetness)*6+(1-unit(stamina))*5-unit(submergence)*10)
