import random,unittest
from ai_models import actor_ranges,vehicle_ranges,actor_eligible,zombie_factor,weighted_selection


class AIModelTests(unittest.TestCase):
    def test_floor_sleep_and_zombie_order_counterexample(self):
        self.assertEqual(actor_ranges(0,0,0,1,0,0), (3,1))
        v,a=actor_ranges(0,0,0,1,0,0,sleeping=True,zombie_factor=.8)
        self.assertAlmostEqual(v,.24);self.assertAlmostEqual(a,.32)

    def test_stationary_crouched_and_moving_audio(self):
        self.assertEqual(actor_ranges(100,100,1,0,1,0)[1],1)
        self.assertEqual(actor_ranges(100,100,4,0,1,0)[1],100)
        self.assertEqual(actor_ranges(100,100,4,0,1,0,crouched=True)[1],2)

    def test_vehicle_sleep_is_distinct_from_actor_sleep(self):
        self.assertEqual(vehicle_ranges(100,20,0,1,sleeping=True),vehicle_ranges(100,20,0,1))
        self.assertNotEqual(actor_ranges(100,20,4,0,1,0,sleeping=True),actor_ranges(100,20,4,0,1,0))

    def test_seeded_fog_light_speed_monotonicity(self):
        rng=random.Random(25904830)
        for _ in range(500):
            fog,day,light,speed=[rng.random() for _ in range(4)]
            v,a=actor_ranges(100,30,4*speed,fog,day,light)
            self.assertLessEqual(actor_ranges(100,30,4*speed,min(1,fog+.1),day,light)[0],v+1e-12)
            self.assertGreaterEqual(actor_ranges(100,30,4*speed,fog,day,min(1,light+.1))[0],v-1e-12)
            self.assertGreaterEqual(actor_ranges(100,30,4*speed+.1,fog,day,light)[1],a)

    def test_category_flags_teams_incapacity_and_prey(self):
        self.assertTrue(actor_eligible('character',1,0,0))
        self.assertFalse(actor_eligible('character',31,1,1))
        self.assertFalse(actor_eligible('character',1,0,0,incapacitated=True))
        self.assertTrue(actor_eligible('character',17,0,0,incapacitated=True))
        self.assertFalse(actor_eligible('creature',31,0,0,behavior='prey'))
        self.assertTrue(actor_eligible('creature',2,0,0,behavior='predator'))
        for flags in range(32):self.assertFalse(actor_eligible('zombie',flags,0,1,invisible=True))

    def test_zombie_factor_period_and_ordinary_bounds(self):
        for ident in range(100):
            self.assertEqual(zombie_factor(ident),zombie_factor(ident+9))
            self.assertTrue(.8<=zombie_factor(ident)<=1)
        self.assertEqual(zombie_factor(0),.8);self.assertEqual(zombie_factor(8),1)

    def test_supplied_weighted_draw_boundary_and_zero_weights(self):
        self.assertEqual(weighted_selection([2,3],2),0)
        self.assertEqual(weighted_selection([2,3],2.0001),1)
        self.assertEqual(weighted_selection([0,1],0),0)
        self.assertEqual(weighted_selection([0,0],0),0)

    def test_explicit_ordinary_model_domain(self):
        for thunk in [lambda:actor_ranges(1,1,-1,0,0,0),lambda:vehicle_ranges(1,1,2,0),
                      lambda:vehicle_ranges(1,1,0,float('nan')),
                      lambda:zombie_factor(-1),lambda:weighted_selection([],0),lambda:actor_eligible('prop',1,0,0)]:
            with self.assertRaises(ValueError):thunk()


if __name__=='__main__':unittest.main()
