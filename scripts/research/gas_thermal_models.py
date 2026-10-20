"""Selected gas and temperature arithmetic; not a complete network simulator.

Build 25904830. Pair and vector gas equalization intentionally differ in
temperature handling. These ordinary-state guards are model choices, not
native validation. No ideal-gas law, SI heat capacity or pressure unit assumed.
"""
from dataclasses import dataclass
from powertrain_models import number,unit

VERSION='1.0.0'


@dataclass(frozen=True)
class Content:
    parts:tuple
    capacity:float
    temperature:float

    def __post_init__(self):
        if not self.parts:raise ValueError('At least one species required')
        parts=tuple(number(x) for x in self.parts);cap=number(self.capacity)
        if min(parts)<0 or cap<0:raise ValueError('Negative ordinary content outside model domain')
        object.__setattr__(self,'parts',parts);object.__setattr__(self,'capacity',cap)
        object.__setattr__(self,'temperature',number(self.temperature))

    @property
    def quantity(self):return sum(self.parts)

    @property
    def pressure(self):return self.quantity/self.capacity if self.capacity>0 else 0.0


def move_gas(source,destination,requested):
    """Return changed contents and actual model amount; native method is void.

    Source quantity caps movement; destination capacity does not cap gas here.
    Source temperature remains; destination mixes by incoming quantity.
    """
    if len(source.parts)!=len(destination.parts):raise ValueError('Species dimensions differ')
    requested=number(requested);amount=min(requested,source.quantity)
    if amount<=0:return source,destination,0.0
    fraction=amount/source.quantity
    moved=tuple(x*fraction for x in source.parts)
    weight=amount/(destination.quantity+amount)
    temperature=destination.temperature+(source.temperature-destination.temperature)*weight
    return (Content(tuple(x-y for x,y in zip(source.parts,moved)),source.capacity,source.temperature),
            Content(tuple(x+y for x,y in zip(destination.parts,moved)),destination.capacity,temperature),amount)


def equalize_gas(contents,*,pair_overload=False):
    """Capacity-weight species; pair overload preserves each temperature.

    Vector overload assigns one quantity-weighted temperature. Empty-total
    native constructor/default details are excluded from this model domain.
    """
    contents=tuple(contents)
    if not contents or len({len(x.parts) for x in contents})!=1:raise ValueError('Matching species required')
    if type(pair_overload) is not bool:raise ValueError('Boolean overload selector required')
    if pair_overload and len(contents)!=2:raise ValueError('Pair overload needs two contents')
    capacity=sum(x.capacity for x in contents);quantity=sum(x.quantity for x in contents)
    if capacity<=0 or quantity<=0:raise ValueError('Model requires positive totals')
    parts=tuple(sum(x.parts[i] for x in contents) for i in range(len(contents[0].parts)))
    mean=sum(x.temperature*x.quantity/quantity for x in contents)
    return tuple(Content(tuple(p*x.capacity/capacity for p in parts),x.capacity,
                         x.temperature if pair_overload else mean) for x in contents)


def blend_temperatures(quantity_a,temp_a,quantity_b,temp_b,factor):
    """Shared gas/gas, gas/liquid and liquid/liquid wrapper arithmetic.

    Quantity-weighted temperature only; no differing material heat capacity.
    Factor domain 0..1 is a model guard; the native helper does not clamp it.
    """
    a,b=number(quantity_a),number(quantity_b);ta,tb=number(temp_a),number(temp_b);f=unit(factor)
    if a<0 or b<0:raise ValueError('Negative ordinary quantity outside model domain')
    if a+b<=0:return ta,tb
    mean=ta+(tb-ta)*b/(a+b)
    return ta+(mean-ta)*f,tb+(mean-tb)*f
