from math import pi
import random,unittest
from joint_models import constraint_pair_tiers,hinge_angle_limits,ballscrew_step,winch_step


class JointModelTests(unittest.TestCase):
    def test_constraint_tiers_are_per_peer_not_a_whole_graph_tier(self):
        tiers=constraint_pair_tiers([(1,100,1),(2,100,2),(3,200,1)])
        self.assertEqual(tiers,{100:2,200:1})
        self.assertGreater(tiers[100],1);self.assertEqual(tiers[200],1)

    def test_seeded_tier_order_and_added_link_monotonicity(self):
        rng=random.Random(25904830)
        for _ in range(500):
            links=[(i,rng.randrange(5),rng.randrange(3)) for i in range(20)]
            expected=constraint_pair_tiers(links);rng.shuffle(links)
            self.assertEqual(constraint_pair_tiers(links),expected)
            extended=constraint_pair_tiers(links+[(99,0,2)])
            self.assertGreaterEqual(extended[0],expected.get(0,0))

    def test_hinge_interpolation_and_degenerate_interval(self):
        self.assertEqual(hinge_angle_limits(0,pi,0,1),(0,pi))
        for factors in [(.5,.5),(1,0)]:
            low,high=hinge_angle_limits(0,pi,*factors)
            self.assertAlmostEqual(high-low,.02)
            self.assertAlmostEqual((low+high)/2,pi/2)

    def test_ballscrew_strict_endpoint_brake_and_constraint_state(self):
        out=ballscrew_step(1,0,2,0,.1,10)
        self.assertEqual((out['target'],out['brake']),(1,0))
        self.assertEqual(ballscrew_step(0,0,2,0,.1,10)['brake'],.99)
        out=ballscrew_step(1,0,2,10,.1,10,constraint_added=False)
        self.assertEqual(out['target'],1);self.assertEqual(out['brake'],.99)

    def test_ballscrew_mass_cancellation_and_final_brake_counterexample(self):
        for mass in [0,1,10,1000]:
            out=ballscrew_step(1,0,2,.1,.01,mass)
            self.assertAlmostEqual(out['torque_argument']/out['node_mass'],out['pending_speed_delta'])
        blocked=ballscrew_step(2,0,2,0,.1,10);free=ballscrew_step(1,0,2,0,.1,20)
        self.assertEqual([blocked['brake'],free['brake']],[.99,0])

    def test_winch_release_polarity_and_load_without_attached_rope(self):
        for release in [-1,1]:
            out=winch_step(10,.1,release,[(1,1)])
            self.assertEqual((out['advance'],out['lengths']),(0,[1]))
        out=winch_step(1,.1,0,[])
        self.assertAlmostEqual(out['torque_argument'],-10*out['advance'])
        self.assertGreater(out['advance'],0)

    def test_winch_strict_bounds_stretch_direction_and_multiple_ropes(self):
        self.assertEqual(winch_step(0,.1,0,[(.5,1)])['brake'],.99)
        self.assertEqual(winch_step(0,.1,0,[(20,1)])['brake'],.99)
        self.assertEqual(winch_step(-.1,.1,0,[(2,1.21)])['lengths'],[2])
        self.assertGreater(winch_step(.1,.1,0,[(2,1.21)])['lengths'][0],2)
        out=winch_step(.1,.1,0,[(20,1),(2,1)])
        self.assertEqual(out['brake'],.99);self.assertGreater(out['lengths'][1],2)

    def test_explicit_model_domain_guards(self):
        for thunk in [lambda:constraint_pair_tiers([(True,1,1)]),lambda:hinge_angle_limits(0,pi,2,1),
                      lambda:ballscrew_step(0,1,0,0,.1,1),lambda:winch_step(0,.1,2,[]),
                      lambda:winch_step(float('nan'),.1,0,[])]:
            with self.assertRaises(ValueError):thunk()


if __name__=='__main__':unittest.main()
