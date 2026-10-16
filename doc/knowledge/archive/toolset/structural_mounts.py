"""Conservative base-grid attachment audit from native attach-test evidence.

Supports cardinal component frames, beam endpoints/axis-aligned beam spans,
and rectangular axis-aligned panels. Unsupported geometry is not certified.
Evidence: output/mount-repair/attach-test.{bin,json,c}.
"""
from itertools import product
from collections import defaultdict, deque
import anymaker as a

DIRS = [(-1,0,0),(1,0,0),(0,-1,0),(0,1,0),(0,0,-1),(0,0,1)]
AXES = [(2,1),(2,1),(0,2),(0,2),(0,1),(0,1)]

def add(p,q): return tuple(p[i]+q[i] for i in range(3))
def rotate(r,p): return tuple(sum(r[3*j+i]*p[j] for j in range(3)) for i in range(3))
def world(c,p): return add(c.get('pos',(0,0,0)),rotate(c.get('rot',a.IDENTITY),p))
def stretch(c,d,p):
    ext=c.get('ext',(0,0,0)); center=d.get('center_stretch',(.5,.5,.5))
    return tuple(p[i]+(ext[i] if p[i]>center[i] else 0) for i in range(3))

def surfaces(c,d):
    result=[]
    for index,s in enumerate(d.get('surfaces',[])):
        direction=s.get('dir',0);u,v=AXES[direction]
        lo=list(s.get('pos',(0,0,0)));hi=lo.copy();size=s.get('size',(1,1))
        hi[u]+=size[0]-1;hi[v]+=size[1]-1
        pts=[world(c,stretch(c,d,p)) for p in product(*zip(lo,hi))]
        low=tuple(min(p[i] for p in pts) for i in range(3));high=tuple(max(p[i] for p in pts) for i in range(3))
        n=rotate(c.get('rot',a.IDENTITY),DIRS[direction])
        result.append({'index':index,'lo':low,'hi':high,'normal':n,'type':s.get('type','')})
    return result

def overlap(lo,hi,p,q): return all(lo[i]<=q[i] and p[i]<=hi[i] for i in range(3))
def endpoint(s,p):
    return (overlap(s['lo'],s['hi'],p,p) or
            overlap(add(s['lo'],s['normal']),add(s['hi'],s['normal']),p,p))

def beam_hit(s,p,q):
    if endpoint(s,p) or endpoint(s,q): return True
    axes=[i for i in range(3) if p[i]!=q[i]]
    if len(axes)!=1:return False
    axis=axes[0];normal=s['normal'];naxis=next(i for i in range(3) if normal[i])
    if axis==naxis or (p[naxis]-s['lo'][naxis])*normal[naxis]!=1:return False
    low=tuple(min(p[i],q[i]) for i in range(3));high=tuple(max(p[i],q[i]) for i in range(3))
    return overlap(add(s['lo'],normal),add(s['hi'],normal),low,high)

def panel_rectangle(points):
    normal=[0,0,0]
    for p,q in zip(points,points[1:]+points[:1]):
        normal[0]+=p[1]*q[2]-p[2]*q[1]
        normal[1]+=p[2]*q[0]-p[0]*q[2]
        normal[2]+=p[0]*q[1]-p[1]*q[0]
    axes=[i for i in range(3) if normal[i]]
    if len(axes)!=1:return None
    axis=axes[0];other=[i for i in range(3) if i!=axis]
    if len({p[axis] for p in points})!=1:return None
    lo=tuple(min(p[i] for p in points) for i in range(3));hi=tuple(max(p[i] for p in points) for i in range(3))
    # Shoelace area must equal bounding rectangle area; no concave panel shortcuts.
    if abs(normal[axis])!=2*(hi[other[0]]-lo[other[0]])*(hi[other[1]]-lo[other[1]]):return None
    return axis,1 if normal[axis]>0 else -1,lo,hi

def audit(doc,cat):
    v=a.vehicles(doc)[0]
    assert len(a.vehicles(doc))==1 and len(v['grids'])==1
    assert not v['grids'][0].get('origin') and not v['grids'][0].get('dir')
    refs=a.references(doc);cs={c['id']:c for c in a.components(v)}
    ss={i:surfaces(c,cat[refs[c['def']]]) for i,c in cs.items()}
    ns={n['id']:tuple(n['pos']) for n in v['nodes']}
    graph=defaultdict(set); contacts=defaultdict(list)
    def join(x,y):graph[x].add(y);graph[y].add(x)
    for e in v['edges']:join(('n',e['n0']),('n',e['n1']))
    for p in v['plates']:
        for n in p['nodes']:join(('p',p['id']),('n',n))
    for i in cs:
        for j in cs:
            if j<=i:continue
            for s in ss[i]:
                if any(s['normal']==tuple(-x for x in t['normal']) and overlap(add(s['lo'],s['normal']),add(s['hi'],s['normal']),t['lo'],t['hi']) for t in ss[j]):
                    join(('c',i),('c',j));contacts[i].append({'component':j,'surface':s['index']});contacts[j].append({'component':i});break
        for e in v['edges']:
            for s in ss[i]:
                if beam_hit(s,ns[e['n0']],ns[e['n1']]):
                    join(('c',i),('n',e['n0']));contacts[i].append({'edge':[e['n0'],e['n1']],'surface':s['index']});break
        for p in v['plates']:
            rect=panel_rectangle([ns[n] for n in p['nodes']])
            if rect is None:continue
            axis,sign,lo,hi=rect
            for s in ss[i]:
                if s['normal'][axis]!=-sign:continue
                if (s['lo'][axis]-lo[axis])*sign!=1:continue
                adjacent_lo=add(s['lo'],s['normal']);adjacent_hi=add(s['hi'],s['normal'])
                if overlap(lo,hi,adjacent_lo,adjacent_hi):
                    join(('c',i),('p',p['id']));contacts[i].append({'plate':p['id'],'surface':s['index']});break
    seen=set();islands=[]
    for x in list(graph)+[('c',i) for i in cs]:
        if x in seen:continue
        queue=[x];seen.add(x);group=[]
        while queue:
            y=queue.pop();group.append(y)
            for z in graph[y]-seen:seen.add(z);queue.append(z)
        islands.append(group)
    islands.sort(key=len,reverse=True);main=set(islands[0])
    disconnected=[{'id':i,'definition':refs[c['def']],'pos':c['pos'],'contacts':contacts[i]} for i,c in cs.items() if ('c',i) not in main]
    return {'islands':[{'components':sorted(x[1] for x in g if x[0]=='c'),'nodes':sum(x[0]=='n' for x in g)} for g in islands],
            'disconnected_components':disconnected,'contacts':dict(contacts),
            'status':'Conservative static base-grid audit; not a runtime physics test.'}
