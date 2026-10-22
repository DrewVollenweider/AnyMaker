"""Selected combustion demand/draw arithmetic from build 26113663.

Explicit positive component-volume and stock inputs; registered intake/exhaust
manifolds and finite ordinary states are assumed. No graph, shaft dynamics,
heat/wear, scheduling, native clamp exceptional values or gameplay simulation.
Model guards are not game validation. Results describe calculated energy,
not measured shaft work or a recovered torque-intrinsic unit.
"""
from powertrain_models import clamp,number,positive

VERSION='1.0.0'
FUEL_ENERGY=32000000.0
EFFICIENCY=0.3
AIR_PER_FUEL=10.9*800.0


def demand(volume,rps,throttle,intake_pressure=1.0,exhaust_pressure=0.0,rate=60):
    if type(volume) is not int or volume<=0:raise ValueError('Positive integer model volume required')
    rps=number(rps);throttle=clamp(number(throttle),0,1);rate=positive(rate)
    boost=1+(clamp(number(intake_pressure),1,10)-1)/9
    exhaust=1-clamp((number(exhaust_pressure)-4)/16,0,1)
    speed=clamp(rps*60/8000+.2,0,1)
    fuel=volume*400/rate*speed*boost*throttle*exhaust/(FUEL_ENERGY*EFFICIENCY)
    if rps<6 or rps>8000/60:fuel=0.0
    return dict(fuel=fuel,air=fuel*AIR_PER_FUEL,boost=boost,exhaust=exhaust)


def consume(requested_fuel,total_gas,fresh_air,petrol,damage=0):
    requested_fuel=number(requested_fuel)
    if requested_fuel<0:raise ValueError('Nonnegative requested fuel required')
    if type(damage) is not int or damage not in (0,1,2):raise ValueError('Model damage stage must be 0, 1 or 2')
    total_gas=number(total_gas);fresh_air=number(fresh_air);petrol=number(petrol)
    if not 0<=fresh_air<=total_gas or petrol<0:raise ValueError('Invalid stock composition')
    if requested_fuel==0:return dict(gas=0.0,fresh_air=0.0,fuel=0.0,air_factor=0.0,fuel_factor=0.0,energy=0.0)
    # The actual code divides by stock totals; zero-stock exceptional arithmetic
    # is outside this explicit model, rather than replaced with guessed guards.
    total_gas=positive(total_gas);petrol=positive(petrol)
    requested_air=requested_fuel*AIR_PER_FUEL
    gas=total_gas*clamp(requested_air/total_gas,0,1)
    air=fresh_air*clamp(requested_air/total_gas,0,1)
    fuel=petrol*clamp(requested_fuel/petrol,0,1)
    air_factor=clamp(air/requested_air,0,1)
    energy=fuel*air_factor*FUEL_ENERGY*EFFICIENCY*(1,.5,0)[damage]
    return dict(gas=gas,fresh_air=air,fuel=fuel,air_factor=air_factor,
                fuel_factor=clamp(fuel/requested_fuel,0,1),energy=energy)
