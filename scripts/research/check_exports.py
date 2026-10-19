"""Verify exported instruction bytes against the exact indexed GCL snapshot."""
import argparse,hashlib,json
from pathlib import Path
from baseline import sha,write

def check(source,output,folders):
 b=source.read_bytes();digest=hashlib.sha256(b).hexdigest();results=[]
 for folder in folders:
  meta=json.loads((folder/'records.json').read_text(encoding='utf-8'))
  if meta['source_sha256']!=digest:raise ValueError('Export/source build mismatch')
  for r in meta['records']:
   name=r['export_name'];assembly=folder/'ghidra'/(name+'.asm.tsv');c=folder/'ghidra'/(name+'.c')
   previous_end=r['code_offset'];covered=0;count=0
   for line in assembly.read_text(encoding='utf-8').splitlines():
    if line.startswith('#'):continue
    address,hexbytes,instruction=line.split('\t',2)
    offset=int(address,16);raw=bytes.fromhex(hexbytes)
    if offset<previous_end or not raw or offset+len(raw)>r['code_offset']+r['code_size']:
     raise ValueError('Instruction outside record or overlapping: '+name)
    if b[offset:offset+len(raw)]!=raw:raise ValueError('Instruction bytes differ: '+name)
    previous_end=offset+len(raw);covered+=len(raw);count+=1
   pseudo=c.read_text(encoding='utf-8')
   if pseudo.startswith('ERROR:'):raise ValueError(pseudo)
   results.append({'signature':r['signature'],'code_offset':r['code_offset'],
    'code_size':r['code_size'],'code_sha256':r['code_sha256'],
    'instructions_exported':count,'instruction_bytes_checked':covered,
    'assembly_sha256':sha(assembly),'pseudocode_sha256':sha(c),
    'export_name':name})
 report={'schema':1,'source_sha256':digest,'tool_sha256':sha(Path(__file__)),
  'functions_exported':len(results),'instructions_byte_checked':sum(r['instructions_exported'] for r in results),
  'instruction_bytes_checked':sum(r['instruction_bytes_checked'] for r in results),'records':results,
  'limits':'Checks exact bytes, bounds and export success. Does not prove recovered types, semantics, complete CFG coverage, or runtime behavior.'}
 write(output,report);print(json.dumps({k:v for k,v in report.items() if k!='records'},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('exports',nargs='+',type=Path)
 a=p.parse_args();check(a.source,a.output,a.exports)
