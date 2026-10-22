"""Synthetic chained, nested, invalid and separated x64 unwind layouts."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from native_image import Image
from native_unwind import UnwindGroups
from native_export import select,check
from test_native_image import fixture


def chained_fixture():
    b = fixture()
    struct.pack_into('<I',b,0x98+112+28,48)
    rows = [(0x1000,0x1020,0x3100),(0x1020,0x1040,0x3120),
            (0x1040,0x1060,0x3140),(0x1060,0x1080,0x3180)]
    for i,row in enumerate(rows):
        struct.pack_into('<III',b,0x400+12*i,*row)
    b[0x700:0x704] = bytes((1,0,0,0))
    b[0x720:0x724] = bytes((0x21,0,0,0))
    struct.pack_into('<III',b,0x724,*rows[0])
    # Three slots must be rounded to four slots before reading the nested link.
    b[0x740:0x744] = bytes((0x21,0,3,0))
    b[0x744:0x74c] = bytes(8)
    struct.pack_into('<III',b,0x74c,*rows[1])
    b[0x780:0x784] = bytes((1,0,0,0))
    return b


class NativeUnwindTests(unittest.TestCase):
    def test_nested_links_resolve_same_primary_from_any_fragment(self):
        g = UnwindGroups(Image(chained_fixture()))
        a,b = g.group(0x1001),g.group(0x1041)
        self.assertEqual(a,b)
        self.assertEqual(a['primary']['begin_rva'],0x1000)
        self.assertEqual([r['begin_rva'] for r in a['ranges']],[0x1000,0x1020,0x1040])
        self.assertTrue(a['contiguous'])

    def test_adjacent_unlinked_range_is_not_included(self):
        g = UnwindGroups(Image(chained_fixture())).group(0x1061)
        self.assertEqual(len(g['ranges']),1)
        self.assertEqual(g['primary']['begin_rva'],0x1060)

    def test_padded_slot_count_locates_chain_payload(self):
        g = UnwindGroups(Image(chained_fixture())).group(0x1041)
        self.assertEqual(g['unwind'][2]['parent'],[0x1020,0x1040,0x3120])
        self.assertEqual(len(bytes.fromhex(g['unwind'][2]['bytes'])),24)

    def test_noncontiguous_group_is_reported_and_export_rejects_gap(self):
        b=chained_fixture()
        struct.pack_into('<I',b,0x40c,0x1030)
        struct.pack_into('<III',b,0x74c,0x1030,0x1040,0x3120)
        g=UnwindGroups(Image(b)).group(0x1001)
        self.assertFalse(g['contiguous'])
        with self.assertRaises(ValueError):select(b,['0x1001'],chained=True)

    def test_bad_target_and_cycles_reject(self):
        for kind in ['missing','cycle']:
            b=chained_fixture()
            if kind=='missing':struct.pack_into('<I',b,0x728,0x1021)
            else:
                b[0x700]=0x21
                struct.pack_into('<III',b,0x704,0x1040,0x1060,0x3140)
            with self.assertRaises(ValueError):UnwindGroups(Image(b))

    def test_invalid_flags_versions_alignment_and_truncation_reject(self):
        for kind in ['flags','version','alignment','truncation','version2chain']:
            b=chained_fixture()
            if kind=='flags':b[0x720]=0x29
            elif kind=='version':b[0x720]=0x20
            elif kind=='alignment':struct.pack_into('<I',b,0x414,0x3121)
            elif kind=='truncation':
                struct.pack_into('<I',b,0x414,0x31f8)
                b[0x7f8:0x7fc]=bytes((0x21,0,0,0))
            else:b[0x720]=0x22
            with self.assertRaises(ValueError):UnwindGroups(Image(b))

    def test_duplicate_runtime_entry_rejects_ambiguous_graph(self):
        b=chained_fixture();b[0x40c:0x418]=b[0x400:0x40c]
        with self.assertRaises(ValueError):UnwindGroups(Image(b))

    def test_nonchained_version2_header_is_explicit_opaque_root(self):
        b=chained_fixture();b[0x780]=2
        g=UnwindGroups(Image(b)).group(0x1061)
        self.assertEqual(g['unwind'][0]['version'],2)
        self.assertEqual(len(bytes.fromhex(g['unwind'][0]['bytes'])),4)

    def test_chained_export_is_opt_in_and_manual_spans_not_reinterpreted(self):
        b=chained_fixture()
        self.assertEqual(select(b,['0x1001'])['spans'][0]['size'],32)
        s=select(b,['0x1041'],chained=True)['spans'][0]
        self.assertEqual((s['begin_rva'],s['end_rva']),(0x1000,0x1060))
        self.assertIn('unwind_group',s)
        with self.assertRaises(ValueError):select(b,['0x1000:0x1020'],chained=True)
        with self.assertRaises(ValueError):select(b,['0x1001'],chained=1)

    def test_two_selections_of_one_group_reject_overlap(self):
        with self.assertRaises(ValueError):select(chained_fixture(),['0x1001','0x1041'],chained=True)

    def test_group_metadata_is_required_and_rechecked_against_source(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            root=Path(directory);raw=chained_fixture();source=root/'source.bin';source.write_bytes(raw)
            plan=select(raw,['0x1001'],chained=True);row=plan['spans'][0];name=row['name'];va=row['va']
            facts=dict(schema=1,decompile_completed=True,code_offset=va,code_size=row['size'],export_name=name,
                       instructions=[dict(address=str(va),bytes=raw[0x200:0x207].hex()),dict(address=str(va+7),bytes='c3')])
            (root/(name+'.c')).write_text('void selected(void) {}')
            (root/(name+'.facts.json')).write_text(json.dumps(facts))
            (root/(name+'.asm.tsv')).write_text(f'{va:x}\t{raw[0x200:0x207].hex()}\tLEA\n{va+7:x}\tc3\tRET\n')
            self.assertEqual(check(source,plan,root)['instructions_byte_checked'],2)
            original=row.pop('unwind_group')
            with self.assertRaises(ValueError):check(source,plan,root)
            row['unwind_group']=original
            original['unwind'][1]['bytes']='00'
            with self.assertRaises(ValueError):check(source,plan,root)


if __name__ == '__main__':
    unittest.main()
