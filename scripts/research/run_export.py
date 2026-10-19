"""Bounded Ghidra integration, adapted from the archived portable launcher.

Requires an existing Ghidra/JDK runtime; downloads and game execution are absent.
Project root must be a new directory with a Ghidra-compatible path (no braces or
dot-prefixed path elements). Analysis is restricted to selected indexed records.
"""
import argparse,json,os,subprocess
from pathlib import Path
from baseline import resources,sha,write
from export_plan import plan
from check_exports import check

def run(source,database,out,runtime,project_root,terms):
 runtime=runtime.resolve();out=out.resolve();project_root=project_root.resolve()
 if project_root.exists():raise FileExistsError(project_root)
 if any(p.startswith('.') or any(c in p for c in '{}') for p in project_root.parts):
  raise ValueError('Use a Ghidra-compatible project path, e.g. a plain temporary directory')
 budget=resources(out.parent)
 if budget.get('memory_available_bytes',10**10)<4*1024**3:raise MemoryError('Require 4 GiB available')
 ghidras=list((runtime/'ghidra').glob('ghidra_*'))
 jdks=list((runtime/'jdk').glob('*/bin/java.exe'))
 if len(ghidras)!=1 or len(jdks)!=1:raise ValueError('Ambiguous/missing portable Ghidra or JDK')
 ghidra,java=ghidras[0],jdks[0]
 plan(source,database,out,terms)
 project_root.mkdir(parents=True)
 state=out/'runtime-state';state.mkdir()
 args=[str(java),'-Xmx2G','-Xshare:off','-XX:ActiveProcessorCount=2',
  '--enable-native-access=ALL-UNNAMED',
  '-Djava.system.class.loader=ghidra.GhidraClassLoader','-Dfile.encoding=UTF8',
  '-Dsun.java2d.d3d=false','-Dlog4j.skipJansi=true',f'-Duser.home={state}',
  f'-Dapplication.settingsdir={state}/settings',f'-Dapplication.cachedir={state}/cache',
  f'-Dapplication.tempdir={state}/tmp','-Djavax.xml.accessExternalDTD=',
  '-Djavax.xml.accessExternalSchema=','-Djavax.xml.accessExternalStylesheet=',
  '-cp',str(ghidra/'Ghidra/Framework/Utility/lib/Utility.jar'),'ghidra.Ghidra',
  'ghidra.app.util.headless.AnalyzeHeadless',str(project_root),'Selected',
  '-import',str(source.resolve()),'-loader','BinaryLoader','-processor','x86:LE:64:default',
  '-cspec','windows','-loader-baseAddr','0','-noanalysis','-max-cpu','1',
  '-scriptPath',str(Path(__file__).resolve().parent),'-postScript','ExportResearch.java',
  str(out/'plan.tsv'),str(out/'ghidra')]
 with (out/'ghidra.log').open('x',encoding='utf-8') as log:
  result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,
   creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
 if result.returncode:raise RuntimeError('Ghidra failed; inspect output log')
 # Headless Ghidra may exit zero after a script error. Validate actual outputs.
 check(source,out/'export-check.json',[out])
 write(out/'run.json',{'tool_sha256':sha(Path(__file__)),
  'export_script_sha256':sha(Path(__file__).with_name('ExportResearch.java')),
  'source_sha256':sha(source),'resources_before':budget,'java_version':subprocess.check_output([str(java),'--version'],text=True),
  'ghidra_properties_sha256':sha(ghidra/'Ghidra/application.properties'),
  'heap_limit':'2GiB','headless_workers':1,'automatic_analysis':False,
  'limits':'Raw imported copy only; unresolved pointers/types preserved; no game execution.'})

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for name in ('source','database','output','runtime','project_root'):p.add_argument(name,type=Path)
 p.add_argument('terms',nargs='+');a=p.parse_args()
 run(a.source,a.database,a.output,a.runtime,a.project_root,a.terms)
