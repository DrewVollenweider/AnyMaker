import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import anymaker as am
import workshop_index as wi


class WorkshopTests(unittest.TestCase):
    def test_copy_index_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(dir=am.OUTPUT) as tmp:
            root=Path(tmp); source=root/'source'; item=source/'123'; item.mkdir(parents=True)
            raw=json.dumps({'definitions':{},'vehicles':{'vehicles':[{'id':1}]}}).encode()
            (item/'vehicle.data').write_bytes(raw)
            (item/'vehicle.meta').write_text('{}'); (item/'workshop_preview.png').write_bytes(b'preview fixture')
            with patch.object(am,'OUTPUT',root):
                result=wi.build(source,'copied')
                self.assertEqual(result['creations'],1)
                self.assertTrue(result['originals_unchanged']); self.assertTrue(result['copies_match'])
                self.assertEqual((root/'copied/123/vehicle.data').read_bytes(),raw)
                self.assertEqual((item/'vehicle.data').read_bytes(),raw)
                self.assertIn('Workshop 123',(root/'copied/index.html').read_text())
                with self.assertRaises(ValueError): wi.build(source,'copied')

    def test_script_content_is_extracted_as_data(self):
        sample={'a':[{'script':'on_tick { in Display.display_value = out Sensor.altitude }'}]}
        found=wi.script_fields(sample)
        self.assertEqual(found[0]['path'],'/a/0/script')
        self.assertEqual(found[0]['text'],sample['a'][0]['script'])

    def test_downloaded_corpus_integrity_and_audit(self):
        folder=am.OUTPUT/'workshop-examples'
        if not folder.exists(): self.skipTest('Downloaded corpus not present')
        index=am.load(folder/'index.json'); records=am.load(folder/'integrity.json')
        self.assertEqual(len(index),33)
        for record in records:
            self.assertEqual(hashlib.sha256(Path(record['copy']).read_bytes()).hexdigest(),record['sha256'])
        cat=am.definitions()
        for item in index:
            self.assertTrue(am.audit(am.load(folder/item['workshop_id']/'vehicle.data'),cat)['ok'],item['workshop_id'])


if __name__=='__main__': unittest.main()
