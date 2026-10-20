"""Small explanatory models of reviewed native arithmetic; never executes game code.

These models are not a game simulator, native save editor, or recovered source.
They assume finite, nonnegative, internally consistent liquid quantities and
distinct containers. Validation errors are model guards, not game restrictions.
See doc/knowledge/research/OFFLINE-SYSTEMS-20261019.md for versioned evidence.
"""
from dataclasses import dataclass
import json
import math


def nonnegative(value):
    value=float(value)
    if not math.isfinite(value) or value<0:raise ValueError('Require finite nonnegative model input')
    return value


def consume_sequence(available,requests):
    """Connected group, in supplied call order; modes are binary or fractional."""
    available=nonnegative(available);pending=0.0;results=[]
    for mode,request in requests:
        request=nonnegative(request)
        if mode not in ('binary','fractional'):raise ValueError('Unknown consumer mode')
        remaining=available-pending
        accepted=0.0
        if request>0 and remaining>0:
            if mode=='fractional':accepted=min(request,remaining)
            elif remaining>=request:accepted=request
        pending+=accepted
        results.append({'mode':mode,'request':request,'accepted':accepted,
                        'fraction':accepted/request if request>0 else 0.0})
    return {'results':results,'pending':pending,'remaining':available-pending}


def debit_sources(charges,pending):
    """Pre-build debit only; excludes charge redistribution/generation/efficiency."""
    charges=tuple(nonnegative(x) for x in charges);pending=nonnegative(pending)
    total=sum(charges);fraction=min(pending/total,1.0) if total>0 else 0.0
    return tuple(q-q*fraction for q in charges)


@dataclass(frozen=True)
class Liquid:
    parts:tuple
    capacity:float
    temperature:float

    def __post_init__(self):
        object.__setattr__(self,'parts',tuple(nonnegative(x) for x in self.parts))
        object.__setattr__(self,'capacity',nonnegative(self.capacity))
        if not math.isfinite(self.temperature):raise ValueError('Require finite temperature')

    @property
    def quantity(self):return sum(self.parts)

    @property
    def overfill_pressure(self):return max(self.quantity-self.capacity,0.0)


def move_liquid(source,destination,request):
    """Model move_content, including an unmodified negative candidate return.

    A negative candidate (e.g. already-overfull destination) moves nothing. The
    native helper returns that candidate; it is not necessarily actual movement.
    This function does not model node-network transfers or heat capacities.
    """
    if source is destination:raise ValueError('Model requires distinct containers')
    if len(source.parts)!=len(destination.parts):raise ValueError('Different species dimensions')
    candidate=min(nonnegative(request),source.quantity,destination.capacity-destination.quantity)
    if candidate<=0:return source,destination,candidate
    fraction=candidate/source.quantity
    moved=tuple(x*fraction for x in source.parts)
    temperature=destination.temperature+(source.temperature-destination.temperature)*(
        candidate/(destination.quantity+candidate))
    return (Liquid(tuple(x-y for x,y in zip(source.parts,moved)),source.capacity,source.temperature),
            Liquid(tuple(x+y for x,y in zip(destination.parts,moved)),destination.capacity,temperature),
            candidate)


def equalize_liquids(contents):
    """Reviewed capacity-weighted equalization, for positive total volume/capacity."""
    contents=tuple(contents)
    if not contents or len({len(x.parts) for x in contents})!=1:raise ValueError('Require same species dimensions')
    capacity=sum(x.capacity for x in contents);quantity=sum(x.quantity for x in contents)
    if capacity<=0 or quantity<=0:raise ValueError('Model requires positive totals')
    parts=tuple(sum(x.parts[i] for x in contents) for i in range(len(contents[0].parts)))
    temperature=sum(x.temperature*x.quantity/quantity for x in contents)
    return tuple(Liquid(tuple(p*x.capacity/capacity for p in parts),x.capacity,temperature) for x in contents)


def loop_iterations(requested,limit=256):
    """Per invocation, not a controller-wide operation allowance."""
    if type(requested) is not int or type(limit) is not int or limit<0:raise ValueError('Require integer loop inputs')
    return max(0,min(requested,limit))


def demo():
    src=Liquid((6,2),10,80);dst=Liquid((0,0),3,20)
    a,b,moved=move_liquid(src,dst,100)
    return {'scope':'Explanatory arithmetic only; no game execution.',
        'scarce_energy_binary_first':consume_sequence(10,[('binary',8),('fractional',8)]),
        'scarce_energy_fractional_first':consume_sequence(10,[('fractional',8),('binary',8)]),
        'next_build_charges':debit_sources([25,75],20),
        'transfer':{'candidate':moved,'source_parts':a.parts,'destination_parts':b.parts,
                    'destination_temperature':b.temperature},
        'nested_256_by_256_body_visits':loop_iterations(1000)*loop_iterations(1000)}


if __name__=='__main__':print(json.dumps(demo(),indent=2))
