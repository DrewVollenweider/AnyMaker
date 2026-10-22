"""Selected belt-link walk from build 26113663, after start-link resolution.

Explicit endpoint tokens replace native node IDs. The caller must already have
resolved the ordered start link and endpoint using component/surface geometry.
No creation parser, geometry, belt tension, torque solver or native validation
is modeled. Non-self links are this tool's domain, not a game placement rule.
"""

VERSION='1.0.0'


def walk(links,start_link=0,start_side=0):
    """Return acceptance, reason and the visited endpoint sequence.

    A dead end after the first link is accepted by the source's two-entry
    exception, even with other links behind the starting endpoint. The native
    caller's output vector is assumed initially empty, as in the roller tick.
    Acceptance must not be interpreted as proof of an enclosed track shape.
    """
    links=tuple(tuple(edge) for edge in links)
    if any(len(edge)!=2 for edge in links):raise ValueError('Two endpoints per model link required')
    for a,b in links:
        hash(a);hash(b)
        if a==b:raise ValueError('Self-links outside this model domain')
    if type(start_link) is not int or not 0<=start_link<len(links):raise ValueError('Invalid start link')
    if type(start_side) is not int or start_side not in (0,1):raise ValueError('Invalid start endpoint')
    current=start_link;free_side=1-start_side
    nodes=[links[current][start_side],links[current][free_side]]
    visited=[current];states=set()
    while True:
        state=(current,free_side)
        if state in states:raise ValueError('Walk repeated without returning to start link')
        states.add(state);endpoint=links[current][free_side]
        candidates=[]
        for i,(a,b) in enumerate(links):
            if i==current:continue
            if a==endpoint:candidates.append((i,1))
            elif b==endpoint:candidates.append((i,0))
        if len(candidates)!=1:
            accepted=not candidates and len(nodes)==2
            return dict(accepted=accepted,reason='two_entry_exception' if accepted else 'open_end' if not candidates else 'branch',
                        nodes=tuple(nodes),links=tuple(visited),incident_other_links=len(candidates))
        nxt,free_side=candidates[0]
        if nxt==start_link:
            return dict(accepted=True,reason='closed_return',nodes=tuple(nodes),links=tuple(visited),incident_other_links=1)
        current=nxt;visited.append(current);nodes.append(links[current][free_side])
