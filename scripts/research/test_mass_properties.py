"""Independent geometry, axis, scaling and native boundary checks."""
import math
import unittest

from mass_properties import Child,MassProperties,box,capsule_y,combine,sphere


class MassPropertiesTests(unittest.TestCase):
    def assertRelative(self,actual,expected,tolerance=1e-7):
        self.assertAlmostEqual(actual/expected,1,delta=tolerance)

    def test_unit_cube(self):
        result = box((1,1,1),1200)
        self.assertEqual(result.mass,1200)
        self.assertEqual(result.inertia_diagonal,(200,200,200))

    def test_rectangular_box_axes(self):
        result = box((2,3,4),10)
        self.assertEqual(result.mass,240)
        self.assertEqual(result.inertia_diagonal,(500,400,260))

    def test_full_side_lengths_are_not_half_extents(self):
        self.assertAlmostEqual(box((.08,.08,.08),1000).mass,.512,places=12)

    def test_sphere_volume_and_inertia(self):
        result = sphere(2,800)
        mass = 4*math.pi*8*800/3
        self.assertRelative(result.mass,mass)
        for inertia in result.inertia_diagonal:
            self.assertRelative(inertia,2*mass*4/5)

    def test_capsule_against_independent_hemisphere_centroid_integral(self):
        radius,length,density = .7,2.3,1234
        result = capsule_y(radius,length,density)
        mh = 2*math.pi*radius**3*density/3
        mc = math.pi*radius**2*length*density
        # A hemisphere's transverse inertia about its own COM is 83/320*m*r^2.
        transverse = (mc*(3*radius**2+length**2)/12
                      +2*mh*(83*radius**2/320+(length/2+3*radius/8)**2))
        axial = mc*radius**2/2+2*(2*mh*radius**2/5)
        self.assertRelative(result.mass,mc+2*mh)
        self.assertRelative(result.inertia_diagonal[0],transverse)
        self.assertRelative(result.inertia_diagonal[1],axial)
        self.assertEqual(result.inertia_diagonal[0],result.inertia_diagonal[2])

    def test_capsule_length_excludes_ends(self):
        r,l,density = 1,2,1000
        self.assertRelative(capsule_y(r,l,density).mass,math.pi*(l+4*r/3)*r*r*density)

    def test_density_scaling_on_positive_length_shapes(self):
        for make in [lambda d:box((2,3,4),d),lambda d:sphere(.5,d),
                     lambda d:capsule_y(.5,2,d)]:
            a,b = make(400),make(800)
            self.assertEqual(b.mass,2*a.mass)
            self.assertEqual(b.inertia_diagonal,tuple(2*x for x in a.inertia_diagonal))

    def test_length_scaling_cubic_mass_fifth_power_inertia(self):
        for make in [lambda s:box((s,2*s,3*s),900),lambda s:sphere(s,900),
                     lambda s:capsule_y(s,3*s,900)]:
            a,b = make(1),make(2)
            self.assertEqual(b.mass,8*a.mass)
            self.assertEqual(b.inertia_diagonal,tuple(32*x for x in a.inertia_diagonal))

    def test_zero_length_capsule_uses_factory_sphere_density(self):
        self.assertEqual(capsule_y(.5,0,400),sphere(.5,1000))
        self.assertNotEqual(capsule_y(.5,0,400),sphere(.5,400))
        self.assertEqual(capsule_y(.5,-0.0,2000),sphere(.5,1000))

    def test_tiny_positive_length_does_not_apply_factory_zero_branch(self):
        result = capsule_y(.5,1e-8,400)
        self.assertRelative(result.mass,sphere(.5,400).mass)
        self.assertLess(result.mass,sphere(.5,1000).mass/2)

    def test_model_guards_and_overflow(self):
        for bad in [0,-1,math.nan,math.inf]:
            with self.assertRaises(ValueError):
                sphere(bad,400)
            with self.assertRaises(ValueError):
                box((1,1,1),bad)
        with self.assertRaises(ValueError):
            capsule_y(1,-1,400)
        with self.assertRaises(ValueError):
            box((1,2),400)
        with self.assertRaises(ValueError):
            capsule_y(1,math.nan,400)
        with self.assertRaises(ValueError):
            sphere(1e200,400)

    def test_dimensions_are_preserved(self):
        dimensions = [2,3,4]
        box(dimensions,1200)
        self.assertEqual(dimensions,[2,3,4])

    def test_compound_parallel_axis_and_weighted_center(self):
        p = MassProperties(1,(0,0,0))
        result = combine([Child(p,(-2,0,0)),Child(p,(2,0,0))])
        self.assertEqual(result.mass,2)
        self.assertEqual(result.center,(0,0,0))
        self.assertEqual(result.inertia,((0,0,0),(0,8,0),(0,0,8)))
        weighted = combine([Child(p,(0,0,0)),Child(MassProperties(3,(0,0,0)),(4,0,0))])
        self.assertEqual(weighted.center,(3,0,0))
        self.assertEqual(weighted.inertia[1][1],12)

    def test_compound_off_diagonal_sign(self):
        p = MassProperties(1,(0,0,0))
        result = combine([Child(p,(-1,-1,0)),Child(p,(1,1,0))])
        self.assertEqual(result.inertia,((2,-2,0),(-2,2,0),(0,0,4)))

    def test_rotated_child_and_translation_invariance(self):
        p = box((2,3,4),10)
        rotation = ((0,-1,0),(1,0,0),(0,0,1))
        a = combine([Child(p,rotation=rotation)])
        b = combine([Child(p,(100,-200,30),rotation)])
        self.assertEqual(a.inertia,((400,0,0),(0,500,0),(0,0,260)))
        self.assertEqual(a.inertia,b.inertia)
        self.assertEqual(b.center,(100,-200,30))

    def test_overlapping_children_contribute_independently(self):
        p = box((1,1,1),1200)
        result = combine([Child(p),Child(p)])
        self.assertEqual(result.mass,2400)
        self.assertEqual(result.inertia,((400,0,0),(0,400,0),(0,0,400)))

    def test_oblique_rotation_produces_symmetric_tensor(self):
        c = math.sqrt(.5)
        p = MassProperties(1,(2,6,8))
        result = combine([Child(p,rotation=((c,-c,0),(c,c,0),(0,0,1)))])
        expected = ((4,-2,0),(-2,4,0),(0,0,8))
        for row,want in zip(result.inertia,expected):
            for value,target in zip(row,want):
                self.assertAlmostEqual(value,target)

    def test_compound_model_guards(self):
        p = box((1,1,1),1200)
        for children in [[],[Child(p,(math.inf,0,0))],
                         [Child(p,rotation=((2,0,0),(0,1,0),(0,0,1)))],
                         [Child(p,rotation=((-1,0,0),(0,1,0),(0,0,1)))],
                         [Child(MassProperties(1,(-1,0,0)))]]:
            with self.assertRaises(ValueError):
                combine(children)


if __name__ == '__main__':
    unittest.main()
