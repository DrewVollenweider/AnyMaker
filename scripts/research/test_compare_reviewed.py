"""Local comparison categories and rejection of mismatched archived evidence."""
import copy
import hashlib
import unittest
from compare_reviewed import compare_function


def fixture():
    old=bytes(range(32));new=bytearray(64);new[20:32]=old[4:16]
    def rec(raw,offset,size=12):
        return dict(signature='() sample ()',code_offset=offset,code_size=size,
                    code_sha256=hashlib.sha256(raw[offset:offset+size]).hexdigest(),
                    references=[dict(kind=3,slot_offset=12,symbol='global')])
    a,b=rec(old,4),rec(new,20)
    assembly='00000004\t0405\topaque\n00000006\t0607\topaque\n'
    e=dict(signature=a['signature'],code_offset=4,code_sha256=a['code_sha256'],
           embedded_reads=[dict(offset=8,width=4,bytes=old[8:12].hex())])
    return old,new,a,b,assembly,e


class CompareReviewedTests(unittest.TestCase):
    def run_case(self,change=None):
        old,new,a,b,asm,e=fixture()
        if change:change(new,b)
        b['code_sha256']=hashlib.sha256(new[b['code_offset']:b['code_offset']+b['code_size']]).hexdigest()
        return compare_function(old,new,a,b,asm,e)

    def test_rebased_local_bytes_and_references_match(self):
        r=self.run_case()
        self.assertEqual(r['status'],'local_checks_match')
        self.assertTrue(r['whole_code_equal'])
        self.assertEqual(r['archived_instructions_checked'],2)

    def test_unclassified_tail_change_is_not_called_unchanged_code(self):
        r=self.run_case(lambda raw,b:raw.__setitem__(30,255))
        self.assertEqual(r['status'],'local_checks_match')
        self.assertFalse(r['whole_code_equal'])
        self.assertEqual(r['unclassified_changed_bytes'],1)

    def test_instruction_change_is_separate(self):
        r=self.run_case(lambda raw,b:raw.__setitem__(20,255))
        self.assertEqual(r['status'],'instruction_bytes_changed')
        self.assertEqual(r['changed_instruction_offsets'],[0])

    def test_direct_read_change_is_separate(self):
        r=self.run_case(lambda raw,b:raw.__setitem__(24,255))
        self.assertEqual(r['status'],'direct_reads_changed')
        self.assertEqual(r['changed_direct_read_offsets'],[4])

    def test_reference_change_is_not_hidden_by_identical_code(self):
        r=self.run_case(lambda raw,b:b['references'][0].update(symbol='different'))
        self.assertEqual(r['status'],'references_changed')
        self.assertTrue(r['whole_code_equal'])

    def test_size_change_prevents_mapping_new_local_spans(self):
        r=self.run_case(lambda raw,b:b.update(code_size=13))
        self.assertEqual(r['status'],'code_size_changed')
        self.assertFalse(r['new_local_checks_performed'])

    def test_source_hash_and_reader_identity_mismatches_reject(self):
        for which in ['source','reader','signature']:
            old,new,a,b,asm,e=fixture()
            if which=='source':new[20]=255
            elif which=='reader':e['code_offset']=5
            else:b['signature']='() other ()'
            with self.assertRaises(ValueError):compare_function(old,new,a,b,asm,e)

    def test_tampered_archived_instruction_and_direct_read_reject(self):
        for which in ['instruction','read']:
            old,new,a,b,asm,e=fixture()
            if which=='instruction':asm=asm.replace('0405','ffff')
            else:e['embedded_reads'][0]['bytes']='ffffffff'
            with self.assertRaises(ValueError):compare_function(old,new,a,b,asm,e)

    def test_empty_overlapping_and_out_of_range_assembly_reject(self):
        for asm in ['', '4\t0405\tx\n5\t0506\tx\n','3\t0304\tx\n']:
            old,new,a,b,_,e=fixture()
            with self.assertRaises(ValueError):compare_function(old,new,a,b,asm,e)

    def test_out_of_range_or_mis_sized_read_rejects(self):
        for read in [dict(offset=15,width=4,bytes='00000000'),
                     dict(offset=8,width=8,bytes='08090a0b')]:
            old,new,a,b,asm,e=fixture();e['embedded_reads']=[read]
            with self.assertRaises(ValueError):compare_function(old,new,a,b,asm,e)


if __name__=='__main__':unittest.main()
