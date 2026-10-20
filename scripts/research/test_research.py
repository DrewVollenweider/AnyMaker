"""Synthetic format fixtures and failure cases; no shipped machine code required."""
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import sqlite3
import unittest
from unittest.mock import patch

import baseline
import gcl_index as gcl
from compare_builds import mapping_diff
from export_plan import plan

TEST_TEMP = Path(__file__).resolve().parent / '.test-tmp'
TEST_TEMP.mkdir(exist_ok=True)
tempfile.tempdir = str(TEST_TEMP)


def u32(n):
    return struct.pack('<I', n)


def text(s):
    b=s.encode()
    return u32(len(b))+b


def fixture(extra=0):
    sig='() research.example (const s32)'
    # Own synthetic single RET and padding, followed by pointer slots.
    return (text(sig)+u32(3)+u32(42)+u32(2)
            +u32(3)+text('research.global')+u32(4)+text('() research.target ()')
            +u32(8)+u32(24+extra)+b'\xc3'+b'\0'*23)


class GclTests(unittest.TestCase):
    def test_template_qualified_name_spaces_are_valid_but_plain_name_spaces_are_not(self):
        old='() research.example (const s32)'
        new='() research.container<s32, f64>.example (const s32)'
        raw=text(new)+fixture()[len(text(old)):]
        result,_=gcl.scan(raw)
        self.assertEqual([row['signature'] for row in result],[new])
        self.assertFalse(gcl.valid_signature(b'() research.bad name (const s32)'))
        self.assertFalse(gcl.valid_signature(b'() research.container<s32, f64.example ()'))

    def test_export_plan_binds_source_and_parser_versions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'input.gcl';source.write_bytes(fixture())
            r=gcl.record(source.read_bytes(),4);r['same_signature_records']=1
            db=sqlite3.connect(root/'index.sqlite')
            db.executescript('CREATE TABLE provenance(key TEXT,value TEXT);CREATE TABLE functions(signature TEXT,record TEXT);')
            db.executemany('INSERT INTO provenance VALUES(?,?)',[
                ('source_sha256',json.dumps(baseline.sha(source))),('tool_sha256',json.dumps('stale'))])
            db.execute('INSERT INTO functions VALUES(?,?)',(r['signature'],json.dumps(r)))
            db.commit()
            with self.assertRaisesRegex(ValueError,'parser version/hash differs'):
                plan(source,root/'index.sqlite',root/'wrong',['research.example'])
            db.execute("UPDATE provenance SET value=? WHERE key='tool_sha256'",(json.dumps(baseline.sha(Path(gcl.__file__))),))
            db.commit();db.close()
            plan(source,root/'index.sqlite',root/'good',['research.example'])
            self.assertEqual(len((root/'good/plan.tsv').read_text().splitlines()),3)
            source.write_bytes(b'different version')
            with self.assertRaisesRegex(ValueError,'version mismatch'):
                plan(source,root/'index.sqlite',root/'changed',['research.example'])

    def test_semantic_diff_preserves_omitted_values(self):
        r=mapping_diff({'a':0,'b':1},{'a':False,'c':0})
        # JSON boolean versus integer must remain distinguishable downstream.
        self.assertEqual(r['added'],['c'])
        self.assertEqual(r['removed'],['b'])
        self.assertEqual(r['changed'],['a'])

    def test_offsets_hashes_relocations(self):
        b=fixture()
        r=gcl.record(b,4)
        self.assertEqual(r['code_offset'],len(b)-24)
        self.assertEqual(r['code_sha256'],hashlib.sha256(b[-24:-16]).hexdigest())
        self.assertEqual([x['slot_offset'] for x in r['references']],[8,16])

    def test_all_truncations_rejected(self):
        b=fixture()
        for n in range(len(b)):
            with self.subTest(n=n),self.assertRaises(ValueError):
                gcl.record(b[:n],4)

    def test_extra_allocation_is_not_serialized(self):
        b=fixture(8)+b'TRAILER!'
        r=gcl.record(b,4)
        self.assertEqual(r['serialized_size'],24)
        self.assertEqual(r['allocation_extra_uninterpreted'],8)
        self.assertEqual(r['serialized_sha256'],hashlib.sha256(b[-32:-8]).hexdigest())

    def test_unknown_allocation_shape_rejected(self):
        with self.assertRaises(ValueError):gcl.record(fixture(16),4)

    def test_nonzero_pointer_slots_rejected(self):
        b=bytearray(fixture()); b[-1]=1
        with self.assertRaises(ValueError):gcl.record(b,4)

    def test_signature_string_is_not_function(self):
        rows,_=gcl.scan(text('() misleading.name ()')+b'\0'*32)
        self.assertEqual(rows,[])

    def test_unknown_relocation_kind_rejected(self):
        b=bytearray(fixture()); at=4+len('() research.example (const s32)')+12
        struct.pack_into('<I',b,at,99)
        with self.assertRaisesRegex(ValueError,'unsupported relocation'):gcl.record(b,4)

    def test_numeric_operand(self):
        b=text('() research.numeric ()')+u32(1)+u32(0)+u32(1)+u32(1)+u32(7)+u32(8)+u32(16)+b'\xc3'+b'\0'*15
        self.assertEqual(gcl.record(b,4)['references'][0]['operand_u32'],7)


class BaselineTests(unittest.TestCase):
    def test_utf8_prefix_ending_inside_character(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'text.bin'
            p.write_bytes(b'a\t'+b'x'*4093+'é'.encode()+b'\n')
            self.assertEqual(baseline.classify(p),'utf8-tabular')

    def test_actual_format_over_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.exe'; p.write_text('{"a":1}')
            self.assertEqual(baseline.classify(p),'json')
            p.write_bytes(b'\x89PNG\r\n\x1a\n')
            self.assertEqual(baseline.classify(p),'png')

    def test_never_output_into_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with self.assertRaises(ValueError):baseline.baseline(p,p/'snapshot')

    def test_stable_copy_manifest_and_account_whitelist(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); source=p/'install'; source.mkdir()
            (source/'game.exe').write_bytes(b'own fixture')
            (source/'other.bin').write_bytes(b'other')
            steam=p/'manifest'; steam.write_text('"buildid" "7"\n"LastOwner" "PRIVATE"')
            with patch.object(baseline,'resources',return_value={'disk_free_bytes':100*1024**3}):
                baseline.baseline(source,p/'out',steam)
            report=json.loads((p/'out/inventory.json').read_text())
            self.assertEqual(report['file_count'],2)
            self.assertEqual(report['snapshot_count'],1)
            self.assertNotIn('PRIVATE',json.dumps(report))
            self.assertEqual((p/'out/snapshot/game.exe').read_bytes(),b'own fixture')
            with self.assertRaises(FileExistsError):baseline.baseline(source,p/'out')

    def test_source_change_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); source=p/'install'; source.mkdir()
            (source/'x.bin').write_bytes(b'fixed')
            calls=iter(['a','b'])
            with patch.object(baseline,'resources',return_value={'disk_free_bytes':100*1024**3}),patch.object(baseline,'sha',side_effect=lambda p:next(calls)):
                with self.assertRaisesRegex(ValueError,'changed on second pass'):
                    baseline.baseline(source,p/'out')


if __name__=='__main__':unittest.main()
