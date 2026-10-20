import random,unittest
from survival_models import condition_clock,vital_flags,stamina_step,clothing_wetness_step,insulation,effective_temperature


class SurvivalModelTests(unittest.TestCase):
    def test_condition_cadence_is_61_calls_not_60(self):
        counter=0;passes=[]
        for call in range(1,184):
            counter,ran=condition_clock(counter)
            if ran:passes.append(call)
        self.assertEqual(passes,[61,122,183]);self.assertEqual(counter,0)

    def test_warning_and_critical_do_not_overlap(self):
        self.assertEqual(vital_flags(.5),dict(value=.5,warning=True,critical=False))
        self.assertFalse(vital_flags(.5000001)['warning'])
        self.assertEqual(vital_flags(-1),dict(value=0,warning=False,critical=True))
        self.assertEqual(vital_flags(2)['value'],1)

    def test_jump_edge_can_coexist_with_recovery(self):
        dt=1/60
        first=stamina_step(1,0,dt,jump=True)
        self.assertAlmostEqual(first['value'],1-.05+dt/90)
        held=stamina_step(first['value'],0,dt,jump=True,previous_jump=True)
        self.assertAlmostEqual(held['value'],first['value']+dt/90)
        self.assertFalse(first['draining'])

    def test_stamina_thresholds_additive_drains_and_time_partition(self):
        self.assertFalse(stamina_step(.5,2,.1,sprint=True)['draining'])
        self.assertFalse(stamina_step(.5,.5,.1,swim=True)['draining'])
        both=stamina_step(1,4,1,sprint=True,swim=True)
        self.assertAlmostEqual(both['value'],1-2/45)
        half=stamina_step(1,3,.5,sprint=True)
        half=stamina_step(half['value'],3,.5,sprint=True)
        self.assertAlmostEqual(half['value'],stamina_step(1,3,1,sprint=True)['value'])

    def test_soaking_priority_and_temperature_boundary(self):
        # Submergence below current wetness falls through to rain/drying.
        self.assertAlmostEqual(clothing_wetness_step(.5,0,.4,15,0),.5-1/1200)
        self.assertAlmostEqual(clothing_wetness_step(.5,0,.4,15.0001,0),.5-1/600)
        self.assertAlmostEqual(clothing_wetness_step(.5,1,.55,0,25),.55)
        self.assertEqual(clothing_wetness_step(.5,1,0,0,25),.5)

    def test_seeded_resistance_and_insulation_monotonicity(self):
        rng=random.Random(25904830)
        for _ in range(500):
            w,r=rng.random(),rng.random();a=rng.random()*30;b=a+rng.random()*30
            self.assertGreaterEqual(clothing_wetness_step(w,r,0,20,a),clothing_wetness_step(w,r,0,20,b))
            self.assertGreaterEqual(insulation(90,w),insulation(90,min(1,w+.1)))
        self.assertAlmostEqual(insulation(90,1),9)

    def test_effective_temperature_separates_weather_wetness_and_motion(self):
        exposed=effective_temperature(20,0,1,1,1,0)
        sheltered=effective_temperature(20,0,1,1,1,0,sheltered=True)
        self.assertEqual(sheltered-exposed,10)
        self.assertEqual(effective_temperature(20,0,0,0,0,1),15)

    def test_explicit_model_domain(self):
        for thunk in [lambda:condition_clock(True),lambda:stamina_step(1,-1,.1),
                      lambda:clothing_wetness_step(2,0,0,0,0),lambda:insulation(1,float('nan'))]:
            with self.assertRaises(ValueError):thunk()


if __name__=='__main__':unittest.main()
