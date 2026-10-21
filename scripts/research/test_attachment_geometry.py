"""Boundary and independent geometric counterexamples for attachment helpers."""
import itertools
import unittest
from fractions import Fraction

from attachment_geometry import (compiled_triangle_rectangle,grids_equivalent,
    sampled_line_rectangle,sampled_triangle_rectangle,surface_bounds,voxel_overlap)


class AttachmentGeometryTests(unittest.TestCase):
    def test_voxel_touch_and_one_cell_separation(self):
        self.assertTrue(voxel_overlap((0,0,0),(2,2,2),(2,2,2),(3,3,3)))
        self.assertFalse(voxel_overlap((0,0,0),(2,2,2),(3,2,2),(4,3,3)))

    def test_surface_sizes_and_face_planes_all_directions(self):
        for direction in range(6):
            lo,hi,size=surface_bounds(direction,(4,5,6),(3,2),(0,0,0),(0,0,0))
            self.assertEqual(size,(3,2));self.assertEqual(lo[direction//2],hi[direction//2])
            self.assertEqual((hi[0]-lo[0]+1)*(hi[1]-lo[1]+1)*(hi[2]-lo[2]+1),6)

    def test_quarter_deadband_can_move_only_upper_surface_bound(self):
        # Y-facing single cell, X stretch center=0: spans from x=0 to x=4.
        self.assertEqual(surface_bounds(2,(0,0,0),(1,1),(4,0,0),(0,0,0)),
                         ((0,0,0),(4,0,0),(5,1)))
        # Lower physical edge=-.5; threshold center-.25 is equal at center=-.25.
        at=surface_bounds(2,(0,0,0),(1,1),(4,0,0),(-.25,0,0))
        below=surface_bounds(2,(0,0,0),(1,1),(4,0,0),(-.25001,0,0))
        self.assertEqual(at[0][0],0);self.assertEqual(below[0][0],4)

    def test_positive_and_negative_face_move_differently(self):
        self.assertEqual(surface_bounds(0,(0,0,0),(1,1),(4,0,0),(0,0,0))[0][0],0)
        self.assertEqual(surface_bounds(1,(0,0,0),(1,1),(4,0,0),(0,0,0))[0][0],4)

    def test_grid_equivalence_cardinal_shortcut_and_inclined_plane(self):
        self.assertTrue(grids_equivalent((0,0,0),(1,0,0),(99,99,99),(0,-1,0)))
        self.assertTrue(grids_equivalent((0,0,0),(1,1,0),(3,-3,5),(2,2,0)))
        self.assertFalse(grids_equivalent((0,0,0),(1,1,0),(3,-2,5),(2,2,0)))
        self.assertFalse(grids_equivalent((0,0,0),(1,1,0),(0,0,0),(-1,-1,0)))

    def test_line_endpoints_degenerate_and_octants(self):
        for end in itertools.product((-5,0,5),repeat=2):
            self.assertTrue(sampled_line_rectangle(end,end,(0,0),end))
        self.assertFalse(sampled_line_rectangle((1,1),(2,2),(0,0),(0,0)))

    def test_integer_triangle_contains_closed_boundary_both_windings(self):
        for tri in [((0,0),(4,0),(0,4)),((0,4),(4,0),(0,0))]:
            self.assertTrue(sampled_triangle_rectangle((2,2),(2,2),*tri))
            self.assertFalse(sampled_triangle_rectangle((3,3),(3,3),*tri))

    def test_continuous_overlap_can_have_no_integer_sample(self):
        tri=((-1,0),(2,1),(3,1))
        # Independent barycentric witness, all weights positive and sum=1.
        weights=(Fraction(9,16),Fraction(1,4),Fraction(3,16))
        point=tuple(sum(w*p[i] for w,p in zip(weights,tri)) for i in range(2))
        self.assertEqual(point,(Fraction(1,2),Fraction(7,16)))
        self.assertFalse(sampled_triangle_rectangle((0,0),(1,1),*tri))

    def test_float_helper_repeated_corner_can_reject_actual_overlap(self):
        tri=((-8,-8),(1,2),(2,1))
        # Independent barycentric witness at rectangle lower-left: 3/19 A + 8/19 B + 8/19 C.
        weights=(Fraction(3,19),Fraction(8,19),Fraction(8,19))
        self.assertEqual(tuple(sum(w*p[i] for w,p in zip(weights,tri)) for i in range(2)),(0,0))
        self.assertFalse(compiled_triangle_rectangle((0,0),(4,4),*tri))
        self.assertTrue(sampled_triangle_rectangle((0,0),(4,4),*tri))

    def test_float_helper_accepts_ordinary_overlap_and_rejects_separation(self):
        self.assertTrue(compiled_triangle_rectangle((0,0),(1,1),(0,0),(2,0),(0,2)))
        self.assertFalse(compiled_triangle_rectangle((0,0),(1,1),(2,2),(4,2),(2,4)))

    def test_translation_preserves_sampled_contact(self):
        tri=((-1,0),(2,1),(3,1));move=(13,-7)
        shift=lambda p:tuple(x+y for x,y in zip(p,move))
        self.assertEqual(sampled_triangle_rectangle((0,0),(1,1),*tri),
                         sampled_triangle_rectangle(shift((0,0)),shift((1,1)),*[shift(p) for p in tri]))

    def test_model_rejects_unbounded_work_and_invalid_inputs(self):
        with self.assertRaises(ValueError):sampled_triangle_rectangle((0,0),(100,100),(0,0),(1,0),(0,1),max_samples=10)
        with self.assertRaises(ValueError):surface_bounds(6,(0,0,0),(1,1),(0,0,0),(0,0,0))
        with self.assertRaises(ValueError):compiled_triangle_rectangle((0,0),(1,1),(float('nan'),0),(1,0),(0,1))


if __name__=='__main__':unittest.main()
