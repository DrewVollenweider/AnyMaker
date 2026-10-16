import copy
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import anymaker as am


class SystemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cart=am.load(ROOT.parent/'exploration/baseline/steercart.data')
        cls.catalog=am.definitions()

    def test_real_cart_reports_links_without_runtime_certification(self):
        r=am.systems_review(self.cart,self.catalog)
        self.assertTrue(r['review_available'])
        self.assertEqual(r['functional_status'],'unverified')
        handbrake=next(c for c in r['components'] if c['definition']=='handbrake')
        expected=[x for x in am.vehicles(self.cart)[0]['mechanical_links']
                  if any(x[p]['comp']==handbrake['id'] for p in ('p0','p1'))]
        self.assertEqual(len(handbrake['direct_saved_links']),len(expected))
        self.assertTrue(all(q['status']=='unverified' for q in handbrake['requirements']))

    def test_port_wiring_does_not_certify_its_consumer(self):
        doc={'definitions':{'components':['microcontroller','electric_port']},
             'vehicles':{'vehicles':[{'id':1,'grids':[{'components':[
                 {'id':1,'def':0},{'id':2,'def':1},{'id':3,'def':1}]}],
                 'electric_links':[{'p0':{'comp':2},'p1':{'comp':3}}]}]}}
        r=am.systems_review(doc,self.catalog)
        c=next(x for x in r['components'] if x['id']==1)
        self.assertEqual(c['direct_saved_links'],[])
        self.assertTrue(c['requirements'])
        self.assertTrue(all(q['status']=='unverified' for q in c['requirements']))
        self.assertEqual(r['functional_status'],'unverified')

    def test_missing_channel_direction_stays_unknown(self):
        doc={'definitions':{'components':['electric_motor_a']},
             'vehicles':{'vehicles':[{'id':1,'grids':[{'components':[{'id':1,'def':0}]}]}]}}
        r=am.systems_review(doc,self.catalog)
        channels={x['name']:x for x in r['components'][0]['data_channels']}
        self.assertEqual(channels['is_reverse']['direction'],'unknown')
        self.assertEqual(channels['target_rps']['direction'],'input')
        self.assertEqual(channels['rps']['direction'],'output')

    def test_invalid_creation_withholds_system_review(self):
        doc=copy.deepcopy(self.cart); am.components(am.vehicles(doc)[0])[0]['def']=999999
        r=am.systems_review(doc,self.catalog)
        self.assertFalse(r['review_available']); self.assertEqual(r['components'],[])
        self.assertIn('withheld',am.systems_markdown(r))

    def test_results_cannot_mutate_source_link_fields(self):
        doc=copy.deepcopy(self.cart); before=copy.deepcopy(doc)
        r=am.systems_review(doc,self.catalog)
        linked=next(c for c in r['components'] if c['direct_saved_links'])
        linked['direct_saved_links'][0]['endpoints']['p0']['comp']=999
        self.assertEqual(doc,before)

    def test_frame_only_and_unknown_components_do_not_invent_requirements(self):
        frame={'definitions':{},'vehicles':{'vehicles':[{'id':1}]}}
        self.assertEqual(am.systems_review(frame,self.catalog)['components'],[])
        unknown={'definitions':{'components':['<script>unknown</script>']},
                 'vehicles':{'vehicles':[{'id':1,'grids':[{'components':[{'id':1,'def':0}]}]}]}}
        r=am.systems_review(unknown,self.catalog)
        self.assertFalse(r['components'][0]['definition_known'])
        self.assertEqual(r['components'][0]['requirements'],[])
        self.assertEqual(r['components'][0]['rule_coverage'],'definition_only')
        self.assertNotIn('<script>',am.systems_markdown(r))

if __name__=='__main__': unittest.main()
