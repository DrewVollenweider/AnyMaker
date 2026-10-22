"""Compare archived reviewed GCL instructions/reads with a new indexed build.

This checks selected local bytes and operand metadata only. It does not copy
decompilations into a new reader or prove unchanged callees, bindings, globals,
address-taken data, reflection, native code, solver behavior or game mechanics.
"""
import argparse
from collections import Counter,defaultdict
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3

from baseline import sha,write
from gcl_index import record

VERSION = '1.0.0'


def _span(raw,start,size):
    if type(start) is not int or type(size) is not int or size<=0 or not 0<=start<start+size<=len(raw):
        raise ValueError('Unbounded source span')
    return raw[start:start+size]


def compare_function(old_raw,new_raw,old,new,assembly,evidence):
    """Both records must describe the same exact signature; verify before mapping."""
    if old['signature']!=new['signature'] or evidence['signature']!=old['signature']:
        raise ValueError('Function signature mismatch')
    for raw,r in [(old_raw,old),(new_raw,new)]:
        if hashlib.sha256(_span(raw,r['code_offset'],r['code_size'])).hexdigest()!=r['code_sha256']:
            raise ValueError('Function source/hash mismatch')
    if evidence['code_offset']!=old['code_offset'] or evidence['code_sha256']!=old['code_sha256']:
        raise ValueError('Reader identity mismatch')
    instructions=[];covered=set();last=old['code_offset']
    for line in assembly.splitlines():
        if not line or line.startswith('#'):continue
        parts=line.split('\t',2)
        if len(parts)!=3:raise ValueError('Malformed assembly row')
        at=int(parts[0],16);data=bytes.fromhex(parts[1]);end=at+len(data)
        if not data or at<last or not old['code_offset']<=at<end<=old['code_offset']+old['code_size']:
            raise ValueError('Instruction outside function or overlapping')
        if _span(old_raw,at,len(data))!=data:raise ValueError('Archived instruction bytes mismatch')
        instructions.append((at-old['code_offset'],data));covered.update(range(at-old['code_offset'],end-old['code_offset']));last=end
    if not instructions:raise ValueError('No reviewed instructions')
    reads=[]
    for r in evidence['embedded_reads']:
        at,width=r['offset'],r['width'];data=bytes.fromhex(r['bytes'])
        if len(data)!=width or not old['code_offset']<=at<at+width<=old['code_offset']+old['code_size']:
            raise ValueError('Direct read outside function')
        if _span(old_raw,at,width)!=data:raise ValueError('Archived direct-read bytes mismatch')
        reads.append((at-old['code_offset'],data));covered.update(range(at-old['code_offset'],at-old['code_offset']+width))
    result=dict(signature=old['signature'],old_offset=old['code_offset'],new_offset=new['code_offset'],
                old_code_sha256=old['code_sha256'],new_code_sha256=new['code_sha256'],
                whole_code_equal=(old['code_size'],old['code_sha256'])==(new['code_size'],new['code_sha256']),
                archived_instructions_checked=len(instructions),archived_direct_reads_checked=len(reads),
                references_equal=old['references']==new['references'])
    if old['code_size']!=new['code_size']:
        return dict(result,status='code_size_changed',new_local_checks_performed=False)
    changed_instructions=[rel for rel,data in instructions if _span(new_raw,new['code_offset']+rel,len(data))!=data]
    changed_reads=[rel for rel,data in reads if _span(new_raw,new['code_offset']+rel,len(data))!=data]
    a=_span(old_raw,old['code_offset'],old['code_size']);b=_span(new_raw,new['code_offset'],new['code_size'])
    result.update(new_local_checks_performed=True,changed_instruction_offsets=changed_instructions,
                  changed_direct_read_offsets=changed_reads,
                  unclassified_changed_bytes=sum(x!=y and i not in covered for i,(x,y) in enumerate(zip(a,b))))
    status=('instruction_bytes_changed' if changed_instructions else 'direct_reads_changed' if changed_reads
            else 'references_changed' if not result['references_equal'] else 'local_checks_match')
    return dict(result,status=status)


def _index(path,raw):
    with closing(sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        expected=json.loads(db.execute("SELECT value FROM provenance WHERE key='source_sha256'").fetchone()[0])
        if expected!=hashlib.sha256(raw).hexdigest():raise ValueError('Index/source mismatch')
        return [json.loads(j) for j, in db.execute('SELECT record FROM functions')]


def compare(old_source,old_index,old_reader,new_source,new_index,output):
    if output.exists():raise FileExistsError(output)
    old_raw,new_raw=old_source.read_bytes(),new_source.read_bytes()
    old_records={r['code_offset']:r for r in _index(old_index,old_raw)}
    new_records=defaultdict(list)
    for r in _index(new_index,new_raw):new_records[r['signature']].append(r)
    rows=[]
    with closing(sqlite3.connect(old_reader.resolve().as_uri()+'?mode=ro',uri=True)) as db:
        complete=db.execute("SELECT value FROM metadata WHERE key='complete'").fetchone()
        provenance=json.loads(db.execute("SELECT value FROM metadata WHERE key='provenance'").fetchone()[0])
        if complete!=('true',) or provenance['source_sha256']!=hashlib.sha256(old_raw).hexdigest():
            raise ValueError('Reader/source mismatch or incomplete reader')
        for at,signature,assembly,j in db.execute('SELECT code_offset,signature,assembly,evidence FROM functions'):
            old=old_records[at];old_checked=record(old_raw,old['signature_offset'])
            if old_checked['signature']!=signature or any(old_checked[k]!=old[k] for k in ['code_offset','code_size','code_sha256','references']):
                raise ValueError('Archived record mismatch')
            candidates=new_records[signature]
            if len(candidates)!=1:
                # Still validate the archived evidence instead of silently skipping it.
                compare_function(old_raw,old_raw,old,old,assembly,json.loads(j))
                rows.append(dict(signature=signature,old_offset=at,status='missing' if not candidates else 'ambiguous'))
                continue
            new=candidates[0];checked=record(new_raw,new['signature_offset'])
            if any(checked[k]!=new[k] for k in ['signature','code_offset','code_size','code_sha256','references']):
                raise ValueError('Current record mismatch')
            rows.append(compare_function(old_raw,new_raw,old,new,assembly,json.loads(j)))
    result=dict(schema=1,tool_version=VERSION,old_source_sha256=hashlib.sha256(old_raw).hexdigest(),
                new_source_sha256=hashlib.sha256(new_raw).hexdigest(),counts=dict(Counter(r['status'] for r in rows)),
                functions=rows,limits=__doc__.strip())
    if sha(old_source)!=result['old_source_sha256'] or sha(new_source)!=result['new_source_sha256']:
        raise ValueError('Source changed during comparison')
    write(output,result);print(json.dumps(result['counts']))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['old_source','old_index','old_reader','new_source','new_index','output']:p.add_argument(name,type=Path)
    a=p.parse_args();compare(a.old_source,a.old_index,a.old_reader,a.new_source,a.new_index,a.output)
