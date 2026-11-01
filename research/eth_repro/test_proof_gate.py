import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from proof_gate import audit, strip_lean_comments, render_html

class ContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.base=Path(self.tmp.name)
        self.src=self.base/'Example.lean'
        self.src.write_text('-- sorry in comment\n/- nested /- sorry -/ comment -/\ntheorem identity : True := by trivial\n')
        self.sha=hashlib.sha256(self.src.read_bytes()).hexdigest()
        self.manifest=self.base/'audit.json'
        self.run={'repository':'user/repo','run_id':42,'head_sha':'abc','workflow_name':'Formal CI'}
        self.claim={'id':'C1','title':'Example','scope':'finite','artifact':'Example.lean','sha256':self.sha,'ci_run':self.run,
                    'formal_statement':'theorem identity : True := by trivial'}
        self.save([self.claim])
    def tearDown(self): self.tmp.cleanup()
    def save(self,claims): self.manifest.write_text(json.dumps({'schema':'astra-prooflab-evidence/1','claims':claims}))
    def fetch(self,url): return {'head_sha':'abc','status':'completed','conclusion':'success','name':'Formal CI'}
    def test_valid_verified_claim(self):
        report=audit(self.manifest,self.fetch)
        self.assertEqual(report['summary']['PASS'],1)
        self.assertFalse(report['valuation_usd_verified'])
    def test_mismatch_to_formal_statement_rejected(self):
        self.save([{**self.claim,'formal_statement':'theorem impossible : False := by trivial'}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'FAIL')
    def test_without_statement_is_partial(self):
        self.save([{k:v for k,v in self.claim.items() if k!='formal_statement'}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'PARTIAL')
    def test_valid_asymptotic_claim_never_passes(self):
        self.save([{**self.claim,'scope':'asymptotic'}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'PARTIAL')
    def test_bad_sha_rejected(self):
        self.save([{**self.claim,'sha256':'0'*64}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'FAIL')
    def test_proof_escape_rejected(self):
        self.src.write_text('theorem bad : True := by sorry\n')
        self.save([{**self.claim,'sha256':hashlib.sha256(self.src.read_bytes()).hexdigest()}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'FAIL')
    def test_ci_sha_mismatch_rejected(self):
        self.assertEqual(audit(self.manifest,lambda url:{**self.fetch(url),'head_sha':'def'})['claims'][0]['status'],'FAIL')
    def test_unrelated_green_workflow_rejected(self):
        self.assertEqual(audit(self.manifest,lambda url:{**self.fetch(url),'name':'Other CI'})['claims'][0]['status'],'FAIL')
    def test_ci_failure_rejected(self):
        self.assertEqual(audit(self.manifest,lambda url:{**self.fetch(url),'conclusion':'failure'})['claims'][0]['status'],'FAIL')
    def test_network_unavailable_unverified(self):
        def fail(url): raise TimeoutError()
        self.assertEqual(audit(self.manifest,fail)['claims'][0]['status'],'UNVERIFIED')
    def test_no_ci_unverified(self):
        self.save([{k:v for k,v in self.claim.items() if k!='ci_run'}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'UNVERIFIED')
    def test_path_traversal_fails(self):
        self.save([{**self.claim,'artifact':'../foo'}])
        self.assertEqual(audit(self.manifest,self.fetch)['claims'][0]['status'],'FAIL')
    def test_lean_comment_strip(self):
        self.assertNotIn('sorry',strip_lean_comments('-- sorry\n/- sorry /- sorry -/ -/\ntheorem ok : True := by trivial'))
    def test_html_escaping(self):
        self.save([{**self.claim,'title':'<script>alert(1)</script>'}])
        page=render_html(audit(self.manifest,self.fetch))
        self.assertNotIn('<script>',page)
    def test_invalid_schema(self):
        self.manifest.write_text('{}')
        with self.assertRaises(ValueError): audit(self.manifest,self.fetch)
if __name__=='__main__':unittest.main()