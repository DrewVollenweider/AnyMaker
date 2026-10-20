import math,random,unittest
from gas_thermal_models import Content,blend_temperatures,equalize_gas,move_gas


class GasThermalTests(unittest.TestCase):
    def test_gas_destination_capacity_does_not_limit_move(self):
        a=Content((8,2),10,80);b=Content((0,0),1,20)
        a,b,moved=move_gas(a,b,100)
        self.assertEqual((a.quantity,b.quantity,moved),(0,10,10))
        self.assertEqual((b.pressure,b.temperature),(10,80))

    def test_move_conserves_species_and_quantity_temperature_moment(self):
        rng=random.Random(25904830)
        for _ in range(500):
            a=Content(tuple(rng.random()*10 for _ in range(3)),1,rng.uniform(-10,100))
            b=Content(tuple(rng.random()*10 for _ in range(3)),1,rng.uniform(-10,100))
            x,y,_=move_gas(a,b,rng.random()*30)
            for before,after in zip((u+v for u,v in zip(a.parts,b.parts)),(u+v for u,v in zip(x.parts,y.parts))):
                self.assertAlmostEqual(before,after)
            self.assertAlmostEqual(a.quantity*a.temperature+b.quantity*b.temperature,
                                   x.quantity*x.temperature+y.quantity*y.temperature,places=9)

    def test_pair_overload_temperature_counterexample(self):
        a=Content((10,0),10,100);b=Content((0,0),30,0)
        x,y=equalize_gas([a,b],pair_overload=True)
        self.assertEqual((x.quantity,y.quantity),(2.5,7.5))
        self.assertEqual((x.temperature,y.temperature),(100,0))
        # Species are conserved, but this is not the vector thermal operation.
        self.assertNotEqual(x.quantity*x.temperature+y.quantity*y.temperature,
                            a.quantity*a.temperature+b.quantity*b.temperature)
        x,y=equalize_gas([a,b])
        self.assertEqual((x.temperature,y.temperature),(100,100))

    def test_vector_equalization_pressure_and_species(self):
        contents=[Content((5,1),2,20),Content((0,4),8,60),Content((1,0),1,10)]
        out=equalize_gas(contents)
        for x in out:self.assertAlmostEqual(x.pressure,1)
        self.assertEqual(tuple(sum(x.parts[i] for x in out) for i in range(2)),(6,5))
        self.assertAlmostEqual(sum(x.quantity*x.temperature for x in out),370)

    def test_heat_blend_preserves_weighted_mean_and_difference_decay(self):
        rng=random.Random(4435340)
        for _ in range(500):
            a,b=rng.random()*10,rng.random()*10;ta,tb=rng.uniform(-50,150),rng.uniform(-50,150);f=rng.random()
            x,y=blend_temperatures(a,ta,b,tb,f)
            self.assertAlmostEqual(a*x+b*y,a*ta+b*tb,places=9)
            self.assertAlmostEqual(y-x,(tb-ta)*(1-f),places=9)

    def test_empty_and_explicit_model_domains(self):
        self.assertEqual(blend_temperatures(0,5,0,10,.5),(5,10))
        self.assertEqual(Content((1,),0,20).pressure,0)
        a,b=Content((1,),1,20),Content((2,),1,30)
        self.assertEqual(move_gas(a,b,-1),(a,b,0))
        with self.assertRaises(ValueError):Content((math.nan,),1,0)
        with self.assertRaises(ValueError):equalize_gas([a],pair_overload=True)
        with self.assertRaises(ValueError):blend_temperatures(1,0,1,100,2)


if __name__=='__main__':unittest.main()
