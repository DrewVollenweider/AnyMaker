"""Synthetic constructor-prefix controls, independent of shipped game code."""
import unittest

from constructor_trace import trace_prefix
from test_code_trace import vn,op,ins


RCX=vn('register',8);RAX=vn('register',0);RDX=vn('register',16);SP=vn('register',32)
U=vn('unique',20);V=vn('unique',30)
CONST=lambda value:vn('const',value)
MEM=lambda value:vn('ram',value)
REFS=[dict(address=900,kind=4,symbol='() ctor (server_scene.vehicle_component.base)'),
      dict(address=908,kind=5,symbol='server_scene.vehicle_component.example')]


def prefix(saved_offset=40):
    return [ins(1,op('INT_SUB',SP,SP,CONST(56))),
            ins(2,op('INT_ADD',U,SP,CONST(saved_offset)),op('STORE',None,CONST(433),U,RCX)),
            ins(3,op('COPY',RDX,MEM(900))),
            ins(4,op('LOAD',V,CONST(433),RDX),op('INT_SUB',SP,SP,CONST(8)),
                op('CALLIND',None,V)),
            ins(5,op('COPY',RAX,MEM(908))),
            ins(6,op('INT_ADD',U,SP,CONST(saved_offset)),op('LOAD',V,CONST(433),U),op('COPY',RCX,V)),
            ins(7,op('STORE',None,CONST(433),RCX,RAX))]


def consecutive(instructions):
    for address,instruction in enumerate(instructions,1):
        instruction['address']=str(address)
        instruction['fallthrough']=str(address+1)
    return instructions


class ConstructorTests(unittest.TestCase):
    def test_parent_call_and_own_type_store_with_private_spill(self):
        result=trace_prefix(prefix(),REFS)
        self.assertEqual(result['initializers'][0]['object_offset'],0)
        self.assertEqual(result['initializers'][0]['initialized_type'],'server_scene.vehicle_component.base')
        self.assertEqual(result['type_stores'][0]['symbol'],'server_scene.vehicle_component.example')

    def test_shadow_space_is_not_preserved_across_call(self):
        result=trace_prefix(prefix(16),REFS)
        self.assertEqual(len(result['initializers']),1)
        self.assertEqual(result['type_stores'],[])

    def test_partial_stack_overwrite_invalidates_saved_pointer(self):
        seq=prefix()
        seq.insert(2,ins(20,op('INT_ADD',U,SP,CONST(40)),op('STORE',None,CONST(433),U,vn('const',1,4))))
        self.assertEqual(trace_prefix(consecutive(seq),REFS)['type_stores'],[])

    def test_unknown_store_invalidates_private_spills(self):
        seq=prefix()
        seq.insert(2,ins(20,op('STORE',None,CONST(433),vn('register',88),CONST(1))))
        self.assertEqual(trace_prefix(consecutive(seq),REFS)['type_stores'],[])

    def test_field_constructor_is_not_base_initializer(self):
        seq=prefix()
        seq.insert(3,ins(20,op('INT_ADD',RCX,RCX,CONST(8))))
        self.assertEqual(trace_prefix(consecutive(seq),REFS)['initializers'],[])

    def test_virtual_displacement_not_promoted_to_direct_ctor(self):
        refs=[dict(REFS[0],kind=6),REFS[1]]
        self.assertEqual(trace_prefix(prefix(),refs)['initializers'],[])

    def test_branch_stops_trace(self):
        seq=prefix()
        seq.insert(3,ins(20,op('CBRANCH',None,MEM(100),vn('register',500,1))))
        result=trace_prefix(consecutive(seq),REFS)
        self.assertEqual(result['initializers'],[])
        self.assertEqual(result['type_stores'],[])
        self.assertEqual(result['stopped_at'],'CBRANCH')

    def test_temporary_does_not_survive_instruction(self):
        seq=[ins(1,op('COPY',V,MEM(900))),ins(2,op('CALLIND',None,V))]
        self.assertEqual(trace_prefix(seq,REFS)['initializers'],[])

    def test_missing_instruction_stops_instead_of_skipping_effects(self):
        seq=prefix();del seq[2]
        result=trace_prefix(seq,REFS)
        self.assertEqual(result['initializers'],[])
        self.assertEqual(result['type_stores'],[])
        self.assertEqual(result['stopped_at'],'instruction_gap')


if __name__=='__main__':
    unittest.main()
