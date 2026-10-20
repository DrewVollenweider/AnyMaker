import math,random,unittest
from powertrain_models import (TorqueNode,alternator_step,applied_delta,build_rps,
 ground_effect_extra,island_post_build,motor_request,rotor_step,swashplate_mix)


class PowertrainTests(unittest.TestCase):
    def test_pending_delta_and_native_damping(self):
        self.assertEqual(applied_delta(2,12,3),6)
        self.assertAlmostEqual(build_rps(10,6),15.9968)

    def test_engaged_island_conserves_weighted_momentum_and_ratios(self):
        rng=random.Random(25904830)
        for _ in range(500):
            nodes=[TorqueNode(rng.uniform(-30,30),rng.uniform(.1,20),rng.choice([-3,-1,.5,2]),
                              island_ratio=rng.choice([-2,-1,1,2])) for _ in range(rng.randrange(1,8))]
            result=island_post_build(nodes)
            before=sum(n.mass*n.ratio*n.island_ratio*n.rps for n in nodes)
            after=sum(n.mass*n.ratio*n.island_ratio*r for n,r in zip(nodes,result))
            self.assertAlmostEqual(before,after,places=9)
            normalized=[r/(n.ratio*n.island_ratio) for n,r in zip(nodes,result)]
            self.assertLess(max(normalized)-min(normalized),1e-10)

    def test_mass_and_ratio_counterexamples(self):
        self.assertEqual(island_post_build([TorqueNode(10,1),TorqueNode(0,9)]),(1,1))
        a,b=island_post_build([TorqueNode(10,1),TorqueNode(0,1,ratio=2)])
        self.assertAlmostEqual(a,2);self.assertAlmostEqual(b,4)

    def test_partial_clutch_has_two_contributions_and_lerp(self):
        self.assertEqual(island_post_build([TorqueNode(10,1,clutch=.5)]),(7.5,))
        self.assertEqual(island_post_build([TorqueNode(10,1,clutch=0)]),(10,))

    def test_brakes_multiply_shared_numerator(self):
        result=island_post_build([TorqueNode(10,1,brake=.5),TorqueNode(10,1,brake=.5)])
        self.assertEqual(result,(2.5,2.5))
        self.assertEqual(island_post_build([TorqueNode(10,1),TorqueNode(10,1,brake=1)]),(0,0))
        # A zero-clutch node still participates in the separate brake loop.
        self.assertEqual(island_post_build([TorqueNode(10,1),TorqueNode(20,1,clutch=0,brake=1)]),(0,20))

    def test_motor_direction_and_overspeed_no_regeneration(self):
        self.assertEqual(motor_request(0,30,30,10000,1,1,.02),(1,200))
        self.assertEqual(motor_request(40,30,30,10000,1,1,.02),(0,0))
        self.assertEqual(motor_request(-40,-30,30,10000,1,1,.02),(0,0))
        self.assertEqual(motor_request(10,0,30,10000,1,1,.02),(0,0))
        self.assertEqual(motor_request(0,30,30,10000,1,1,.02,True,False),(-1,200))
        self.assertEqual(motor_request(0,30,30,10000,1,1,.02,True,True),(1,200))

    def test_alternator_efficiency_capacity_and_shaft_sign(self):
        q,p,a=alternator_step(100,100,1500,0,1500,.02)
        self.assertEqual((q,p),(22.5,1125));self.assertEqual(a,-1.2)
        self.assertEqual(alternator_step(-100,100,1500,1500,1500,.02),(1500,0,0))
        self.assertEqual(alternator_step(-100,100,1500,0,1500,.02)[2],1.2)

    def test_swashplate_mixing_and_saturation(self):
        self.assertEqual(swashplate_mix(1,1,1),(1,0,0))
        self.assertEqual(swashplate_mix(0,-1,1),(0,0,1))
        self.assertEqual(swashplate_mix(-1,1,1),(1,-1,0))

    def test_rotor_symmetry_reversal_and_installed_blades(self):
        a,load,retain=rotor_step(5,2,4,.02,.5)
        b,revload,revretain=rotor_step(-5,2,4,.02,.5)
        self.assertEqual(a,tuple(-v for v in b));self.assertEqual(load,-revload)
        self.assertEqual(retain,revretain)
        self.assertLess(load,0);self.assertGreater(retain,0);self.assertLess(retain,1)
        a0,load0,retain0=rotor_step(5,2,0,.02,.5)
        self.assertEqual(a0,(0,0,0,0));self.assertLess(load0,0);self.assertEqual(retain0,1)

    def test_rotor_cyclic_zero_net_at_zero_collective(self):
        for pitch,roll in [(.2,.8),(-.9,.1),(1,1)]:
            impulses,load,_=rotor_step(5,2,4,.02,0,pitch,roll)
            self.assertAlmostEqual(sum(impulses),0)
            self.assertLess(load,0)

    def test_ground_effect_endpoints_monotonic(self):
        self.assertEqual(ground_effect_extra(0),1)
        self.assertEqual(ground_effect_extra(16),.25)
        self.assertEqual(ground_effect_extra(32),0)
        values=[ground_effect_extra(x) for x in range(33)]
        self.assertEqual(values,sorted(values,reverse=True))

    def test_model_guards_are_explicit(self):
        for node in [TorqueNode(1,0),TorqueNode(1,1,ratio=0),TorqueNode(math.nan,1),TorqueNode(1,1,clutch=2)]:
            with self.assertRaises(ValueError):island_post_build([node])
        with self.assertRaises(ValueError):rotor_step(1,1,True,.02,0)
        with self.assertRaises(ValueError):ground_effect_extra(33)
        with self.assertRaises(ValueError):alternator_step(1,1,1,2,1,.02)


if __name__=='__main__':unittest.main()
