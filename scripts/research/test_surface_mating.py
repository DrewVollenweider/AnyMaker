"""Boundary examples and independent interface/geometry invariants."""
from dataclasses import replace
import itertools,random,unittest
from surface_mating import Surface,compatible,matable,NORMALS,NONE,MALE,FEMALE
from attachment_geometry import voxel_overlap


def plane(z,interface='torque',gender=NONE,mask=0,lo=(0,0),hi=(1,1),direction=5):
    return Surface((lo[0],lo[1],z),(hi[0],hi[1],z),direction,interface,gender,mask)


class SurfaceMatingTests(unittest.TestCase):
    def test_ordinary_interfaces_against_explicit_pair_table(self):
        kinds=('', 'torque','liquid','port')
        pairs={(NONE,NONE),(MALE,FEMALE),(FEMALE,MALE)}
        checked=0
        for ta,tb,ga,gb,ma,mb in itertools.product(kinds,kinds,range(3),range(3),range(4),range(4)):
            a=plane(0,ta,ga,ma);b=plane(1,tb,gb,mb,direction=4)
            # Independent unordered endpoint-label table for special plugs.
            labels=frozenset(((ta,ga),(tb,gb)))
            plug=('port',MALE) in labels
            valid_special=labels in (frozenset((('port',MALE),('',NONE))),frozenset((('port',MALE),('port',FEMALE))))
            want=bool(ma&mb) and valid_special if plug else ta==tb and (ga,gb) in pairs
            self.assertEqual(compatible(a,b),want)
            self.assertEqual(compatible(a,b),compatible(b,a));checked+=1
        self.assertEqual(checked,2304)

    def test_opposed_adjacent_required(self):
        a=plane(0);b=plane(1,direction=4)
        self.assertTrue(matable(a,b));self.assertTrue(matable(b,a))
        self.assertFalse(matable(a,replace(b,direction=5)))
        self.assertFalse(matable(a,plane(2,direction=4)))

    def test_genderless_surfaces_need_overlap_not_containment(self):
        a=plane(0,lo=(0,0),hi=(2,2));b=plane(1,lo=(2,2),hi=(4,4),direction=4)
        self.assertTrue(matable(a,b));self.assertTrue(matable(b,a))

    def test_male_must_fit_female_not_merely_overlap(self):
        a=plane(0,gender=MALE,lo=(0,0),hi=(2,2));b=plane(1,gender=FEMALE,lo=(2,2),hi=(4,4),direction=4)
        self.assertFalse(matable(a,b));self.assertFalse(matable(b,a))
        b=plane(1,gender=FEMALE,lo=(-1,-1),hi=(3,3),direction=4)
        self.assertTrue(matable(a,b));self.assertTrue(matable(b,a))

    def test_port_masks_and_generic_socket_exception(self):
        a=plane(0,'port',MALE,1,hi=(0,0));b=plane(1,'',NONE,3,direction=4)
        self.assertTrue(matable(a,b));self.assertTrue(matable(b,a))
        self.assertFalse(matable(a,replace(b,port_mask=2)))
        self.assertFalse(matable(a,replace(b,interface='data')))

    def test_all_six_directions(self):
        for direction,n in enumerate(NORMALS):
            a=Surface((0,0,0),(0,0,0),direction,'torque',NONE)
            b=Surface(n,n,direction^1,'torque',NONE)
            self.assertTrue(matable(a,b));self.assertTrue(matable(b,a))

    def test_two_independent_battery_face_mating_candidates(self):
        left=Surface((0,0,0),(0,1,1),0,'port',FEMALE,3)
        right=Surface((1,0,0),(1,1,1),1,'port',FEMALE,3)
        p=Surface((-1,0,0),(-1,0,0),1,'port',MALE,1)
        q=Surface((2,0,0),(2,0,0),0,'port',MALE,1)
        self.assertTrue(matable(left,p));self.assertTrue(matable(right,q))
        for port in (p,q):self.assertFalse(voxel_overlap(port.lower,port.upper,(0,0,0),(1,1,1)))
        self.assertFalse(voxel_overlap(p.lower,p.upper,q.lower,q.upper))

    def test_seeded_translation_and_argument_symmetry(self):
        rng=random.Random(62982050)
        for _ in range(300):
            x,y=rng.randint(-5,5),rng.randint(-5,5)
            a=plane(0,gender=MALE,lo=(x,y),hi=(x+rng.randint(0,3),y+rng.randint(0,3)))
            b=plane(1,gender=FEMALE,lo=(-4,-4),hi=(4,4),direction=4)
            shift=tuple(rng.randint(-100,100) for _ in range(3))
            move=lambda s:replace(s,lower=tuple(v+d for v,d in zip(s.lower,shift)),upper=tuple(v+d for v,d in zip(s.upper,shift)))
            self.assertEqual(matable(a,b),matable(move(a),move(b)))
            self.assertEqual(matable(a,b),matable(b,a))

    def test_surface_order_and_domain(self):
        a=plane(0);self.assertEqual(a.lower,(0,0,0))
        for kwargs in [dict(direction=6),dict(gender=3),dict(port_mask=-1),dict(upper=(1,1,2))]:
            with self.assertRaises(ValueError):replace(a,**kwargs)

    def test_female_female_and_male_male_rejected(self):
        for gender in (MALE,FEMALE):
            self.assertFalse(matable(plane(0,'port',gender,3),plane(1,'port',gender,3,direction=4)))


if __name__=='__main__':unittest.main()
