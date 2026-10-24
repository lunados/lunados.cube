import unittest,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class ReferenceIntegrity(unittest.TestCase):
 def test_canonical_source_snapshots(self):
  lock=json.loads((ROOT/'SOURCE_LOCK.json').read_text())
  self.assertEqual(len(lock['sources']),6)
  for filename, meta in lock['sources'].items():
   data=(ROOT/'reference'/filename).read_bytes()
   with self.subTest(source=filename):
    self.assertEqual(hashlib.sha256(data).hexdigest(),meta['sha256'])
    self.assertEqual(len(data),meta['bytes'])
 def test_p1_display_contract_is_not_p1_validator(self):
  meta=json.loads((ROOT/'reference/p1-form-color.json').read_text())
  self.assertEqual(meta['presentation_extension'],'P1-VG-basic/1.0.0')
  self.assertIn('presentation',meta['semantics_boundary'].lower())
 def test_core_has_exactly_five_pairs(self):
  meta=json.loads((ROOT/'reference/p0-core-v9.4.json').read_text())
  pairs=meta['ontology']['X']['pairs']
  self.assertEqual(len(pairs),5)
  self.assertEqual([p['dimension'] for p in pairs],['X:dimension:epistemology','X:dimension:governance','X:dimension:semantics','X:dimension:execution','X:dimension:provenance'])
 def test_not_original_p1_files(self):
  self.assertFalse((ROOT/'AIAEAO_Pure_Cube_P0_v9.4').exists())
  self.assertFalse((ROOT/'P1').exists())
