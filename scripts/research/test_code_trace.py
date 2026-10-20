"""Synthetic dataflow and reader failure controls; never imports/runs game code."""
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
import tempfile
import unittest
from contextlib import closing

import code_reader
import check_offline_evidence
import gcl_index
import trace_code as trace
from test_research import fixture


def vn(space,offset,size=8):
    return {'space':space,'offset':str(offset),'size':size,'constant':space=='const',
            'register':space=='register','unique':space=='unique'}
def op(name,out=None,*inputs):return {'opcode':name,'output':out,'inputs':list(inputs)}
def ins(address,*ops,fallthrough=None):
    return {'address':str(address),'bytes':'90','text':'synthetic','pcode':list(ops),
            'fallthrough':str(address+1 if fallthrough is None else fallthrough)}
SLOT=900
SLOTS={SLOT:{'kind':6,'symbol':'() example.virtual ()','slot_offset':8}}
R=vn('register',0);U=vn('unique',20);M=vn('ram',SLOT)


class DataflowTests(unittest.TestCase):
    def run_flow(self,instructions):return trace.interpret(instructions,SLOTS)

    def test_slot_memory_copy_then_indirect_call(self):
        calls,reads=self.run_flow([ins(1,op('COPY',R,M)),ins(2,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'slot-derived-in-local-block')
        self.assertEqual(calls[0]['loaded_at'],1)
        self.assertEqual(reads[0]['slot_address'],SLOT)

    def test_virtual_displacement_multi_load_is_dependency_not_target_binding(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),
            ins(2,op('INT_ADD',R,R,vn('register',24))),
            ins(3,op('LOAD',U,vn('const',1),R),op('COPY',R,U)),
            ins(4,op('LOAD',U,vn('const',1),R),op('CALLIND',None,U))])
        self.assertEqual([x['operation'] for x in calls[0]['dependency_steps']],['read-slot','INT_ADD','LOAD','LOAD'])
        self.assertNotIn('target_record',calls[0])

    def test_plain_metadata_read_is_not_call(self):
        calls,reads=self.run_flow([ins(1,op('COPY',R,M))])
        self.assertFalse(calls);self.assertEqual(len(reads),1)

    def test_unknown_pointer_remains_unresolved(self):
        self.assertEqual(self.run_flow([ins(1,op('CALLIND',None,R))])[0][0]['resolution'],'unresolved-indirect')

    def test_calls_clobber_all_register_provenance(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),ins(2,op('CALLIND',None,R)),ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[1]['resolution'],'unresolved-indirect')

    def test_narrow_register_write_invalidates_pointer(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),
            ins(2,op('COPY',vn('register',0,4),vn('const',2,4))),ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_unknown_register_write_invalidates_pointer(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),
            ins(2,op('INT_XOR',R,R,R)),ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_branch_ends_block(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),ins(2,op('CBRANCH',None,vn('ram',8),vn('register',3,1))),
                              ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_branch_target_clears_fallthrough_load(self):
        calls,_=self.run_flow([ins(1,op('CBRANCH',None,vn('ram',3),vn('register',3,1))),
                              ins(2,op('COPY',R,M)),ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_gap_clears_provenance(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),ins(9,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_unique_temporary_never_survives_instruction(self):
        calls,_=self.run_flow([ins(1,op('COPY',U,M)),ins(2,op('CALLIND',None,U))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')

    def test_direct_call_address_is_not_memory_slot_read(self):
        calls,reads=self.run_flow([ins(1,op('CALL',None,M))])
        self.assertEqual(calls[0]['resolution'],'direct-address');self.assertFalse(reads)

    def test_explicit_load_of_slot(self):
        calls,_=self.run_flow([ins(1,op('LOAD',U,vn('const',1),vn('const',SLOT)),op('CALLIND',None,U))])
        self.assertEqual(calls[0]['slot_address'],SLOT)

    def test_two_tagged_values_do_not_create_unique_candidate(self):
        calls,_=self.run_flow([ins(1,op('COPY',R,M)),
            ins(2,op('INT_ADD',R,R,R)),ins(3,op('CALLIND',None,R))])
        self.assertEqual(calls[0]['resolution'],'unresolved-indirect')


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.source=self.root/'copy.gcl'
        raw=fixture();self.source.write_bytes(raw);self.raw=raw
        r=gcl_index.record(raw,4);r['export_name']='example'
        self.rec=r;self.folder=self.root/'export';(self.folder/'ghidra').mkdir(parents=True)
        self.meta={'source_sha256':hashlib.sha256(raw).hexdigest(),'records':[r]}
        (self.folder/'records.json').write_text(json.dumps(self.meta))
        self.fact={k:r[k] for k in ['signature','code_offset','code_size','export_name']}
        self.fact.update(schema=1,decompile_completed=True,instructions=[{
            'address':str(r['code_offset']),'bytes':'c3','text':'RET','mnemonic':'RET',
            'fallthrough':None,'references':[],'pcode':[]}])
        self.factpath=self.folder/'ghidra/example.facts.json';self.factpath.write_text(json.dumps(self.fact))
        self.asm=f"# own synthetic fixture\n{r['code_offset']:x}\tc3\tRET\n"
        (self.folder/'ghidra/example.asm.tsv').write_text(self.asm)
        (self.folder/'ghidra/example.c').write_text('void example() { return; }')
        self.index=self.root/'index.sqlite'
        with closing(sqlite3.connect(self.index)) as db:
            db.execute('CREATE TABLE provenance(key TEXT,value TEXT)')
            db.execute('INSERT INTO provenance VALUES(?,?)',('source_sha256',json.dumps(self.meta['source_sha256'])))
            db.execute('CREATE TABLE functions(signature TEXT,code_offset INTEGER,code_size INTEGER)')
            db.execute('INSERT INTO functions VALUES(?,?,?)',(r['signature'],r['code_offset'],r['code_size']))
            db.commit()

    def test_reader_build_search_show_and_no_overwrite(self):
        out=self.root/'reader';r=code_reader.build(self.source,self.index,out,[self.folder])
        self.assertEqual(r['counts']['functions'],1)
        hits=code_reader.search(out/'code.sqlite','research')
        self.assertEqual(hits[0]['code_offset'],self.rec['code_offset'])
        self.assertIn('return',code_reader.show(out/'code.sqlite',self.rec['code_offset'],'c'))
        self.assertEqual(code_reader.show(out/'code.sqlite',self.rec['code_offset'],'calls'),[])
        with self.assertRaises(FileExistsError):code_reader.build(self.source,self.index,out,[self.folder])
        with self.assertRaises(ValueError):code_reader.search(out/'code.sqlite','example',101)
        with self.assertRaises(ValueError):code_reader.show(out/'code.sqlite',1)

    def test_wrong_original_bytes_rejected(self):
        f=json.loads(json.dumps(self.fact));f['instructions'][0]['bytes']='90'
        with self.assertRaisesRegex(ValueError,'bytes differ'):
            trace.validate_instructions(f,self.rec,self.raw,self.asm)

    def test_assembly_and_facts_disagreement_rejected(self):
        with self.assertRaisesRegex(ValueError,'disagree'):
            trace.validate_instructions(self.fact,self.rec,self.raw,self.asm.replace('RET','different'))

    def test_forged_metadata_rejected(self):
        self.meta['records'][0]['code_sha256']='forged';(self.folder/'records.json').write_text(json.dumps(self.meta))
        with self.assertRaisesRegex(ValueError,'original GCL metadata'):
            trace.audit(self.source,self.index,self.folder,self.root/'bad.json')

    def test_source_version_mismatch_rejected(self):
        self.source.write_bytes(self.raw+b'changed')
        with self.assertRaisesRegex(ValueError,'mismatch'):
            trace.audit(self.source,self.index,self.folder,self.root/'bad.json')

    def test_unsafe_export_path_rejected(self):
        self.meta['records'][0]['export_name']='../escape';(self.folder/'records.json').write_text(json.dumps(self.meta))
        with self.assertRaisesRegex(ValueError,'Unsafe'):
            trace.audit(self.source,self.index,self.folder,self.root/'bad.json')

    def test_incomplete_reader_not_queryable(self):
        path=self.root/'incomplete.sqlite'
        with closing(sqlite3.connect(path)) as db:
            db.execute('CREATE TABLE metadata(key TEXT,value TEXT)');db.commit()
        with self.assertRaisesRegex(ValueError,'Incomplete'):code_reader.search(path,'x')

    def test_nonfinite_literal_is_not_invalid_json(self):
        raw=b'\x90'+struct.pack('<d',float('inf'))
        i=ins(0,op('COPY',R,vn('ram',1)));i['bytes']='90'
        r=trace.embedded_reads([i],{'code_offset':0,'code_size':len(raw)},raw)
        self.assertEqual(r[0]['ieee_float_interpretation'],'inf')
        json.dumps(r,allow_nan=False)

    def test_literal_reader_excludes_instruction_bytes(self):
        r=trace.literal_strings([{'address':'0','bytes':'41424344'}],{'code_offset':0,'code_size':9},b'ABCD\0name')
        self.assertEqual([x['text'] for x in r],['name'])

    def test_address_reference_is_distinct_from_memory_read(self):
        raw=b'\x90'+struct.pack('<d',.0001)
        i=ins(0,op('COPY',R,vn('const',1)))
        rec={'code_offset':0,'code_size':len(raw)}
        self.assertEqual(trace.embedded_reads([i],rec,raw),[])
        preview=trace.address_literals([i],rec,raw)
        self.assertEqual(preview[0]['classification'],'address-reference-not-proven-read')
        self.assertEqual(preview[0]['preview_f64'],.0001)

    def selected_evidence(self):
        evidence={'schema':1,'source_sha256':self.meta['source_sha256'],
                  'functions':[self.rec],'constants':[{
                      'function_offset':self.rec['code_offset'],'offset':self.rec['code_offset'],
                      'format':'u8','bytes':'c3','value':195,'name':'synthetic return byte'}],
                  'strings':[],'call_examples':[]}
        path=self.root/'selected.json';path.write_text(json.dumps(evidence))
        return evidence,path

    def test_selected_evidence_checks_source_and_constant(self):
        e,path=self.selected_evidence()
        result=check_offline_evidence.check(self.source,path)
        self.assertEqual(result['constants_checked'],1)
        e['constants'][0]['value']=194;path.write_text(json.dumps(e))
        with self.assertRaisesRegex(ValueError,'Changed constant'):
            check_offline_evidence.check(self.source,path)
        self.source.write_bytes(self.raw+b'changed')
        with self.assertRaisesRegex(ValueError,'build mismatch'):
            check_offline_evidence.check(self.source,path)

    def test_selected_evidence_rejects_wrong_operand_metadata(self):
        e,path=self.selected_evidence()
        e['call_examples']=[{'function_offset':self.rec['code_offset'],
            'instruction':self.rec['code_offset'],'bytes':'c3',
            'slot_address':self.rec['code_offset'],'kind':6,'symbol':'invented'}]
        path.write_text(json.dumps(e))
        with self.assertRaisesRegex(ValueError,'operand metadata mismatch'):
            check_offline_evidence.check(self.source,path)

    def test_selected_evidence_rejects_out_of_range_constant(self):
        e,path=self.selected_evidence()
        e['constants'][0]['offset']=self.rec['code_offset']+self.rec['code_size']
        path.write_text(json.dumps(e))
        with self.assertRaisesRegex(ValueError,'Constant out of range'):
            check_offline_evidence.check(self.source,path)


if __name__=='__main__':unittest.main()
