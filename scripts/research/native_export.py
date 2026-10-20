"""Bounded static Ghidra export of an isolated x64 PE, never native execution.

Uses exception-directory ranges or explicitly supplied manual spans. A manual
span is not a recovered function boundary. No signature binding is inferred.
Requires an existing Ghidra/JDK runtime; no downloads or installation changes.
"""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
from baseline import resources,sha,write
from native_image import Image

VERSION='1.0.0'


def select(raw,selections):
    image=Image(raw);rows=[]
    if not 1<=len(selections)<=64:raise ValueError('Select 1..64 bounded native spans')
    for selection in selections:
        if ':' in selection:
            parts=selection.split(':')
            if len(parts)!=2:raise ValueError('Manual span requires begin:end RVA')
            begin,end=(int(x,0) for x in parts);kind='manual_span_not_recovered_boundary';unwind=None
        else:
            found=image.containing_runtime_ranges(int(selection,0))
            if len(found)!=1:raise ValueError('Missing/ambiguous runtime-function range; specify a reviewed manual span explicitly')
            row=found[0];begin,end,unwind=row['begin_rva'],row['end_rva'],row['unwind_rva']
            kind='exception_directory_range_not_complete_function_inventory'
        if not 0<end-begin<=65536:raise ValueError('Native span must be 1..65536 bytes')
        offset=image.file_offset(begin,end-begin)
        if not image.section_for_rva(begin)['flags']&0x20000000:raise ValueError('Native span outside executable section')
        rows.append(dict(begin_rva=begin,end_rva=end,va=image.image_base+begin,file_offset=offset,
                         size=end-begin,unwind_rva=unwind,bound_kind=kind,name=f'native_{begin:x}',
                         span_sha256=hashlib.sha256(raw[offset:offset+end-begin]).hexdigest()))
    ordered=sorted(rows,key=lambda x:x['begin_rva'])
    if any(a['end_rva']>b['begin_rva'] for a,b in zip(ordered,ordered[1:])):raise ValueError('Selected native spans overlap')
    return dict(schema=1,tool_version=VERSION,source_sha256=hashlib.sha256(raw).hexdigest(),image_base=image.image_base,
                spans=rows,limits='Selected static spans only. Manual bounds, native signatures, ABI and runtime dispatch require separate evidence.')


def check(source,plan,output):
    raw=source.read_bytes();image=Image(raw)
    if plan.get('schema')!=1 or plan.get('source_sha256')!=hashlib.sha256(raw).hexdigest() or plan.get('image_base')!=image.image_base:
        raise ValueError('Native export/source identity mismatch')
    selections=[f"{r['begin_rva']}:{r['end_rva']}" for r in plan['spans']]
    bounded=select(raw,selections)['spans'];instructions=total=0
    for row,expected in zip(plan['spans'],bounded):
        for key in ['begin_rva','end_rva','va','file_offset','size','name','span_sha256']:
            if row[key]!=expected[key]:raise ValueError('Changed native selected range')
        path=output/row['name']
        c=path.with_suffix('.c').read_text(encoding='utf-8')
        if not c.strip() or c.startswith('ERROR:'):raise ValueError('Native decompilation did not complete')
        facts=json.loads(path.with_suffix('.facts.json').read_text(encoding='utf-8'))
        if facts.get('schema')!=1 or not facts.get('decompile_completed') or facts.get('code_offset')!=row['va'] or facts.get('code_size')!=row['size'] or facts.get('export_name')!=row['name']:
            raise ValueError('Native facts/plan identity mismatch')
        asm=[]
        for line in path.with_suffix('.asm.tsv').read_text(encoding='utf-8').splitlines():
            if not line or line.startswith('#'):continue
            parts=line.split('\t',2)
            if len(parts)!=3:raise ValueError('Malformed native assembly line')
            asm.append((int(parts[0],16),parts[1]))
        observed=[];end_address=row['va']
        for ins in facts['instructions']:
            address=int(ins['address']);data=bytes.fromhex(ins['bytes'])
            if not data or address<end_address or not row['va']<=address<address+len(data)<=row['va']+row['size']:
                raise ValueError('Native instruction outside selected span or overlapping')
            offset=image.file_offset(address-image.image_base,len(data))
            if raw[offset:offset+len(data)]!=data:raise ValueError('Native instruction bytes changed')
            observed.append((address,data.hex()));end_address=address+len(data)
            instructions+=1;total+=len(data)
        if not observed or asm!=observed:raise ValueError('Native facts/assembly disagreement')
    if sha(source)!=plan['source_sha256']:raise ValueError('Native source changed during checking')
    return dict(schema=1,source_sha256=plan['source_sha256'],spans=len(plan['spans']),
                instructions_byte_checked=instructions,instruction_bytes_checked=total,
                limits='Exact selected bytes/bounds and artifact consistency only; not a complete CFG, ABI, native binding or semantic proof.')


