"""Synthetic coverage-accounting cases; passing is not game understanding."""
import unittest
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile

from audit_scope import inventory, load_reader, owner_name, qualified_name


class ScopeTests(unittest.TestCase):
    def function(self, signature='() research.plain (engine)', offset=10):
        return dict(signature=signature, code_offset=offset, code_size=3, code_sha256='hash')

    def test_types_do_not_create_method_topic_hits(self):
        rows, _, _ = inventory([self.function('(ptr<engine>) research.plain (liquid)')], [], {})
        self.assertEqual(rows[0]['topic_leads'], ['unclassified'])

    def test_templates_do_not_change_owner(self):
        name = qualified_name('(tuple<(s32),f64>) research.container<server_scene.actor>.tick (ptr<engine>)')
        self.assertEqual(owner_name(name), 'research.container<server_scene.actor>')

    def test_missing_class_and_unparsed_function_are_retained(self):
        definition = dict(source='rom/data/vehicle_component_definitions.json',
                          pointer='/definitions/0', id='a', **{'class': ''}, sha256='x')
        rows, classes, summary = inventory([self.function('unknown')], [definition], {})
        self.assertEqual(rows[0]['owner'], '<unparsed>')
        self.assertIsNone(classes[0]['class'])
        self.assertEqual(summary['component_definitions_with_omitted_class'], 1)

    def test_exact_owner_not_nested_or_template_parameter(self):
        definition = dict(source='rom/data/vehicle_component_definitions.json',
                          pointer='/definitions/0', id='a', **{'class': 'engine'}, sha256='x')
        funcs = [self.function('() server_scene.vehicle_component.engine.tick ()'),
                 self.function('() server_scene.vehicle_component.engine.nested.tick ()', 20),
                 self.function('() research.container<server_scene.vehicle_component.engine>.tick ()', 30)]
        _, classes, _ = inventory(funcs, [definition], {10: (funcs[0]['signature'], 'hash')})
        self.assertEqual(classes[0]['indexed_exact_owner_methods'], 1)
        self.assertEqual(classes[0]['exported_exact_owner_methods'], 1)
        self.assertEqual(classes[0]['binding_status'], 'name_candidate_only')

    def test_stale_reader_and_unknown_reader_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            inventory([self.function()], [], {10: ('wrong', 'hash')})
        with self.assertRaisesRegex(ValueError, 'absent from index'):
            inventory([], [], {10: ('wrong', 'hash')})

    def test_duplicate_offsets_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            inventory([self.function(), self.function()], [], {})

    def test_incomplete_and_wrong_build_reader_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'reader.sqlite'
            with closing(sqlite3.connect(path)) as db:
                db.execute('CREATE TABLE metadata(key TEXT,value TEXT)')
                db.commit()
                with self.assertRaisesRegex(ValueError, 'Incomplete'):
                    load_reader(path, 'expected')
                db.executemany('INSERT INTO metadata VALUES(?,?)', [
                    ('complete', 'true'),
                    ('provenance', json.dumps({'source_sha256': 'wrong'}))])
                db.commit()
            with self.assertRaisesRegex(ValueError, 'source mismatch'):
                load_reader(path, 'expected')


if __name__ == '__main__':
    unittest.main()
