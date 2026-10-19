"""Compare installation hashes and optional versioned definition/function indexes."""
import argparse,json,sqlite3
from pathlib import Path
from baseline import write

def mapping_diff(a,b):
 canonical=lambda value:json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
 equal=lambda key:canonical(a[key])==canonical(b[key])
 return {'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),
         'changed':[k for k in sorted(a.keys()&b.keys()) if not equal(k)],
         'unchanged':sum(equal(k) for k in a.keys()&b.keys())}

def definitions(dbpath):
 db=sqlite3.connect(dbpath.resolve().as_uri()+'?mode=ro',uri=True)
 return {source+'#'+ident:json.loads(raw) for source,ident,raw in db.execute('SELECT source,id,json FROM definitions')}

def functions(dbpath):
 db=sqlite3.connect(dbpath.resolve().as_uri()+'?mode=ro',uri=True)
 rows={}
 for (raw,) in db.execute('SELECT record FROM functions'):
  r=json.loads(raw)
  rows.setdefault(r['signature'],[]).append((r['code_sha256'],r['code_size']))
 return {k:sorted(v) for k,v in rows.items()}

def compare(old,new,out,old_definitions=None,new_definitions=None,old_functions=None,new_functions=None):
 a=json.loads(old.read_text(encoding='utf-8'));b=json.loads(new.read_text(encoding='utf-8'))
 result={'schema':1,'old_build':a['steam'],'new_build':b['steam'],
   'files':mapping_diff({r['path']:(r['sha256'],r['bytes']) for r in a['files']},
                       {r['path']:(r['sha256'],r['bytes']) for r in b['files']}),
   'limits':'Semantic JSON changes preserve missing versus present fields. Same machine-code bytes do not establish unchanged bindings, constants, callers or runtime behavior.'}
 if bool(old_definitions)!=bool(new_definitions) or bool(old_functions)!=bool(new_functions):
  raise ValueError('Index comparisons require both old and new inputs')
 if old_definitions:
  x,y=definitions(old_definitions),definitions(new_definitions)
  result['definitions']=mapping_diff(x,y)
  result['definition_fields']={k:mapping_diff(x[k],y[k]) for k in result['definitions']['changed']}
 if old_functions:
  result['function_record_hashes']=mapping_diff(functions(old_functions),functions(new_functions))
 write(out,result)
 print(json.dumps({k:v for k,v in result.items() if k not in ('definition_fields',)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('old','new','output'):p.add_argument(name,type=Path)
 for name in ('old-definitions','new-definitions','old-functions','new-functions'):p.add_argument('--'+name,type=Path)
 a=p.parse_args();compare(a.old,a.new,a.output,a.old_definitions,a.new_definitions,a.old_functions,a.new_functions)
