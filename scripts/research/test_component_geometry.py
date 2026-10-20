"""Boundary counterexamples and invariants for traced component arithmetic."""
import math
import random
import unittest

from component_geometry import node_index,point_extended,port_size_offset,upper_extension,zone_extended,zone_volume_sum


class ComponentGeometryTests(unittest.TestCase):
    def test_mixed_ports_preserve_absolute_indexes(self):
        nodes=[{'type':'mechanical'},{'type':'gas'},{'type':'gas'},{'type':'gas'}]
        self.assertEqual([node_index(nodes,'gas',i) for i in range(3)],[1,2,3])
        self.assertEqual(node_index(nodes,'gas',3),-1)
        self.assertEqual(node_index(nodes,'gas',-1),-1)

    def test_point_and_cell_boundary_must_not_use_one_extension_rule(self):
        ext=(6,6,6);center=(.1,.1,.1)
        self.assertEqual(point_extended((0,0,0),ext,center),(0,0,0))
        self.assertEqual(zone_extended((0,0,0),(0,0,0),ext,center),((0,0,0),(6,6,6)))
        self.assertEqual(zone_volume_sum([((0,0,0),(0,0,0))],ext,center),343)
        self.assertEqual(point_extended((1,1,1),ext,(1,1,1)),(1,1,1))

    def test_native_get_volume_is_sum_not_geometric_union(self):
        zone=((-1,-1,-1),(1,1,1))
        self.assertEqual(zone_volume_sum([zone],(0,0,0),(0,0,0)),27)
        self.assertEqual(zone_volume_sum([zone,zone],(0,0,0),(0,0,0)),54)

    def test_odd_size_hydraulic_endpoint_is_half_cell_on_tangents(self):
        # Published prior 2x2 base point [0,1,0], direction 2, size selector 1.
        point=(0,1,0);offset=port_size_offset(1,2)
        self.assertEqual(tuple(a+b for a,b in zip(point,offset)),(.5,1,.5))
        for direction in range(6):
            self.assertEqual(port_size_offset(2,direction),(0,0,0))
            self.assertEqual(sum(port_size_offset(1,direction)),1)

    def test_named_clamp_does_not_imply_a_lower_bound(self):
        self.assertEqual(upper_extension((-2,7,11),(10,10,10)),(-2,7,10))

    def test_native_direction_pairs_do_not_share_an_axis_by_sign_guess(self):
        expected=[(0,.5,.5),(0,.5,.5),(.5,0,.5),(.5,0,.5),(.5,.5,0),(.5,.5,0)]
        self.assertEqual([port_size_offset(1,i) for i in range(6)],expected)

    def test_translation_and_nonnegative_extension_volume_invariants(self):
        rng=random.Random(25904830)
        for _ in range(500):
            lower=tuple(rng.randrange(-5,4) for _ in range(3))
            upper=tuple(x+rng.randrange(5) for x in lower)
            extension=tuple(rng.randrange(8) for _ in range(3))
            center=tuple(rng.randrange(-6,6)+.25 for _ in range(3))
            shift=tuple(rng.randrange(-4,5) for _ in range(3))
            add=lambda a,b:tuple(x+y for x,y in zip(a,b))
            lo,hi=zone_extended(lower,upper,extension,center)
            moved=zone_extended(add(lower,shift),add(upper,shift),extension,add(center,shift))
            self.assertEqual(moved,(add(lo,shift),add(hi,shift)))
            self.assertGreaterEqual(math.prod(b-a+1 for a,b in zip(lo,hi)),math.prod(b-a+1 for a,b in zip(lower,upper)))

    def test_model_guards_do_not_accept_nonfinite_or_boolean_coordinates(self):
        with self.assertRaises(ValueError):point_extended((True,0,0),(1,1,1),(0,0,0))
        with self.assertRaises(ValueError):point_extended((0,0,0),(1,1,1),(float('nan'),0,0))
        with self.assertRaises(ValueError):zone_extended((1,0,0),(0,0,0),(0,0,0),(0,0,0))


if __name__=='__main__':
    unittest.main()
