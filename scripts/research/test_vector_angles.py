"""Known angles, native sign/fallback distinctions and turn-check boundaries."""
import math
import unittest

from vector_angles import consistent_plate_turns,dot_angle3,projected_angle3

X,Y = (1,0,0),(0,1,0)


class VectorAnglesTests(unittest.TestCase):
    def test_raw_dot_angle_does_not_normalize_inputs(self):
        self.assertEqual(dot_angle3((2,0,0),(1,1,0)),0)
        self.assertEqual(dot_angle3((0,0,0),(0,0,0)),math.pi/2)
        self.assertEqual(dot_angle3((2,0,0),(-2,0,0)),math.pi)

    def test_projected_angle_sign_and_half_turn(self):
        self.assertEqual(projected_angle3(X,Y,X,Y),-math.pi/2)
        self.assertEqual(projected_angle3(Y,X,X,Y),math.pi/2)
        self.assertEqual(projected_angle3(X,(-1,0,0),X,Y),-math.pi)
        self.assertEqual(math.copysign(1,projected_angle3(X,X,X,Y)),-1)

    def test_projection_ignores_normal_component_and_normalizes_lengths(self):
        self.assertEqual(projected_angle3((100,0,91),(0,5,-20),X,Y),-math.pi/2)
        self.assertAlmostEqual(projected_angle3((3,3,12),Y,X,Y),-math.pi/4)

    def test_zero_projection_uses_y_positive_fallback(self):
        zero = (0,0,3)
        self.assertEqual(projected_angle3(zero,X,X,Y),math.pi/2)
        self.assertEqual(projected_angle3(zero,Y,X,Y),0)
        self.assertEqual(projected_angle3(zero,zero,X,Y),0)

    def test_axes_are_used_as_supplied(self):
        self.assertAlmostEqual(projected_angle3(X,(1,1,0),X,(0,2,0)),-math.atan(2))

    def test_convex_and_concave_with_reversal(self):
        square = [(0,0,0),(3,0,0),(3,3,0),(0,3,0)]
        concave = [(0,0,0),(3,0,0),(1,1,0),(3,3,0),(0,3,0)]
        for p in [square,square[::-1]]:
            self.assertTrue(consistent_plate_turns(p,(0,0,1)))
        for p in [concave,concave[::-1]]:
            self.assertFalse(consistent_plate_turns(p,(0,0,1)))

    def test_small_helper_inputs_and_collinear_runs(self):
        for points in [[],[(0,0,0)],[(0,0,0),(1,0,0)]]:
            self.assertTrue(consistent_plate_turns(points,(0,0,1)))
        self.assertTrue(consistent_plate_turns([(0,0,0),(1,0,0),(2,0,0),(2,2,0),(0,2,0)],(0,0,1)))

    def test_consistent_turns_do_not_prove_a_simple_polygon(self):
        star = [(0,3,0),(2,-3,0),(-3,1,0),(3,1,0),(-2,-3,0)]
        # Edges 0 and 2 cross: the turn helper still returns True.
        a,b,c,d = star[0],star[1],star[2],star[3]
        def orientation(p,q,r):
            return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
        self.assertLess(orientation(a,b,c)*orientation(a,b,d),0)
        self.assertLess(orientation(c,d,a)*orientation(c,d,b),0)
        self.assertTrue(consistent_plate_turns(star,(0,0,1)))

    def test_turn_helper_does_not_check_coplanarity(self):
        self.assertTrue(consistent_plate_turns([(0,0,0),(2,0,0),(2,2,1),(0,2,0)],(0,0,1)))

    def test_vertical_normal_reference_axis_switch(self):
        points = [(0,0,0),(3,0,0),(3,0,3),(0,0,3)]
        self.assertTrue(consistent_plate_turns(points,(0,1,0)))
        self.assertTrue(consistent_plate_turns(points,(0,-1,0)))

    def test_model_rejects_nonfinite_and_invalid_basis(self):
        with self.assertRaises(ValueError):
            dot_angle3((math.nan,0,0),X)
        with self.assertRaises(ValueError):
            projected_angle3((1e308,0,0),X,X,Y)
        with self.assertRaises(ValueError):
            consistent_plate_turns([X,Y,(0,0,0)],(0,0,0))


if __name__ == '__main__':
    unittest.main()
