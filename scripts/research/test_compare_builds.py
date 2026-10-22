"""Comparison must preserve anonymous and repeated-ID definition records."""
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from compare_builds import definitions,mapping_diff


class CompareDefinitionsTests(unittest.TestCase):
    def db(self,root,rows):
        path=root/'catalog.sqlite'
        db=sqlite3.connect(path)
        try:
            db.execute('CREATE TABLE definitions(source TEXT,pointer TEXT,id TEXT,json TEXT)')
            db.executemany('INSERT INTO definitions VALUES(?,?,?,?)',
                           [(s,p,i,json.dumps(value)) for s,p,i,value in rows])
            db.commit()
        finally:db.close()
        return path

    def test_anonymous_records_are_not_collapsed(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as d:
            path=self.db(Path(d),[('a.json','/a/0','',{'v':1}),('a.json','/a/1','',{'v':2})])
            self.assertEqual(definitions(path),{'a.json#/a/0':{'v':1},'a.json#/a/1':{'v':2}})

    def test_repeated_ids_in_distinct_locations_are_retained(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as d:
            path=self.db(Path(d),[('a.json','/a','same',{'v':1}),('a.json','/b','same',{'v':2}),
                                  ('b.json','/a','same',{'v':3})])
            self.assertEqual(len(definitions(path)),3)

    def test_duplicate_exact_pointer_rejects_ambiguity(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as d:
            path=self.db(Path(d),[('a.json','/a','x',{}),('a.json','/a','y',{})])
            with self.assertRaises(ValueError):definitions(path)

    def test_missing_and_null_fields_remain_distinct(self):
        result=mapping_diff({'a':{},'b':{'v':None}},{'a':{'v':None},'b':{'v':None}})
        self.assertEqual(result['changed'],['a'])
        self.assertEqual(result['unchanged'],1)


if __name__=='__main__':unittest.main()
