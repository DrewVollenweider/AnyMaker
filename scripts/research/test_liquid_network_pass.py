"""Conservation and counterexamples for a scoped source-shaped group visit."""
import math,random,unittest
from liquid_network_pass import Port,visit


class LiquidNetworkPassTests(unittest.TestCase):
    def test_two_port_mixture_transfer(self):
        r=visit([Port(0,(0,0,0,0),2),Port(20,(.5,.5,0,0),2,100)])
        for actual,want in zip(r['ports'][0]['amounts'],(.2,.2,0,0)):self.assertAlmostEqual(actual,want)
        self.assertAlmostEqual(r['ports'][0]['volume'],.4)
        self.assertEqual(r['ports'][0]['temperature'],100)
        self.assertAlmostEqual(sum(p['flow'] for p in r['ports']),0)

    def test_multiple_candidates_can_overfill_nonexpandable_sink(self):
        r=visit([Port(0,(0,0,0,0),.1),Port(10,(1,0,0,0),1),Port(20,(0,1,0,0),1)])
        self.assertAlmostEqual(r['ports'][0]['volume'],.2)
        self.assertGreater(r['ports'][0]['volume'],r['ports'][0]['capacity'])
        self.assertAlmostEqual(sum(p['volume'] for p in r['ports']),2)

    def test_lower_sink_consumes_stock_before_later_sink(self):
        r=visit([Port(0,(0,0,0,0),2),Port(1,(0,0,0,0),2),Port(100,(1,0,0,0),1)])
        self.assertEqual([p['volume'] for p in r['ports']],[1,0,0])

    def test_equal_head_sort_preserves_input_priority(self):
        r=visit([Port(0,(0,0,0,0),2),Port(0,(0,0,0,0),2),Port(100,(1,0,0,0),1)])
        self.assertEqual(r['order'],(0,1,2));self.assertEqual([p['volume'] for p in r['ports']],[1,0,0])

    def test_expandable_flag_skips_per_candidate_room_cap(self):
        a=visit([Port(0,(0,0,0,0),.1),Port(20,(1,0,0,0),1)])
        b=visit([Port(0,(0,0,0,0),.1,expandable=True),Port(20,(1,0,0,0),1)])
        self.assertAlmostEqual(a['ports'][0]['volume'],.1);self.assertAlmostEqual(b['ports'][0]['volume'],.4)

    def test_equal_heads_do_not_capacity_equalize(self):
        r=visit([Port(5,(1,0,0,0),2),Port(5,(0,0,0,0),2)])
        self.assertEqual([p['volume'] for p in r['ports']],[1,0]);self.assertEqual(r['moves'],[])

    def test_seeded_species_volume_and_temperature_moment(self):
        rng=random.Random(58808739)
        for _ in range(300):
            ports=[]
            for _ in range(rng.randint(2,7)):
                a=tuple(rng.uniform(0,2) for _ in range(4));ports.append(Port(rng.uniform(-20,20),a,sum(a)+rng.uniform(.1,5),rng.uniform(-20,120)))
            r=visit(ports)['ports']
            for k in range(4):self.assertAlmostEqual(sum(p.amounts[k] for p in ports),sum(p['amounts'][k] for p in r),places=9)
            self.assertAlmostEqual(sum(sum(p.amounts) for p in ports),sum(p['volume'] for p in r),places=9)
            self.assertAlmostEqual(sum(sum(p.amounts)*p.temperature for p in ports),sum(p['volume']*p['temperature'] for p in r),places=8)
            self.assertTrue(all(min(p['amounts'])>=-1e-12 and p['volume']>=-1e-12 for p in r))

    def test_explicit_domain_and_input_preservation(self):
        p=Port(1,(1,0,0,0),2);visit([p]);self.assertEqual(p.amounts,(1,0,0,0))
        with self.assertRaises(ValueError):visit([p,p])
        for args in [(0,(1,0,0),2),(0,(-1,0,0,0),2),(0,(2,0,0,0),1),(math.nan,(0,0,0,0),1)]:
            with self.assertRaises(ValueError):Port(*args)
        self.assertEqual(visit([])['ports'],[])


if __name__=='__main__':unittest.main()
