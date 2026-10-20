import json,tempfile,unittest
from pathlib import Path
from native_export import select,check
from test_native_image import fixture


def artifacts(root):
    source=root/'fixture.bin';raw=fixture();source.write_bytes(raw);plan=select(raw,['0x1000:0x1008'])
    out=root/'ghidra';out.mkdir();row=plan['spans'][0];name=row['name'];va=row['va']
    (out/(name+'.c')).write_text('void selected(void) {}\n')
    facts=dict(schema=1,decompile_completed=True,code_offset=va,code_size=8,export_name=name,
               instructions=[dict(address=str(va),bytes=raw[0x200:0x207].hex()),dict(address=str(va+7),bytes='c3')])
    (out/(name+'.facts.json')).write_text(json.dumps(facts))
    (out/(name+'.asm.tsv')).write_text(f"# selected\n{va:x}\t{raw[0x200:0x207].hex()}\tLEA\n{va+7:x}\tc3\tRET\n")
    return source,plan,out,facts


class NativeExportTests(unittest.TestCase):
    def test_assembly_only_is_explicit_and_does_not_promote_failed_c(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            source,plan,out,facts=artifacts(Path(directory));name=plan['spans'][0]['name']
            plan['mode']='assembly-only'
            with self.assertRaises(ValueError):check(source,plan,out)
            facts['decompile_completed']=False
            (out/(name+'.facts.json')).write_text(json.dumps(facts))
            (out/(name+'.c')).write_text('/* Static disassembly only; no pseudocode requested. */\n')
            self.assertFalse(check(source,plan,out)['pseudocode_requested'])
            plan['mode']='decompile'
            with self.assertRaises(ValueError):check(source,plan,out)

    def test_unsupported_mode_and_selector_reject(self):
        self.assertEqual(select(fixture(),['0x1001'],True)['mode'],'assembly-only')
        with self.assertRaises(ValueError):select(fixture(),['0x1001'],1)
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            source,plan,out,_=artifacts(Path(directory));plan['mode']='invented'
            with self.assertRaises(ValueError):check(source,plan,out)

    def test_range_and_manual_selection_are_distinguished(self):
        a=select(fixture(),['0x1001'])['spans'][0];b=select(fixture(),['0x1000:0x1008'])['spans'][0]
        self.assertEqual(a['size'],32);self.assertEqual(b['size'],8)
        self.assertIn('manual',b['bound_kind']);self.assertIn('not_complete',a['bound_kind'])

    def test_ambiguous_missing_overlap_unbacked_and_nondisassembly(self):
        for selections in [[],['0x1020'],['0x1000','0x1001'],['0x1000:0x1201'],['0x3000:0x3010'],['0x1000:0x1000']]:
            with self.assertRaises(ValueError):select(fixture(),selections)

    def test_exact_bytes_and_consistency(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            source,plan,out,_=artifacts(Path(directory));report=check(source,plan,out)
            self.assertEqual((report['instructions_byte_checked'],report['instruction_bytes_checked']),(2,8))

    def test_source_facts_assembly_and_c_tampering_reject(self):
        for target in ['source','facts','assembly','c','range']:
            with self.subTest(target=target),tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
                source,plan,out,facts=artifacts(Path(directory));name=plan['spans'][0]['name']
                if target=='source':source.write_bytes(source.read_bytes()+b'x')
                elif target=='facts':
                    facts['instructions'][0]['bytes']='90';(out/(name+'.facts.json')).write_text(json.dumps(facts))
                elif target=='assembly':(out/(name+'.asm.tsv')).write_text('140001000\t90\tNOP\n')
                elif target=='c':(out/(name+'.c')).write_text('ERROR: failed')
                else:plan['spans'][0]['file_offset']+=1
                with self.assertRaises(ValueError):check(source,plan,out)


if __name__=='__main__':unittest.main()