def run(source,output,runtime,project,selections):
    source=source.resolve();output=output.resolve();runtime=runtime.resolve();project=project.resolve()
    if output.exists() or project.exists():raise FileExistsError('Use new output and project directories')
    if any(p.startswith('.') or any(c in p for c in '{}') for p in project.parts):raise ValueError('Use a plain Ghidra-compatible project path')
    budget=resources(output.parent)
    if budget.get('memory_available_bytes',10**10)<4*1024**3:raise MemoryError('Require 4 GiB available')
    ghidras=list((runtime/'ghidra').glob('ghidra_*'));jdks=list((runtime/'jdk').glob('*/bin/java.exe'))
    if len(ghidras)!=1 or len(jdks)!=1:raise ValueError('Missing/ambiguous existing Ghidra/JDK runtime')
    ghidra,java=ghidras[0],jdks[0];plan=select(source.read_bytes(),selections)
    output.mkdir(parents=True);project.mkdir(parents=True);state=output/'runtime-state';state.mkdir()
    write(output/'plan.json',plan)
    (output/'plan.tsv').write_text(''.join(f"F\t{r['va']}\t{r['size']}\t{r['name']}\tPE selected span; {r['bound_kind']}; signature unresolved\n" for r in plan['spans']),encoding='utf-8')
    args=[str(java),'-Xmx2G','-Xshare:off','-XX:ActiveProcessorCount=2','--enable-native-access=ALL-UNNAMED',
      '-Djava.system.class.loader=ghidra.GhidraClassLoader','-Dfile.encoding=UTF8','-Dsun.java2d.d3d=false','-Dlog4j.skipJansi=true',
      f'-Duser.home={state}',f'-Dapplication.settingsdir={state}/settings',f'-Dapplication.cachedir={state}/cache',
      f'-Dapplication.tempdir={state}/tmp','-Djavax.xml.accessExternalDTD=','-Djavax.xml.accessExternalSchema=',
      '-Djavax.xml.accessExternalStylesheet=','-cp',str(ghidra/'Ghidra/Framework/Utility/lib/Utility.jar'),'ghidra.Ghidra',
      'ghidra.app.util.headless.AnalyzeHeadless',str(project),'Selected','-import',str(source),'-noanalysis','-max-cpu','1',
      '-scriptPath',str(Path(__file__).resolve().parent),'-postScript','ExportNative.java',str(output/'plan.tsv'),str(output/'ghidra')]
    with (output/'ghidra.log').open('x',encoding='utf-8') as log:
        result=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,
            creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name=='nt' else 0)
    if result.returncode:raise RuntimeError('Native Ghidra export failed; inspect the isolated log')
    report=check(source,plan,output/'ghidra');write(output/'verification.json',report)
    write(output/'run.json',dict(tool_version=VERSION,tool_sha256=sha(Path(__file__)),
        export_script_sha256=sha(Path(__file__).with_name('ExportNative.java')),source_sha256=plan['source_sha256'],
        resources_before=budget,heap='2GiB',headless_workers=1,automatic_analysis=False,native_source_executed=False,
        java_version=subprocess.check_output([str(java),'--version'],text=True),ghidra_properties_sha256=sha(ghidra/'Ghidra/application.properties')))
    print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ['source','output','runtime','project']:p.add_argument(name,type=Path)
    p.add_argument('selections',nargs='+',help='RVA inside one exception range, or explicit begin:end RVA')
    a=p.parse_args();run(a.source,a.output,a.runtime,a.project,a.selections)
