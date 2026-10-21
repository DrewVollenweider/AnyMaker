"""Independent expected boundaries, interpolation, winding and slab dimensions."""
import copy
import math
import unittest

from plate_surfaces import clip_polygon, collision_point_cloud, solid_faces


class PlateSurfacesTests(unittest.TestCase):
    def test_halfplane_cuts_known_square(self):
        points = [(-2,-1),(2,-1),(2,1),(-2,1)]
        result, coords = clip_polygon(points, [((0,0),(1,0))])
        self.assertEqual(result, [(-2,-1),(0,-1),(0,1),(-2,1)])
        self.assertIsNone(coords)

    def test_coordinates_interpolate_at_the_same_fraction(self):
        points = [(-2,-1),(2,-1),(2,1),(-2,1)]
        coords = [(10*x+3,7*y-1) for x,y in points]
        result, payload = clip_polygon(points, [((1,0),(1,0))], coords)
        self.assertEqual(payload, [(10*x+3,7*y-1) for x,y in result])
        self.assertEqual(result[1], (1,-1))
        self.assertEqual(result[2], (1,1))

    def test_repeated_planes_and_empty_results(self):
        points = [(-2,-2),(2,-2),(2,2),(-2,2)]
        planes = [((1,0),(1,0)), ((0,1),(0,1))]
        result, _ = clip_polygon(points, planes)
        self.assertEqual(set(result), {(-2,-2),(1,-2),(1,1),(-2,1)})
        self.assertEqual(clip_polygon(result, [((-3,0),(1,0)), *planes]), ([],None))
        self.assertEqual(clip_polygon([], planes, []), ([],[]))

    def test_zero_planes_copy_and_do_not_alias(self):
        points = [[0,0],[1,0],[0,1]]
        original = copy.deepcopy(points)
        result, _ = clip_polygon(points, [])
        result.append((9,9))
        self.assertEqual(points, original)

    def test_exact_boundary_is_kept_including_duplicate_crossing(self):
        result, _ = clip_polygon([(0,0),(1,0),(0,1)], [((0,0),(1,0))])
        self.assertEqual(result, [(0,0),(0,0),(0,1),(0,1)])

    def test_translated_diagonal_plane_and_nonunit_normal(self):
        square = [(0,0),(2,0),(2,2),(0,2)]
        result, _ = clip_polygon(square, [((0.5,0.5),(2,2))])
        self.assertEqual(set(result), {(0,0),(1,0),(0,1)})

    def test_invalid_input_is_a_model_error(self):
        for points, planes, coords in [([(0,0)], [], []), ([(math.nan,0)], [], None),
                                       ([(0,0)], [((0,0),(0,0))], None)]:
            with self.assertRaises(ValueError):
                clip_polygon(points, planes, coords)

    def test_cardinal_visible_skin_and_collision_cloud_have_distinct_extents(self):
        points = [(0,0,0),(.16,0,0),(.16,.24,0),(0,.24,0)]
        faces = solid_faces(points, (0,0,.04), (0,0,1))
        self.assertEqual(len(faces['front']), 2)
        self.assertEqual({p[2] for t in faces['front'] for p in t}, {.04})
        self.assertEqual({round(p[2],8) for t in faces['back'] for p in t}, {.03})
        cloud = collision_point_cloud(points, (0,0,1))
        self.assertEqual({round(p[2],8) for p in cloud}, {.028,.036})
        self.assertEqual(len(cloud), 8)

    def test_opposed_facing_puts_collision_cloud_on_opposite_side(self):
        points = [(0,0,0),(1,0,0),(0,1,0)]
        cloud = collision_point_cloud(points, (0,0,-1))
        self.assertEqual({round(p[2],8) for p in cloud}, {-.036,-.028})

    def test_face_fans_use_opposite_winding_and_same_xy_coverage(self):
        faces = solid_faces([(0,0,0),(2,0,0),(0,3,0)], (0,0,.04), (0,0,1))
        def area_xy(triangle):
            a,b,c = triangle
            return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
        self.assertEqual(area_xy(faces['front'][0]), -6)
        self.assertEqual(area_xy(faces['back'][0]), 6)

    def test_oblique_slab_separation_is_eight_millimetres(self):
        normal = (1/math.sqrt(3),)*3
        cloud = collision_point_cloud([(0,0,0),(1,-1,0),(0,1,-1)], normal)
        distance = math.dist(cloud[0],cloud[1])
        self.assertAlmostEqual(distance, .008)

    def test_geometry_models_require_unit_normal_and_valid_node_count(self):
        for points, normal in [([(0,0,0)], (0,0,1)), ([(0,0,0)]*3, (0,0,3))]:
            with self.assertRaises(ValueError):
                collision_point_cloud(points,normal)
            with self.assertRaises(ValueError):
                solid_faces(points,(0,0,.04),normal)


if __name__ == '__main__':
    unittest.main()
