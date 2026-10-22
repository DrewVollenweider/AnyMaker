"""Selected liquid post-build group visit from build 26113663.

Resolved ports, cached heads and distinct contents are explicit inputs. No
topology, null contents, shared-content aliases, initial overfill, group revisit
cadence, pumps, geometry or native solver is modeled. Guards define this tool's
domain, not game restrictions. Capacity is not guaranteed after the visit.
"""
from dataclasses import dataclass
from powertrain_models import number,positive

VERSION='1.0.0'
HEAD_FACTOR=2.0
TRANSFER_FACTOR=0.01


@dataclass(frozen=True)
class Port:
    head: float
    amounts: tuple
    capacity: float
    temperature: float=20.0
    expandable: bool=False

    def __post_init__(self):
        object.__setattr__(self,'head',number(self.head))
        object.__setattr__(self,'temperature',number(self.temperature))
        object.__setattr__(self,'capacity',positive(self.capacity))
        amounts=tuple(map(number,self.amounts))
        if len(amounts)!=4 or any(x<0 for x in amounts):raise ValueError('Four nonnegative model species required')
        if sum(amounts)>self.capacity:raise ValueError('Initially overfull state outside model domain')
        if type(self.expandable) is not bool:raise ValueError('Boolean expandable flag required')
        object.__setattr__(self,'amounts',amounts)


def visit(ports):
    ports=tuple(ports)
    if any(not isinstance(p,Port) for p in ports):raise ValueError('Explicit model ports required')
    if len({id(p) for p in ports})!=len(ports):raise ValueError('Shared contents outside model domain')
    state=[dict(amounts=list(p.amounts),volume=sum(p.amounts),capacity=p.capacity,
                temperature=p.temperature,flow=0.0) for p in ports]
    order=tuple(sorted(range(len(ports)),key=lambda i:ports[i].head));moves=[]
    for offset,dest in enumerate(order):
        dst=state[dest];candidates=[]
        # Candidates are evaluated together against the same current free room.
        for src in order[offset+1:]:
            q=min((ports[src].head-ports[dest].head)*HEAD_FACTOR*TRANSFER_FACTOR,state[src]['volume'])
            if not ports[dest].expandable:q=min(q,dst['capacity']-dst['volume'])
            candidates.append((src,q))
        if sum(q for _,q in candidates)<=0:continue
        for src,q in candidates:
            s=state[src]
            if s['volume']<=0 or q==0:continue
            fraction=q/s['volume'];moved=s['volume']*fraction
            dst['temperature']+=(s['temperature']-dst['temperature'])*moved/(dst['volume']+moved)
            dst['volume']+=moved;s['volume']-=moved
            dst['flow']+=q;s['flow']-=q
            for k in range(4):
                species=s['amounts'][k]*fraction
                dst['amounts'][k]+=species;s['amounts'][k]-=species
            moves.append(dict(source=src,destination=dest,amount=moved))
    return dict(ports=state,order=order,moves=moves)
