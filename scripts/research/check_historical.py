"""Compare historical evidence ranges and relocate exact signatures on one build."""
import argparse
from collections import Counter
import hashlib,json,sqlite3
from pathlib import Path
from baseline import sha,write

def number(x):return int(x,0) if isinstance(x,str) else int(x)

def check(source,database,evidence,out):
 db=sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)
 expected=json.loads(db.execute("SELECT value FROM provenance WHERE key='source_sha256'").fetchone()[0])
 if sha(source)!=expected:raise ValueError('Index/source mismatch')
 b=source.read_bytes();reports=[]
 for path in sorted(evidence.glob('*.json')):
  v=json.loads(path.read_text(encoding='utf-8')); records=[]
  for r in v.get('functions',[]):
   if not all(k in r for k in ('signature','codeOffset','codeSize','codeSha256')):continue
   offset,size=number(r['codeOffset']),number(r['codeSize'])
   old_matches=hashlib.sha256(b[offset:offset+size]).hexdigest()==r['codeSha256']
   found=db.execute('SELECT record FROM functions WHERE signature=?',(r['signature'],)).fetchall()
   current=json.loads(found[0][0]) if len(found)==1 else None
   records.append({'signature':r['signature'],'historical_offset':offset,'historical_bytes_match_at_old_offset':old_matches,
     'relocation_status':'unique-record' if current else 'ambiguous' if found else 'not-indexed',
     'current_code_offset':current['code_offset'] if current else None,
     'current_code_size':current['code_size'] if current else None,
     'current_code_sha256':current['code_sha256'] if current else None,
     'same_code_hash_after_relocation':current['code_sha256']==r['codeSha256'] if current else None})
  reports.append({'evidence':path.name,'evidence_sha256':sha(path),
    'historical_gcl_sha256':v.get('source',{}).get('sha256'),
    'same_build':v.get('source',{}).get('sha256')==expected,
    'records':records})
 allrows=[r for x in reports for r in x['records']]
 report={'schema':1,'source_sha256':expected,'tool_sha256':sha(Path(__file__)),
  'evidence_files':len(reports),'range_checks':len(allrows),
  'old_offsets_matching':sum(r['historical_bytes_match_at_old_offset'] for r in allrows),
  'relocation_status':dict(Counter(r['relocation_status'] for r in allrows)),
  'same_code_hash_after_relocation':sum(r['same_code_hash_after_relocation'] is True for r in allrows),
  'reports':reports,'limits':'Byte equality is narrower than semantic equality. Relocated records require renewed caller/type/constant validation before carrying conclusions forward.'}
 write(out,report)
 print(json.dumps({k:v for k,v in report.items() if k!='reports'},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('source','database','evidence','output'):p.add_argument(name,type=Path)
 a=p.parse_args();check(a.source,a.database,a.evidence,a.output)
