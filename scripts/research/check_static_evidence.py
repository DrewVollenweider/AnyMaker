"""Recheck selected structured records and typed constants against one exact GCL."""
import argparse,json,struct
from pathlib import Path
from baseline import sha
from gcl_index import record

def check(source,records,constants):
 digest=sha(source);b=source.read_bytes()
 rr=json.loads(records.read_text(encoding='utf-8'))
 cc=json.loads(constants.read_text(encoding='utf-8'))
 if rr['source_sha256']!=digest or cc['source_sha256']!=digest:
  raise ValueError('Evidence/source build mismatch')
 for expected in rr['records']:
  actual=record(b,expected['signature_offset'])
  for key in ('signature','code_offset','code_size','serialized_size','code_sha256','references'):
   if actual[key]!=expected[key]:raise ValueError('Record differs: '+key)
 for c in cc['constants']:
  n=struct.calcsize(c['format']);raw=b[c['file_offset']:c['file_offset']+n]
  if raw.hex()!=c['bytes_hex'] or struct.unpack(c['format'],raw)[0]!=c['value']:
   raise ValueError('Constant differs: '+c['label'])
 print(json.dumps({'source_sha256':digest,'function_records_checked':len(rr['records']),
  'typed_constants_checked':len(cc['constants']),'status':'exact static evidence matches; runtime untested'},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('source','records','constants'):p.add_argument(name,type=Path)
 a=p.parse_args();check(a.source,a.records,a.constants)
