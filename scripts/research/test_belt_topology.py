"""Graph-level cross-checks, including the source's non-cycle exception."""
import itertools,unittest
from belt_topology import walk


class BeltTopologyTests(unittest.TestCase):
    def test_single_link_is_accepted_without_cycle(self):
        r=walk([('a','b')]);self.assertTrue(r['accepted']);self.assertEqual(r['reason'],'two_entry_exception')
        self.assertEqual(r['nodes'],('a','b'))

    def test_longer_open_chain_and_branched_loop_rejected(self):
        self.assertEqual(walk([(0,1),(1,2)])['reason'],'open_end')
        self.assertEqual(walk([(0,1),(1,2),(2,0),(1,3)])['reason'],'branch')

    def test_cycle_records_repeated_start_endpoint(self):
        edges=[(0,1),(1,2),(2,0)]
        self.assertEqual(walk(edges)['nodes'],(0,1,2,0))
        self.assertEqual(walk(edges,start_side=1)['nodes'],(1,0,2,1))

    def test_parallel_links_form_two_link_return(self):
        r=walk([(0,1),(0,1)])
        self.assertEqual((r['accepted'],r['reason'],r['nodes']),(True,'closed_return',(0,1,0)))

    def test_first_dead_end_can_ignore_links_behind_start(self):
        edges=[(0,1),(0,2)]
        self.assertTrue(walk(edges,start_side=0)['accepted'])
        self.assertFalse(walk(edges,start_side=1)['accepted'])

    def test_disconnected_components_do_not_change_walk(self):
        a=walk([((10,0),(20,0)),((20,0),(30,0)),((30,0),(10,0))])
        b=walk([((10,0),(20,0)),((20,0),(30,0)),((30,0),(10,0)),((99,0),(100,0))])
        self.assertEqual(a,b)

    def test_all_four_vertex_simple_graphs_against_degree_oracle(self):
        possible=list(itertools.combinations(range(4),2));checked=0
        for bits in range(1,1<<len(possible)):
            edges=[e for i,e in enumerate(possible) if bits>>i&1]
            for start in range(len(edges)):
                component=set(edges[start]);changed=True
                while changed:
                    before=len(component)
                    for a,b in edges:
                        if a in component or b in component:component.update((a,b))
                    changed=len(component)!=before
                local=[e for e in edges if e[0] in component]
                degrees=[sum(v in e for e in local) for v in component]
                for side in [0,1]:
                    far=edges[start][1-side]
                    expected=sum(far in e for e in local)==1 or all(k==2 for k in degrees)
                    self.assertEqual(walk(edges,start,side)['accepted'],expected,(edges,start,side));checked+=1
        self.assertEqual(checked,384)

    def test_model_guards_and_input_preservation(self):
        edges=[[0,1],[1,2]];walk(edges);self.assertEqual(edges,[[0,1],[1,2]])
        for args in [([],0,0),([(0,0)],0,0),([(0,1,2)],0,0),([(0,1)],True,0),([(0,1)],0,2)]:
            with self.assertRaises(ValueError):walk(*args)


if __name__=='__main__':unittest.main()
