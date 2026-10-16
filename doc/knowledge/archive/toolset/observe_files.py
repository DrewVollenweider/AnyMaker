"""Bounded read-only disk observation for live sandbox experiments.

Records metadata changes, preserves scene checkpoint copies and hashes creations.
No game inputs, process access, or source writes.
"""
import archive_paths as ap
import argparse, datetime, hashlib, json, signal, time
from pathlib import Path

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def hashes(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}
def snapshot(root):
    rows={}
    for p in root.rglob('*'):
        if p.is_file():
            s=p.stat(); rows[str(p.relative_to(root))]=(s.st_size,s.st_mtime_ns)
    return rows
def main():
    a=argparse.ArgumentParser();a.add_argument('--seconds',type=int,default=360);a.add_argument('--name',required=True); args=a.parse_args()
    if not 1<=args.seconds<=1800: raise ValueError('Duration must be 1–1800 seconds')
    if Path(args.name).name!=args.name or args.name in ('.','..'): raise ValueError('Use a plain output directory name')
    root=ap.appdata('')
    out=Path(__file__).resolve().parent/'output'/args.name;out.mkdir(exist_ok=False)
    before=hashes(root/'creations'); previous=snapshot(root)
    (out/'baseline.json').write_text(json.dumps({'utc':now(),'files':previous,'creation_hashes':before},indent=2))
    scene=root/'working'/'scene.json'
    (out/'scene-before.json').write_bytes(scene.read_bytes())
    end=time.monotonic()+args.seconds; count=0; stopped=[False]
    signal.signal(signal.SIGINT, lambda *_: stopped.__setitem__(0, True))
    with (out/'events.jsonl').open('x') as f:
        while time.monotonic()<end and not stopped[0]:
            current=snapshot(root)
            for name,stamp in current.items():
                if previous.get(name)!=stamp:
                    f.write(json.dumps({'utc':now(),'path':name,'size':stamp[0],'mtime_ns':stamp[1],
                                        'new':name not in previous})+'\n'); f.flush();count+=1
                    if name=='working\\scene.json':
                        (out/f'scene-event-{count}.json').write_bytes(scene.read_bytes())
            for name in previous.keys()-current.keys():
                f.write(json.dumps({'utc':now(),'path':name,'removed':True})+'\n');f.flush();count+=1
            previous=current; time.sleep(1)
    (out/'scene-after.json').write_bytes(scene.read_bytes())
    after=hashes(root/'creations')
    (out/'result.json').write_text(json.dumps({'utc':now(),'events':count,'stopped_early':stopped[0],'creations_unchanged':before==after,
                                             'creation_hashes_after':after},indent=2))
    print(f'Observation finished: {count} file events; creations unchanged: {before==after}.',flush=True)

if __name__=='__main__': main()
