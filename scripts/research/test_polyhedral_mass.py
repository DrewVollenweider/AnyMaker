"""Analytic solids and geometry invariants for source-bound hull integration."""
import math
import unittest

from mass_properties import Child,TensorMassProperties,box,combine
from polyhedral_mass import surface_mass_properties

BOX_FACES = ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
TETRA = ((0,0,0),(1,0,0),(0,1,0),(0,0,1))
TETRA_FACES = ((0,2,1),(0,1,3),(0,3,2),(1,2,3))


def cuboid(x,y,z):
    return ((0,0,0),(x,0,0),(x,y,0),(0,y,0),
            (0,0,z),(x,0,z),(x,y,z),(0,y,z))


class PolyhedralMassTests(unittest.TestCase):
    def assertTensorClose(self,actual,expected):
        for row,want in zip(actual,expected):
            for value,target in zip(row,want):
                self.assertAlmostEqual(value,target,delta=2e-7*max(1,abs(target)))

    def test_cuboid_matches_independent_box_formula(self):
        p = surface_mass_properties(cuboid(2,3,4),BOX_FACES,10)
        self.assertEqual(p.mass,240)
        self.assertEqual(p.center,(1,1.5,2))
        self.assertTensorClose(p.inertia,((500,0,0),(0,400,0),(0,0,260)))

    def test_tetrahedron_centroid_and_full_inertia(self):
        # Unit tetra at density480 has mass80, COM(1/4,1/4,1/4).
        # COM moments from direct simplex integrals: diagonal3m/40, off m/80.
        p = surface_mass_properties(TETRA,TETRA_FACES,480)
        self.assertAlmostEqual(p.mass,80)
        self.assertEqual(p.center,(.25,.25,.25))
        self.assertTensorClose(p.inertia,((6,1,1),(1,6,1),(1,1,6)))

    def test_translation_preserves_mass_and_com_inertia(self):
        a = surface_mass_properties(TETRA,TETRA_FACES,480)
        moved = [tuple(v[i]+(100,-200,300)[i] for i in range(3)) for v in TETRA]
        b = surface_mass_properties(moved,TETRA_FACES,480)
        self.assertEqual(a.mass,b.mass)
        self.assertEqual(b.center,(100.25,-199.75,300.25))
        self.assertTensorClose(a.inertia,b.inertia)

    def test_oblique_rotation_matches_tensor_transform(self):
        c = math.sqrt(.5)
        rotation = ((c,-c,0),(c,c,0),(0,0,1))
        vertices = cuboid(2,3,4)
        rotated = [tuple(sum(rotation[i][j]*v[j] for j in range(3)) for i in range(3)) for v in vertices]
        actual = surface_mass_properties(rotated,BOX_FACES,10)
        expected = combine([Child(box((2,3,4),10),rotation=rotation)])
        self.assertTensorClose(actual.inertia,expected.inertia)

    def test_triangulated_and_polygon_faces_agree(self):
        triangles = [(f[0],f[i],f[i+1]) for f in BOX_FACES for i in range(1,len(f)-1)]
        a = surface_mass_properties(cuboid(2,3,4),BOX_FACES,10)
        b = surface_mass_properties(cuboid(2,3,4),triangles,10)
        self.assertEqual(a.mass,b.mass)
        self.assertEqual(a.center,b.center)
        self.assertTensorClose(a.inertia,b.inertia)

    def test_face_order_and_cyclic_start_do_not_change_result(self):
        faces = [f[1:]+f[:1] for f in BOX_FACES[::-1]]
        a = surface_mass_properties(cuboid(2,3,4),BOX_FACES,10)
        b = surface_mass_properties(cuboid(2,3,4),faces,10)
        self.assertEqual(a.mass,b.mass)
        self.assertEqual(a.center,b.center)
        self.assertTensorClose(a.inertia,b.inertia)

    def test_density_scaling(self):
        a = surface_mass_properties(TETRA,TETRA_FACES,480)
        b = surface_mass_properties(TETRA,TETRA_FACES,960)
        self.assertEqual(b.mass,2*a.mass)
        self.assertEqual(b.center,a.center)
        self.assertTensorClose(b.inertia,tuple(tuple(2*x for x in row) for row in a.inertia))

    def test_length_scaling(self):
        a = surface_mass_properties(TETRA,TETRA_FACES,480)
        b = surface_mass_properties([tuple(2*x for x in v) for v in TETRA],TETRA_FACES,480)
        self.assertEqual(b.mass,8*a.mass)
        self.assertEqual(b.center,tuple(2*x for x in a.center))
        self.assertTensorClose(b.inertia,tuple(tuple(32*x for x in row) for row in a.inertia))

    def test_known_plate_collision_slab(self):
        vertices = [(x,y,z+.028) for x,y,z in cuboid(.8,.4,.008)]
        p = surface_mass_properties(vertices,BOX_FACES,400)
        self.assertAlmostEqual(p.mass,1.024,places=12)
        for actual,want in zip(p.center,(.4,.2,.032)):
            self.assertAlmostEqual(actual,want,places=12)

    def test_full_tensor_composes_without_losing_products(self):
        p = surface_mass_properties(TETRA,TETRA_FACES,480)
        tensor = TensorMassProperties(p.mass,p.inertia)
        result = combine([Child(tensor,(-1,0,0)),Child(tensor,(1,0,0))])
        expected = ((12,2,2),(2,172,2),(2,2,172))
        self.assertEqual(result.mass,160)
        self.assertTensorClose(result.inertia,expected)

    def test_open_or_inconsistent_surface_rejected_by_model(self):
        for faces in [TETRA_FACES[:-1],(TETRA_FACES[0][::-1],*TETRA_FACES[1:])]:
            with self.assertRaises(ValueError):
                surface_mass_properties(TETRA,faces,480)

    def test_inward_surface_and_small_volume_are_out_of_scope(self):
        for vertices,faces in [(TETRA,[f[::-1] for f in TETRA_FACES]),
                               ([(x,y,z*1e-9) for x,y,z in TETRA],TETRA_FACES)]:
            with self.assertRaises(ValueError):
                surface_mass_properties(vertices,faces,480)

    def test_nonfinite_and_invalid_indices_rejected(self):
        for vertices,faces in [((*TETRA[:3],(0,0,math.nan)),TETRA_FACES),
                               (TETRA,[(0,1,10)]),
                               (TETRA,[(0,1,1)]),
                               (TETRA,[(0,1,2.0)])]:
            with self.assertRaises(ValueError):
                surface_mass_properties(vertices,faces,480)

    def test_preserves_supplied_geometry(self):
        vertices = [list(p) for p in TETRA]
        faces = [list(f) for f in TETRA_FACES]
        surface_mass_properties(vertices,faces,480)
        self.assertEqual(vertices,[list(p) for p in TETRA])
        self.assertEqual(faces,[list(f) for f in TETRA_FACES])

    def test_nonfinite_density_rejected(self):
        with self.assertRaises(ValueError):
            surface_mass_properties(TETRA,TETRA_FACES,math.inf)


if __name__ == '__main__':
    unittest.main()
