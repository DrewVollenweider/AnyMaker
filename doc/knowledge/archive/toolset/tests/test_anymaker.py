import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('anymaker',ROOT/'anymaker.py')
am=importlib.util.module_from_spec(spec); spec.loader.exec_module(am)


class ToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cart=am.load(ROOT.parent/'exploration/baseline/steercart.data')
        cls.cat=am.definitions()

    def issues(self,doc):
        return am.audit(doc,self.cat)['issues']

    def test_real_creation_has_no_errors(self):
        result=am.audit(self.cart,self.cat)
        self.assertTrue(result['ok'],result['issues'])
        self.assertEqual(result['vehicles'][0]['components'],16)
        self.assertEqual(result['vehicles'][0]['links']['mechanical_links'],8)

    def test_dangling_links_detected(self):
        doc=copy.deepcopy(self.cart)
        doc['vehicles']['vehicles'][0]['mechanical_links'][0]['p1']['comp']=999999
        self.assertIn('dangling_link',[i['code'] for i in self.issues(doc)])

    def test_duplicate_and_invalid_definition(self):
        doc=copy.deepcopy(self.cart); cs=doc['vehicles']['vehicles'][0]['grids'][0]['components']
        cs.append(copy.deepcopy(cs[0])); cs[-1]['def']=999
        codes={i['code'] for i in self.issues(doc)}
        self.assertTrue({'duplicate_component','definition_index'}<=codes)

    def test_reflection_is_not_rotation(self):
        doc=copy.deepcopy(self.cart)
        doc['vehicles']['vehicles'][0]['grids'][0]['components'][0]['rot']=[-1,0,0,0,1,0,0,0,1]
        self.assertIn('rotation',[i['code'] for i in self.issues(doc)])

    def test_nonplanar_plate(self):
        doc={'definitions':{'components':[]},'vehicles':{'vehicles':[{'id':1,'nodes':[{'id':i+1,'pos':p} for i,p in enumerate([[0,0,0],[1,0,0],[1,1,0],[0,1,1]])],'plates':[{'nodes':[1,2,3,4]}]}]}}
        self.assertIn('plate_nonplanar',[i['code'] for i in self.issues(doc)])

    def test_malformed_inputs_report_errors(self):
        for doc in ([],{}, {'definitions':{'components':[]},'vehicles':{'vehicles':[{'id':1,'grids':'bad'}]}}):
            self.assertFalse(am.audit(doc,self.cat)['ok'])

    def test_frame_only_creation_omits_component_table(self):
        doc={'definitions':{},'vehicles':{'vehicles':[{'id':1,'nodes':[{'id':1},{'id':2,'pos':[1,0,0]}],'edges':[{'n0':1,'n1':2}]}]}}
        self.assertTrue(am.audit(doc,self.cat)['ok'])
        self.assertIn('Vehicle 1',am.schematic(doc))

    def test_draft_preserves_source_and_unknown_fields(self):
        base=copy.deepcopy(self.cart); base['unknown_future_field']={'keep':True}
        plan={'replace':[{'path':'/vehicles/vehicles/0/grids/0/components/10/is_on','value':False}]}
        result,check=am.draft(base,plan)
        self.assertTrue(check['ok']); self.assertEqual(result['unknown_future_field'],base['unknown_future_field'])
        self.assertTrue(base['vehicles']['vehicles'][0]['grids'][0]['components'][10]['is_on'])
        self.assertFalse(result['vehicles']['vehicles'][0]['grids'][0]['components'][10]['is_on'])

    def test_addition_allocates_unique_id_and_definition(self):
        plan={'add_components':[{'vehicle_id':209,'definition':'electric_motor_a','component':{'pos':[0,0,0]}}]}
        result,check=am.draft(self.cart,plan)
        last=am.components(am.vehicles(result)[0])[-1]
        self.assertEqual(last['id'],24)
        self.assertEqual(result['definitions']['components'][last['def']],'electric_motor_a')
        self.assertNotIn('electric_motor_a',self.cart['definitions']['components'])

    def test_bad_plan_does_not_silently_add_fields(self):
        with self.assertRaises(KeyError): am.draft(self.cart,{'replace':[{'path':'/typo','value':1}]})
        with self.assertRaises(ValueError): am.draft(self.cart,{'typo':[]})

    def test_append_invalid_edge_rejected(self):
        plan={'append':[{'path':'/vehicles/vehicles/0/edges','values':[{'n0':1,'n1':99999}]}]}
        with self.assertRaises(ValueError): am.draft(self.cart,plan)

    def test_append_valid_structure_preserves_base(self):
        plan={'append':[{'path':'/vehicles/vehicles/0/nodes','values':[{'id':100,'pos':[0,0,0]}]}, {'path':'/vehicles/vehicles/0/edges','values':[{'n0':1,'n1':100}]}]}
        result,check=am.draft(self.cart,plan)
        self.assertTrue(check['ok'])
        self.assertEqual(len(am.vehicles(result)[0]['nodes']),len(am.vehicles(self.cart)[0]['nodes'])+1)

    def test_output_root_redirect_rejected(self):
        with patch.object(am,'OUTPUT',am.OUTPUT/'..'/'reference'):
            with self.assertRaises(ValueError): am.destination('bad.json')

    def test_diff_handles_escaped_pointer_and_add_remove(self):
        changes=am.differences({'a/b':1,'gone':2},{'a/b':3,'new':4})
        self.assertEqual(changes[0]['path'],'/a~1b')
        self.assertTrue(any('removed' in d for d in changes)); self.assertTrue(any('added' in d for d in changes))

    def test_outputs_reject_escape_and_overwrite(self):
        with self.assertRaises(ValueError): am.destination('../reference/vehicle_component_definitions.json')
        with self.assertRaises(ValueError): am.destination(str(ROOT.parent/'sources/test.json'))
        with tempfile.TemporaryDirectory(dir=am.OUTPUT) as tmp:
            with patch.object(am,'OUTPUT',Path(tmp)):
                path=Path(am.save('new.json',{'ok':True}))
                self.assertEqual(am.load(path),{'ok':True})
                with self.assertRaises(ValueError): am.save('new.json',{'ok':False})

    def test_snapshot_nonfinite_json_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=am.OUTPUT) as tmp:
            p=Path(tmp)/'bad.json'; p.write_text('{"x": NaN}')
            with self.assertRaises(ValueError): am.load(p)

    def test_schematic_escapes_definition_names(self):
        doc=copy.deepcopy(self.cart); doc['definitions']['components'][0]='<script>bad</script>'
        rendered=am.schematic(doc)
        self.assertNotIn('<script>bad</script>',rendered)
        self.assertIn('&lt;script&gt;',rendered)


if __name__=='__main__': unittest.main()


