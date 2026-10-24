import subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class CLITests(unittest.TestCase):
 def test_valid_cli_produces_golden_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'printed.svg'
   result=subprocess.run([sys.executable,'-m','vp2d','--input','fixtures/02_migration_relation.json','--output',str(output)],cwd=ROOT,capture_output=True,text=True,timeout=20)
   self.assertEqual(result.returncode,0,result.stderr)
   self.assertEqual(output.read_bytes(),(ROOT/'outputs/02_migration_relation.svg').read_bytes())
 def test_bad_cli_is_nonzero_and_writes_no_svg(self):
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'bad.svg'
   result=subprocess.run([sys.executable,'-m','vp2d','--input','fixtures/does_not_exist.json','--output',str(output)],cwd=ROOT,capture_output=True,text=True,timeout=20)
   self.assertNotEqual(result.returncode,0)
   self.assertFalse(output.exists())
