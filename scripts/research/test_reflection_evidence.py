"""Own reflected declarations: reject forged field/enum/slot claims."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
import tempfile,unittest

from check_reflection_evidence import check
from reflection_index import parse_table
from test_reflection_index import descriptor,u


class ReflectionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'copy.gcl';self.evidence=self.root/'claims.json'
        sig='() research.example.tick (research.example)'
        raw=u(2)+descriptor(fields=[('s32','m_value',0)],virtuals=[sig])+descriptor(name='research.enum',size=4,alignment=4,labels=['a','b'])
        self.source.write_bytes(raw);rows=parse_table(raw,0)
        self.claims=dict(schema=1,source_sha256=hashlib.sha256(raw).hexdigest(),
            table=dict(offset=0,records=2,end=len(raw),sha256=hashlib.sha256(raw).hexdigest()),
            types=[{key:row[key] for key in ['name','base','offset','length','descriptor_sha256','size','alignment']} for row in rows],
            enums=[dict(type='research.enum',labels=['a','b'])],
            fields=[dict(type='research.example',field=dict(type='s32',name='m_value',offset=0))],
            virtuals=[dict(type='research.example',slot=0,signature=sig)])

    def run_check(self,claims):
        self.evidence.write_text(json.dumps(claims));return check(self.source,self.evidence)

    def test_matching_declarations_pass(self):
        result=self.run_check(self.claims)
        self.assertEqual(result['fields_checked'],1)
        self.assertEqual(result['table_records_checked'],2)

    def test_mutated_field_enum_and_slot_claims_fail(self):
        for section,key,value in [('fields','field',dict(type='s32',name='m_value',offset=4)),
                                  ('enums','labels',['b','a']),('virtuals','slot',1)]:
            claims=deepcopy(self.claims);claims[section][0][key]=value
            with self.subTest(section=section),self.assertRaises(ValueError):self.run_check(claims)

    def test_changed_source_fails_before_declaration_checks(self):
        self.source.write_bytes(self.source.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError,'source mismatch'):self.run_check(self.claims)


if __name__=='__main__':
    unittest.main()
