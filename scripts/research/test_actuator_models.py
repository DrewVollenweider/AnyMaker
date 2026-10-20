import random,unittest
from actuator_models import hydraulic_chambers,cylinder_geometry,measured_cylinder_extension


class ActuatorModelTests(unittest.TestCase):
    def test_empty_chambers_retain_geometry_and_full_chambers_fix_ratio(self):
        self.assertEqual(hydraulic_chambers(0,0,10,.7).extension,.7)
        for measured in [0,.2,.8,1]:
            self.assertAlmostEqual(hydraulic_chambers(3,7,10,measured).extension,.3)

    def test_underfilled_volume_allows_an_interval(self):
        self.assertAlmostEqual(hydraulic_chambers(2,3,10,0).extension,.2)
        self.assertAlmostEqual(hydraulic_chambers(2,3,10,1).extension,.7)
        self.assertAlmostEqual(hydraulic_chambers(2,3,10,.5).extension,.5)

    def test_overfilled_ratio_and_capacity_update_order(self):
        result=hydraulic_chambers(8,4,10,.1)
        self.assertAlmostEqual(result.extension,2/3)
        self.assertEqual((result.capacity_a_written,result.capacity_b_written),(1,9))
        # These writes describe the incoming geometry, not the corrected target.
        next_tick=hydraulic_chambers(8,4,10,result.extension)
        self.assertAlmostEqual(next_tick.capacity_a_written,20/3)

    def test_seeded_volume_feasibility_and_capacity_sum(self):
        rng=random.Random(25904830)
        for _ in range(1000):
            capacity=rng.uniform(.1,100);a=rng.random()*capacity;b=rng.random()*(capacity-a)
            out=hydraulic_chambers(a,b,capacity,rng.random())
            self.assertGreaterEqual(out.extension+1e-12,a/capacity)
            self.assertLessEqual(out.extension-1e-12,1-b/capacity)
            self.assertAlmostEqual(out.capacity_a_written+out.capacity_b_written,capacity)

    def test_size_variants_target_max_and_geometry_round_trip(self):
        for margin,rate in [(.16,8),(.20,16),(.24,24)]:
            for cells in [8,16,32]:
                for extension in [0,.2,.5,1]:
                    length,capacity,target,stroke=cylinder_geometry(cells,margin,rate,extension)
                    self.assertAlmostEqual(capacity,length*rate)
                    self.assertAlmostEqual(measured_cylinder_extension(target,cells,margin),extension)
                    self.assertAlmostEqual(cylinder_geometry(cells,margin,rate,1)[2],length)

    def test_model_domain_guards_are_explicit(self):
        for args in [(-1,0,10,.5),(0,0,0,.5),(0,0,10,2),(0,0,10,float('nan'))]:
            with self.assertRaises(ValueError):hydraulic_chambers(*args)
        for args in [(True,.16,8,0),(1,.16,8,0),(8,.16,0,0)]:
            with self.assertRaises(ValueError):cylinder_geometry(*args)


if __name__=='__main__':unittest.main()
