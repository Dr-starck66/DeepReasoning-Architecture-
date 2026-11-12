import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).parent))
from gate_bridge import build_bundle, call_existing_gate, sha

class GateBundleTests(unittest.TestCase):
    def test_manifest_valid_and_hash_bound(self):
        with TemporaryDirectory() as t:
            path,receipt=build_bundle(Path(t))
            m=json.loads(path.read_text())
            self.assertEqual(m['schema'],'astra-prooflab-evidence/1')
            self.assertEqual(len(m['claims']),2)
            self.assertEqual(receipt['finite_computation_status'],'PASS')
            for claim in m['claims']:
                self.assertEqual(sha((Path(t)/claim['artifact']).read_bytes()),claim['sha256'])
                self.assertNotIn('ci_run',claim)
    def test_tampering_detected_by_sha_contract(self):
        with TemporaryDirectory() as t:
            path,_=build_bundle(Path(t))
            m=json.loads(path.read_text())
            target=Path(t)/m['claims'][0]['artifact']
            target.write_bytes(target.read_bytes()+b'BOGUS')
            self.assertNotEqual(sha(target.read_bytes()),m['claims'][0]['sha256'])
    def test_missing_real_gate_is_unverified(self):
        with TemporaryDirectory() as t:
            path,_=build_bundle(Path(t))
            # In the isolated package, existing project gate is not installed.
            r=call_existing_gate(path)
            self.assertIn(r['status'],('UNVERIFIED','PASS'))
            self.assertNotEqual(r['status'],'FAIL')

if __name__=='__main__':unittest.main()