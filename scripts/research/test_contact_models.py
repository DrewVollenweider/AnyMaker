import math,random,unittest
from contact_models import (friction_circle,load_sensitive_grip,pneumatic_brake,
 support_reaction_scale,suspension_load)


class ContactTests(unittest.TestCase):
    def test_compression_boundaries_and_bump_stop(self):
        self.assertEqual(suspension_load(1,1,1,1,0,1,1,0,0,1),(1,4,4))
        self.assertEqual(suspension_load(2,1,1,1,0,1,1,0,0,1),(0,0,0))
        self.assertEqual(suspension_load(1,1,1,1,0,1,1,0,2,1),(1,12,12))

    def test_settings_square_not_linear(self):
        full=suspension_load(1.5,1,1,1,0,1,1,0,0,1)[1]
        half=suspension_load(1.5,1,1,1,0,.5,1,0,0,1)[1]
        self.assertEqual(half,full/4)

    def test_rebound_no_tension_and_mass_cap(self):
        self.assertEqual(suspension_load(2,1,1,0,1,1,1,1,0,1),(0,-8,0))
        a=suspension_load(1,1,1,1,0,1,1,0,0,1000)[2]
        b=suspension_load(1,1,1,1,0,1,1,0,0,5000)[2]
        self.assertEqual(a,b)

    def test_roll_correction_separate_from_grip_base(self):
        c,base,normal=suspension_load(1.5,1,1,1,0,1,1,0,0,2,roll_term=.5)
        self.assertEqual((c,base,normal),(.5,2,8))

    def test_load_history_and_sensitivity_floor(self):
        self.assertEqual(load_sensitive_grip(10,0,.5),(10,10))
        avg,grip=load_sensitive_grip(100,1,1)
        self.assertAlmostEqual(avg,1.297);self.assertEqual(grip,20)
        self.assertEqual(load_sensitive_grip(-10,0,1),(0,0))

    def test_friction_circle_combines_axes_and_projects_normal(self):
        result=friction_circle((3,99,4),(0,1,0),2)
        for actual,expected in zip(result,(1.2,0,1.6)):self.assertAlmostEqual(actual,expected)
        self.assertAlmostEqual(sum(x*x for x in result),4)
        self.assertEqual(friction_circle((0,5,0),(0,1,0),2),(0,0,0))

    def test_seeded_friction_cap_and_orthogonality(self):
        rng=random.Random(4435340)
        for _ in range(500):
            n=[rng.uniform(-1,1) for _ in range(3)];length=math.sqrt(sum(x*x for x in n))
            n=[x/length for x in n];v=[rng.uniform(-100,100) for _ in range(3)];cap=rng.uniform(0,10)
            result=friction_circle(v,n,cap)
            self.assertLessEqual(sum(x*x for x in result),cap*cap+1e-10)
            self.assertAlmostEqual(sum(x*y for x,y in zip(result,n)),0,places=10)

    def test_pneumatic_brake_is_fail_applied(self):
        self.assertEqual([pneumatic_brake(p) for p in [0,4,5,6,20]],[1,1,.5,0,0])

    def test_support_reaction_and_explicit_domain(self):
        self.assertEqual(support_reaction_scale(100,1000),.1)
        self.assertEqual(support_reaction_scale(2000,1000),1)
        with self.assertRaises(ValueError):friction_circle((1,2,3),(0,2,0),1)
        with self.assertRaises(ValueError):friction_circle((1,2),(0,1,0),1)
        with self.assertRaises(ValueError):pneumatic_brake(math.nan)


if __name__=='__main__':unittest.main()
