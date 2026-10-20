"""Recheck selected published offline evidence against a local matching GCL copy.

Checks record identity, code hashes, constant bytes/values, literal strings and
selected instruction bytes. It does not re-prove a prose interpretation of C.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from baseline import write,sha
from gcl_index import record


def check(source,evidence,output=None):
    b=source.read_bytes();e=json.loads(evidence.read_text(encoding='utf-8'))
    if e.get('schema')!=1:raise ValueError('Unknown evidence schema')
    if hashlib.sha256(b).hexdigest()!=e['source_sha256']:raise ValueError('Evidence/source build mismatch')
    records={}
    for f in e['functions']:
        r=record(b,f['signature_offset'])
        for k in ['signature','code_offset','code_size','code_sha256']:
            if r[k]!=f[k]:raise ValueError('Changed function '+f['signature'])
        records[r['code_offset']]=r
    for c in e['constants']:
        r=records[c['function_offset']];fmt={'f64':'<d','u8':'<B','s32':'<i'}[c['format']]
        width=struct.calcsize(fmt);at=c['offset']
        if not r['code_offset']<=at<at+width<=r['code_offset']+r['code_size']:raise ValueError('Constant out of range')
        raw=b[at:at+width]
        if raw.hex()!=c['bytes'] or struct.unpack(fmt,raw)[0]!=c['value']:raise ValueError('Changed constant '+c['name'])
    for s in e['strings']:
        r=records[s['function_offset']];raw=s['text'].encode('ascii')+b'\0';at=s['offset']
        if not r['code_offset']<=at<at+len(raw)<=r['code_offset']+r['code_size']:raise ValueError('String out of range')
        if b[at:at+len(raw)]!=raw:raise ValueError('Changed literal '+s['text'])
    for i in e['call_examples']:
        r=records[i['function_offset']];raw=bytes.fromhex(i['bytes']);at=i['instruction']
        if not raw or not r['code_offset']<=at<at+len(raw)<=r['code_offset']+r['code_size']:raise ValueError('Call instruction out of range')
        if b[at:at+len(raw)]!=raw:raise ValueError('Changed call instruction')
        slot=i['slot_address']-r['code_offset']
        if not any(x['slot_offset']==slot and x['symbol']==i['symbol'] and x['kind']==i['kind'] for x in r['references']):
            raise ValueError('Call-example operand metadata mismatch')
    report={'schema':1,'source_sha256':e['source_sha256'],'tool_sha256':sha(Path(__file__)),
            'function_records_checked':len(records),'constants_checked':len(e['constants']),
            'strings_checked':len(e['strings']),'call_instruction_examples_checked':len(e['call_examples']),
            'limitations':'Exact static identities/bytes only; virtual target binding and prose semantics are not proven by this checker.'}
    if output:write(output,report)
    print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('evidence',type=Path)
    p.add_argument('--output',type=Path);a=p.parse_args();check(a.source,a.evidence,a.output)
