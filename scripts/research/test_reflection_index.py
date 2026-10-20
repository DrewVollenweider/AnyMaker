"""Own descriptor fixtures: strict bounds, EOF, ambiguity and omitted symbols."""
import struct
import unittest

from reflection_index import locate_table,parse,parse_table


def u(value):return struct.pack('<I',value)
def text(value):
    value=value.encode();return u(len(value))+value


def descriptor(name='research.example',base='',size=16,alignment=8,fields=(),virtuals=(),labels=None,unknown=0):
    enum=labels is not None
    result=u(14 if enum else 13)+text(name)+text(base)+u(size)+u(alignment)+u(0)
    result+=u(len(labels or []))+b''.join(text(label) for label in labels or [])
    result+=u(len(virtuals))+b''.join(text(value) for value in virtuals)
    result+=text('')*4+u(unknown)+u(len(fields))
    for typ,field,offset in fields:result+=text(typ)+text(field)+u(offset)
    return result


class ReflectionTests(unittest.TestCase):
    def test_declared_parent_fields_and_template_method_names(self):
        raw=descriptor(base='research.parent',fields=[('s32','m_value',8)],
                       virtuals=['() research.generic<s32, f64>.tick (research.generic<s32, f64>)'])
        row=parse(raw,0)
        self.assertEqual(row['base'],'research.parent')
        self.assertEqual(row['fields'][0]['offset'],8)
        self.assertEqual(row['length'],len(raw))

    def test_duplicate_enum_labels_are_preserved_with_ordinals(self):
        row=parse(descriptor(name='research.enum',size=4,alignment=4,labels=['a','a','b']),0)
        self.assertEqual(row['enum_labels'],['a','a','b'])
        self.assertEqual(row['duplicate_enum_labels'],{'a':2})

    def test_tail_member_is_retained_without_claiming_storage_width(self):
        row=parse(descriptor(fields=[('research.native','m_native',16)]),0)
        self.assertEqual(row['fields'][0]['offset'],row['size'])

    def test_outside_field_and_invalid_alignment_fail(self):
        for raw in [descriptor(fields=[('s32','m_bad',17)]),descriptor(alignment=3),descriptor(unknown=1)]:
            with self.assertRaises(ValueError):parse(raw,0)

    def test_declared_count_and_exact_eof_are_required(self):
        raw=u(2)+descriptor()+descriptor(name='research.second')
        self.assertEqual(len(parse_table(raw,0)),2)
        for broken in [raw+b'junk',u(1)+raw[4:],u(100001)+raw[4:]]:
            with self.assertRaises(ValueError):parse_table(broken,0)

    def test_every_fixture_truncation_is_rejected(self):
        raw=u(1)+descriptor(fields=[('s32','m_value',0)])
        for end in range(len(raw)):
            with self.subTest(end=end),self.assertRaises(ValueError):parse_table(raw[:end],0)

    def test_locator_skips_header_noise_and_finds_complete_table(self):
        prefix=b'\x00'*32
        raw=prefix+u(1)+descriptor()
        offset,rows,_=locate_table(raw,0)
        self.assertEqual(offset,len(prefix))
        self.assertEqual(rows[0]['name'],'research.example')


if __name__=='__main__':
    unittest.main()
