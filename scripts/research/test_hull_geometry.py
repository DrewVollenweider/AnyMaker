"""Independent seed decisions, tolerance distinctions and face-reference tests."""
import math
import unittest
from hull_geometry import (ROUNDING_FACTOR,face_geometry,hull_reference,
                           hull_tolerances,initial_hull_seed)


class HullGeometryTests(unittest.TestCase):
    def test_too_few_points(self):
        for points in [[],[(0,0,0)],[(0,0,0),(1,0,0)]]:
            self.assertEqual(initial_hull_seed(points)['seed_path'],'too_few_points')

    def test_collinear_or_coincident_triangle_is_too_small(self):
        for points in [[(0,0,0),(1,0,0),(2,0,0)],[(0,0,0)]*4]:
            self.assertEqual(initial_hull_seed(points)['seed_path'],'triangle_too_small')

    def test_noncollinear_three_points_use_triangle_pair(self):
        result = initial_hull_seed([(0,0,0),(1,0,0),(0,1,0)])
        self.assertEqual(result['seed_path'],'triangle_pair')
        self.assertEqual(result['triangle'],(1,2,0))
        self.assertEqual(result['triangle_cross_squared'],1)

    def test_cube_and_flat_square_seed_paths(self):
        cube = [(x,y,z) for x in (0,1) for y in (0,1) for z in (0,1)]
        self.assertEqual(initial_hull_seed(cube)['seed_path'],'three_dimensional')
        self.assertEqual(initial_hull_seed([(0,0,0),(1,0,0),(1,1,0),(0,1,0)])['seed_path'],
                         'planar_pair')

    def test_tolerance_scale_uses_max_abs_coordinates_not_extents(self):
        result = hull_tolerances([(-10,-2,0),(1,3,4)],requested=0)
        self.assertEqual(result['rounding'],17*ROUNDING_FACTOR)
        self.assertEqual(result['assignment_squared'],(17*ROUNDING_FACTOR)**2)
        self.assertEqual(result['planar_squared'],36*(17*ROUNDING_FACTOR)**2)

    def test_requested_assignment_tolerance_and_planar_decision_are_distinct(self):
        points = [(0,0,0),(1,0,0),(0,1,0),(.2,.2,1e-5)]
        a,b = initial_hull_seed(points,0),initial_hull_seed(points,.1)
        self.assertEqual(a['seed_path'],'three_dimensional')
        self.assertEqual(a['seed_path'],b['seed_path'])
        self.assertAlmostEqual(b['assignment_squared'],.01)
        self.assertEqual(a['planar_squared'],b['planar_squared'])

    def test_translating_shape_inputs_changes_rounding_scale(self):
        points = [(0,0,0),(1,0,0),(0,1,0),(.2,.2,1e-5)]
        shifted = [(x+100,y,z) for x,y,z in points]
        a,b = initial_hull_seed(points),initial_hull_seed(shifted)
        self.assertEqual(a['seed_path'],'three_dimensional')
        self.assertEqual(b['seed_path'],'planar_pair')
        self.assertGreater(b['rounding'],a['rounding'])

    def test_seed_ties_keep_first_maximum(self):
        result = initial_hull_seed([(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)])
        self.assertEqual(result['triangle'],(0,1,2))
        self.assertEqual(result['seed_path'],'planar_pair')

    def test_face_mean_is_not_area_weighted_centroid(self):
        points = [(0,0,0),(4,0,0),(2,1,0),(0,1,0)]
        mean,normal = face_geometry(points)
        self.assertEqual(mean,(1.5,.5,0))
        self.assertEqual(normal,(0,0,6))
        self.assertNotEqual(mean,(14/9,4/9,0))
        reverse_mean,reverse_normal = face_geometry(points[::-1])
        self.assertEqual(mean,reverse_mean)
        self.assertEqual(reverse_normal,(0,0,-6))

    def test_hull_reference_weights_faces_equally(self):
        a = [(0,0,0),(3,0,0),(0,3,0)]
        b = [(10,0,0),(12,0,0),(12,2,0),(10,2,0)]
        self.assertEqual(hull_reference([a,b]),(6,1,0))
        self.assertNotEqual(hull_reference([a,b]),(47/7,1,0))

    def test_input_preservation(self):
        points = [[0,0,0],[1,0,0],[0,1,0]]
        initial_hull_seed(points)
        face_geometry(points)
        self.assertEqual(points,[[0,0,0],[1,0,0],[0,1,0]])

    def test_model_guards(self):
        for call in [lambda:initial_hull_seed([(math.nan,0,0)]),
                     lambda:hull_tolerances([(1e308,1e308,1e308)]),
                     lambda:hull_tolerances([],requested=-1),
                     lambda:face_geometry([(0,0,0),(1,0,0)]),
                     lambda:hull_reference([])]:
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
