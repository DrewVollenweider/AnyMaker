"""Independent invariants and examples for bounded producer redistribution."""
import math,random,unittest
from electric_balance import Store,redistribute,registered_redistribution,debit_registered
from static_models import consume_sequence,debit_sources


class ElectricBalanceTests(unittest.TestCase):
    def test_default_share_is_slow_transfer_without_energy_loss(self):
        r=redistribute([Store(100,100),Store(0,100)])
        self.assertEqual(r['target_ratio'],.5)
        for a,b in zip(r['energies'],(99.95,.05)):self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(sum(r['delta']),0)

    def test_unit_share_reaches_capacity_weighted_target(self):
        r=redistribute([Store(60,60,1),Store(0,20,1),Store(0,40,1)])
        self.assertEqual(r['energies'],(30,10,20))

    def test_donor_share_controls_release_and_recipient_share_does_not(self):
        a=[Store(100,100,.2),Store(50,100,.8),Store(0,100,0)]
        b=[Store(100,100,.2),Store(50,100,.8),Store(0,100,1)]
        self.assertEqual(redistribute(a)['energies'],(90,50,10))
        self.assertEqual(redistribute(a)['energies'],redistribute(b)['energies'])

    def test_different_donors_pool_release_before_deficit_allocation(self):
        r=redistribute([Store(100,100,.2),Store(100,100,.8),Store(0,50),Store(0,150)])
        self.assertEqual(r['energies'],(90,60,12.5,37.5))
        self.assertEqual(r['released'],50)

    def test_zero_share_and_already_equal_fill(self):
        self.assertEqual(redistribute([Store(100,100,0),Store(0,100)])['energies'],(100,0))
        self.assertEqual(redistribute([Store(20,40),Store(50,100)])['delta'],(0,0))

    def test_empty_and_zero_capacity_producer(self):
        self.assertEqual(redistribute([])['energies'],())
        self.assertEqual(redistribute([Store(0,0)])['energies'],(0,))
        self.assertEqual(redistribute([Store(0,0),Store(10,10)])['energies'],(0,10))

    def test_existing_consumer_debit_then_redistribution_preserves_remaining_energy(self):
        pending=consume_sequence(100,[('binary',30),('fractional',100)])['pending']
        self.assertEqual(pending,100)
        q=debit_sources([25,75],20)
        r=redistribute([Store(q[0],100),Store(q[1],100,1)])
        self.assertAlmostEqual(sum(r['energies']),80)
        self.assertEqual(r['energies'],(40,40))

    def test_seeded_conservation_bounds_and_approach_to_target(self):
        rng=random.Random(58234826)
        for _ in range(500):
            stores=[]
            for _ in range(rng.randint(1,9)):
                c=rng.uniform(.01,10000);stores.append(Store(rng.uniform(0,c),c,rng.random()))
            r=redistribute(stores)
            self.assertAlmostEqual(sum(r['energies']),sum(s.energy for s in stores),places=8)
            for s,q in zip(stores,r['energies']):
                self.assertGreaterEqual(q,-1e-9);self.assertLessEqual(q,s.capacity+1e-9)
                target=s.capacity*r['target_ratio']
                self.assertLessEqual(abs(q-target),abs(s.energy-target)+1e-9)

    def test_permutation_independent_for_distinct_contents_within_roundoff(self):
        a=[Store(90,100,.3),Store(20,100,.7),Store(0,50),Store(10,20)]
        expected=redistribute(a)['energies']
        order=[2,0,3,1];actual=redistribute([a[i] for i in order])['energies']
        for i,q in zip(order,actual):self.assertAlmostEqual(q,expected[i])

    def test_domain_and_original_stocks_preserved(self):
        s=Store(1,2);redistribute([s]);self.assertEqual(s.energy,1)
        with self.assertRaises(ValueError):redistribute([s,s])
        for args in [(-1,1),(2,1),(0,-1),(math.inf,2),(1,2,-.1),(1,2,1.1)]:
            with self.assertRaises(ValueError):Store(*args)

    def test_registered_distinct_settlement_matches_existing_model(self):
        a=[Store(25,100),Store(75,100)]
        r=debit_registered(a,[0,1],100,20)
        self.assertEqual(r['energies'],debit_sources([25,75],20))
        self.assertEqual(r['pending_after'],0)

    def test_repeated_registration_debits_current_stock_twice(self):
        r=debit_registered([Store(100,100)],[0,0],200,100)
        self.assertEqual(r['energies'],(25,))
        self.assertEqual(r['delta'],(-50,-25))
        self.assertEqual(r['fraction'],.5)

    def test_repeated_donor_reference_breaks_distinct_store_conservation(self):
        r=registered_redistribution([Store(100,100,1),Store(0,100)],[0,0,1])
        self.assertAlmostEqual(r['energies'][0],200/3)
        self.assertAlmostEqual(r['energies'][1],200/3)
        self.assertGreater(sum(r['energies']),100)
        self.assertEqual(r['initial_total'],200)

    def test_settlement_saturates_and_missing_budget_does_not_debit(self):
        s=[Store(10,20)]
        self.assertEqual(debit_registered(s,[0,0],20,100)['energies'],(0,))
        self.assertEqual(debit_registered(s,[0],0,10)['energies'],(10,))
        self.assertEqual(debit_registered(s,[0],20,0)['energies'],(10,))

    def test_reference_guards(self):
        s=[Store(1,2)]
        for indices in [[-1],[1],[True]]:
            with self.assertRaises(ValueError):registered_redistribution(s,indices)
        with self.assertRaises(ValueError):debit_registered(s,[0],-1,2)


if __name__=='__main__':unittest.main()
