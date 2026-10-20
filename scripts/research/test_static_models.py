"""Conservation, ordering, and boundary counterexamples for offline arithmetic.

These independently check model invariants; passing is not native execution.
"""
import math
import random
import unittest

from static_models import Liquid,consume_sequence,debit_sources,equalize_liquids,loop_iterations,move_liquid


class ConservationTests(unittest.TestCase):
    def test_species_volume_and_temperature_moment_conserved(self):
        rng=random.Random(25904830)
        for _ in range(500):
            parts=tuple(rng.uniform(0,100) for _ in range(4))
            other=tuple(rng.uniform(0,100) for _ in range(4))
            source=Liquid(parts,sum(parts)+rng.uniform(0,100),rng.uniform(-20,120))
            destination=Liquid(other,sum(other)+rng.uniform(0,100),rng.uniform(-20,120))
            a,b,moved=move_liquid(source,destination,rng.uniform(0,1000))
            for i in range(4):self.assertAlmostEqual(a.parts[i]+b.parts[i],parts[i]+other[i],places=10)
            self.assertAlmostEqual(a.quantity+b.quantity,source.quantity+destination.quantity,places=10)
            self.assertAlmostEqual(a.quantity*a.temperature+b.quantity*b.temperature,
                source.quantity*source.temperature+destination.quantity*destination.temperature,places=8)
            self.assertGreaterEqual(a.quantity,-1e-10)
            self.assertLessEqual(b.quantity,destination.capacity+1e-10)
            self.assertLessEqual(moved,source.quantity)

    def test_full_destination_and_empty_source_cannot_create_liquid(self):
        full=Liquid((2,3),5,25);source=Liquid((10,0),10,80);empty=Liquid((0,0),10,20)
        self.assertEqual(move_liquid(source,full,10),(source,full,0))
        self.assertEqual(move_liquid(empty,source,10),(empty,source,0))

    def test_overfill_returns_negative_candidate_without_negative_transfer(self):
        source=Liquid((5,),5,80);overfull=Liquid((6,),5,20)
        self.assertEqual(overfull.overfill_pressure,1)
        self.assertEqual(move_liquid(source,overfull,5),(source,overfull,-1))

    def test_equalization_preserves_each_species_and_common_fill_ratio(self):
        values=(Liquid((10,0),10,80),Liquid((0,5),30,20),Liquid((1,2),20,40))
        result=equalize_liquids(values)
        for i in range(2):self.assertAlmostEqual(sum(x.parts[i] for x in result),sum(x.parts[i] for x in values))
        ratios=[x.quantity/x.capacity for x in result]
        self.assertAlmostEqual(max(ratios),min(ratios))
        self.assertAlmostEqual(sum(x.quantity*x.temperature for x in result),sum(x.quantity*x.temperature for x in values))

    def test_energy_reservoir_debit_conserves_accepted_quantity(self):
        rng=random.Random(256)
        for _ in range(500):
            charges=[rng.uniform(0,1000) for _ in range(6)];total=sum(charges)
            pending=rng.uniform(0,total*2);after=debit_sources(charges,pending)
            self.assertAlmostEqual(total-sum(after),min(total,pending),places=9)
            self.assertTrue(all(x>=0 for x in after))
            if pending<total:self.assertAlmostEqual(after[0]/charges[0],after[-1]/charges[-1])


class BudgetTests(unittest.TestCase):
    def test_request_order_changes_scarce_supply_outcome(self):
        a=consume_sequence(10,[('binary',8),('fractional',8)])
        b=consume_sequence(10,[('fractional',8),('binary',8)])
        self.assertEqual([x['accepted'] for x in a['results']],[8,2])
        self.assertEqual([x['accepted'] for x in b['results']],[8,0])

    def test_requests_never_overspend_and_equality_succeeds(self):
        self.assertEqual(consume_sequence(8,[('binary',8)])['remaining'],0)
        for available in (0,1,8,20):
            result=consume_sequence(available,[('binary',8),('fractional',8),('fractional',100)])
            self.assertLessEqual(result['pending'],available)
            self.assertGreaterEqual(result['remaining'],0)

    def test_nested_loops_disprove_global_256_body_visit_assumption(self):
        self.assertEqual(loop_iterations(-1),0)
        self.assertEqual(loop_iterations(256),256)
        self.assertEqual(loop_iterations(257),256)
        self.assertEqual(loop_iterations(1000)*loop_iterations(1000),65536)

    def test_model_guards_are_explicit(self):
        for bad in (-1,math.inf,math.nan):
            with self.assertRaises(ValueError):consume_sequence(bad,[])
        with self.assertRaises(ValueError):loop_iterations(1.0)
        with self.assertRaises(ValueError):move_liquid(Liquid((1,),1,20),Liquid((1,0),2,20),1)


if __name__=='__main__':unittest.main()
