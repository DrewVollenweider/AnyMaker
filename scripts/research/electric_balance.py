"""One current-build electrical producer redistribution pass.

Explicit finite, non-overfull producer contents and resolved producer references.
The simple wrapper requires distinct contents; indexed variants permit repeated
references. No graph discovery, consumer scheduling, generation, group revisits
or native units. Guards bound this model and do not claim game restrictions.
"""
from dataclasses import dataclass
from powertrain_models import number

VERSION='1.0.0'
DEFAULT_SHARE_RATE=0.001
ALTERNATOR_SHARE_RATE=1.0


@dataclass(frozen=True)
class Store:
    energy: float
    capacity: float
    share_rate: float=DEFAULT_SHARE_RATE

    def __post_init__(self):
        for name in ['energy','capacity','share_rate']:
            object.__setattr__(self,name,number(getattr(self,name)))
        if not 0<=self.energy<=self.capacity:raise ValueError('Require non-overfull nonnegative contents')
        if not 0<=self.share_rate<=1:raise ValueError('Share rate outside bounded model domain')


def _inputs(stores,producer_indices):
    stores=tuple(stores)
    if any(not isinstance(s,Store) for s in stores):raise ValueError('Explicit stores required')
    if len({id(s) for s in stores})!=len(stores):raise ValueError('Shared-content aliases outside model domain')
    indices=tuple(producer_indices)
    if any(type(i) is not int or not 0<=i<len(stores) for i in indices):raise ValueError('Invalid producer reference')
    return stores,indices


def registered_redistribution(stores,producer_indices):
    """One post-build pass, including explicit repeated content references.

    Producer totals are counted per reference; application revisits the current
    shared energy. No conservation guarantee is made for repeated references.
    """
    stores,indices=_inputs(stores,producer_indices)
    energy=[s.energy for s in stores]
    total=number(sum(energy[i] for i in indices));capacity=number(sum(stores[i].capacity for i in indices))
    ratio=total/capacity if capacity>0 else 0.0
    need=tuple(stores[i].capacity*ratio-energy[i] for i in indices)
    released=sum(-d*stores[i].share_rate for i,d in zip(indices,need) if d<0)
    demand=sum(d for d in need if d>=0)
    delta=[]
    for i in indices:
        d=stores[i].capacity*ratio-energy[i]
        q=d*stores[i].share_rate if d<0 else d*released/demand if demand>0 else 0.0
        energy[i]+=q;delta.append(q)
    return dict(initial_total=total,total_capacity=capacity,target_ratio=ratio,
                released=released,demand=demand,delta=tuple(delta),energies=tuple(energy))


def redistribute(stores):
    """Distinct contents, one producer reference each."""
    stores=tuple(stores)
    return registered_redistribution(stores,range(len(stores)))


def debit_registered(stores,producer_indices,previous_available,pending):
    """One pre-build settlement using the cached group budget, then reset.

    Repeated producer references debit the same current contents repeatedly.
    The cached budget is explicit: it need not equal distinct physical stocks.
    """
    stores,indices=_inputs(stores,producer_indices)
    available=number(previous_available);pending=number(pending)
    if min(available,pending)<0:raise ValueError('Nonnegative ordinary accounting required')
    fraction=min(pending/available,1.0) if pending>0 and available>0 else 0.0
    energy=[s.energy for s in stores];delta=[]
    for i in indices:
        moved=energy[i]*fraction;energy[i]-=moved;delta.append(-moved)
    return dict(fraction=fraction,energies=tuple(energy),delta=tuple(delta),
                pending_after=0.0,available_after=0.0,capacity_cache_after=0.0)
