"""Synthetic plate loader gates and independent geometry diagnostics."""
import copy
import unittest

from plate_reconstruction import audit_body,audit_document,calculate_direction,canonical_loop


def rectangle():
    return dict(nodes=[{'id':i+1,'pos':p} for i,p in enumerate([[0,0,0],[2,0,0],[2,3,0],[0,3,0]])],
                edges=[{'n0':2,'n1':1,'size':1},{'n0':2,'n1':3},{'n0':3,'n1':4},{'n0':4,'n1':1}],
                plates=[{'id':7,'nodes':[1,2,3,4],'size':0}])


class PlateReconstructionTests(unittest.TestCase):
    def test_direction_is_unreduced_cross_and_reversal_changes_facing(self):
        points=[(0,0,0),(2,0,0),(2,3,0),(0,3,0)]
        self.assertEqual(calculate_direction(points),(0,0,6))
        self.assertEqual(calculate_direction(points[::-1]),(0,0,-6))

    def test_collinear_prefix_search_and_duplicate_first_point_fallback(self):
        points=[(0,0,0),(1,0,0),(2,0,0),(2,3,0)]
        self.assertEqual(calculate_direction(points),(0,0,3))
        self.assertEqual(calculate_direction([points[0],points[0],*points[1:]]),(1,0,0))

    def test_boundary_direction_is_unordered_and_size_uses_first_loop_edge(self):
        body=rectangle();first=audit_body(body)['plate_results'][0]
        self.assertEqual(first['inferred_size'],1)
        self.assertIn('saved_size_differs_from_first_boundary_edge',first['warnings'])
        body['plates'][0]['nodes'].reverse()
        second=audit_body(body)['plate_results'][0]
        self.assertEqual(second['inferred_size'],0)
        self.assertEqual(second['calculated_direction'],(0,0,-6))

    def test_missing_closing_edge_and_missing_node_predict_no_plate(self):
        body=rectangle();body['edges'].pop()
        self.assertEqual(audit_body(body)['plate_results'][0]['reason'],'missing_boundary_edges')
        body=rectangle();body['nodes'].pop()
        self.assertEqual(audit_body(body)['plate_results'][0]['reason'],'missing_nodes')

    def test_duplicate_ids_unresolved_and_later_edges_ignored(self):
        body=rectangle();body['nodes'].append(copy.deepcopy(body['nodes'][0]))
        self.assertEqual(audit_body(body)['unresolved'],1)
        body=rectangle();duplicate=copy.deepcopy(body['edges'][0]);duplicate['size']=0
        body['edges'].append(duplicate);report=audit_body(body)
        self.assertEqual(report['ignored_duplicate_edge_indices'],[4])
        self.assertEqual(report['plate_results'][0]['inferred_size'],1)

    def test_nonplanarity_is_a_warning_not_invented_loader_rejection(self):
        body=rectangle();body['nodes'][3]['pos'][2]=1
        result=audit_body(body)['plate_results'][0]
        self.assertEqual(result['status'],'references_available')
        self.assertFalse(result['coplanar']);self.assertIn('noncoplanar_loop',result['warnings'])

    def test_shared_loops_ignore_start_but_warn_only_same_facing_and_size(self):
        body=rectangle();body['edges'][0]['size']=0
        body['plates'].append({'id':8,'nodes':[3,4,1,2]})
        result=audit_body(body)
        self.assertEqual(result['same_facing_loop_groups'],[[0,1]])
        self.assertEqual(canonical_loop([(0,0,0),(1,0,0),(0,1,0)]),
                         canonical_loop([(1,0,0),(0,0,0),(0,1,0)]))

    def test_opposed_skins_share_nodes_without_duplicate_face_warning(self):
        body=rectangle();body['edges'][0]['size']=0
        body['plates'].append({'id':8,'nodes':[3,2,1,4]})
        result=audit_body(body)
        self.assertEqual(result['shared_node_loop_groups'],[[0,1]])
        self.assertEqual(result['same_facing_loop_groups'],[])
        self.assertEqual(result['warning_count'],0)

    def test_audit_does_not_mutate_and_reports_multiple_bodies(self):
        document={'vehicles':{'vehicles':[rectangle(),rectangle()]}}
        original=copy.deepcopy(document);report=audit_document(document)
        self.assertEqual(document,original);self.assertEqual(report['summary']['plates'],2)

    def test_small_loops_and_noninteger_ids(self):
        body=rectangle();body['plates'][0]['nodes']=[1,2]
        self.assertEqual(audit_body(body)['reference_failures'],1)
        body=rectangle();body['plates'][0]['nodes'][0]=True
        with self.assertRaises(ValueError):audit_body(body)


if __name__=='__main__':unittest.main()
