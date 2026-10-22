"""Boundary, dimensional and independent-supply checks for the engine model."""
import math,random,unittest
from engine_demand import AIR_PER_FUEL,consume,demand


class EngineDemandTests(unittest.TestCase):
    def test_speed_cutoff_boundaries(self):
        self.assertEqual(demand(100,math.nextafter(6,-math.inf),1)['fuel'],0)
        self.assertGreater(demand(100,6,1)['fuel'],0)
        maximum=8000/60
        self.assertGreater(demand(100,maximum,1)['fuel'],0)
        self.assertEqual(demand(100,math.nextafter(maximum,math.inf),1)['fuel'],0)

    def test_volume_and_tick_rate_scaling(self):
        a=demand(10,60,.5)['fuel']
        self.assertAlmostEqual(demand(20,60,.5)['fuel'],2*a)
        self.assertAlmostEqual(demand(10,60,.5,rate=30)['fuel'],2*a)

    def test_pressure_and_throttle_limits(self):
        a=demand(100,100,1)['fuel']
        self.assertAlmostEqual(demand(100,100,1,intake_pressure=10)['fuel'],2*a)
        self.assertEqual(demand(100,100,1,intake_pressure=100)['fuel'],demand(100,100,1,intake_pressure=10)['fuel'])
        self.assertEqual(demand(100,100,1,exhaust_pressure=4)['fuel'],a)
        self.assertAlmostEqual(demand(100,100,1,exhaust_pressure=12)['fuel'],a/2)
        self.assertEqual(demand(100,100,1,exhaust_pressure=20)['fuel'],0)
        self.assertEqual(demand(100,100,0)['fuel'],0)

    def test_full_supply_energy_and_declared_air_ratio(self):
        r=demand(100,8000/60,1);c=consume(r['fuel'],r['air'],r['air'],r['fuel'])
        self.assertEqual(AIR_PER_FUEL,8720)
        self.assertAlmostEqual(c['energy']*60,100*400)
        self.assertAlmostEqual(c['fuel'],r['fuel'])

    def test_air_starvation_does_not_reduce_independent_fuel_draw(self):
        a=consume(.001,8.72,8.72,.001);b=consume(.001,4.36,4.36,.001)
        self.assertEqual(a['fuel'],b['fuel'])
        self.assertAlmostEqual(b['energy'],a['energy']/2)

    def test_fuel_starvation_does_not_reduce_independent_gas_draw(self):
        a=consume(.001,8.72,8.72,.001);b=consume(.001,8.72,8.72,.0005)
        self.assertEqual(a['gas'],b['gas'])
        self.assertAlmostEqual(b['energy'],a['energy']/2)

    def test_contamination_and_damage_are_energy_factors_after_draw(self):
        a=consume(.001,8.72,8.72,.001)
        self.assertAlmostEqual(consume(.001,8.72,4.36,.001)['energy'],a['energy']/2)
        for stage,factor in [(1,.5),(2,0)]:
            b=consume(.001,8.72,8.72,.001,stage)
            self.assertEqual(b['fuel'],a['fuel']);self.assertEqual(b['gas'],a['gas'])
            self.assertAlmostEqual(b['energy'],a['energy']*factor)

    def test_seeded_stock_and_energy_bounds(self):
        rng=random.Random(26113663)
        for _ in range(500):
            f=rng.uniform(.00001,.1);g=rng.uniform(.01,1000);air=g*rng.random();p=rng.uniform(.00001,.2)
            c=consume(f,g,air,p)
            self.assertLessEqual(c['gas'],g+1e-10);self.assertLessEqual(c['fresh_air'],air+1e-10)
            self.assertLessEqual(c['fuel'],min(f,p)+1e-12)
            self.assertGreaterEqual(c['energy'],0);self.assertLessEqual(c['energy'],c['fuel']*9600000+1e-8)

    def test_explicit_model_domain(self):
        with self.assertRaises(ValueError):demand(1.5,60,1)
        with self.assertRaises(ValueError):demand(10,math.nan,1)
        with self.assertRaises(ValueError):consume(.1,0,0,1)
        with self.assertRaises(ValueError):consume(.1,1,2,1)
        self.assertEqual(consume(0,0,0,0)['energy'],0)


if __name__=='__main__':unittest.main()
