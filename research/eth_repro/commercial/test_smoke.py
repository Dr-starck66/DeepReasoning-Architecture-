"""ASTRA ProofLab browser integration tests, all public-network calls mocked and marked as such.
This proves frontend integrity, NOT real CI/production API availability.
"""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).parent
LEAN='import Lean\nnamespace Test\ntheorem toy : 1 + 1 = 2 := by decide\nend Test\n'
SHA='a'*40
REPO='public-lab/proof'
PATH='Proof.lean'

class ProofLabBrowser(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        s=socket.socket();s.bind(('127.0.0.1',0));cls.port=s.getsockname()[1];s.close()
        cls.server=subprocess.Popen([sys.executable,'-m','http.server',str(cls.port),'--directory',str(ROOT)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(30):
            try:
                from urllib.request import urlopen
                with urlopen(f'http://localhost:{cls.port}/') as r:
                    if r.status==200:break
            except Exception:time.sleep(.1)
        cls.sync=sync_playwright().start()
        cls.browser=cls.sync.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.sync.stop();cls.server.terminate();cls.server.wait(timeout=5)

    def setUp(self):
        self.context=self.browser.new_context(accept_downloads=True,viewport={'width':1280,'height':800})
        self.page=self.context.new_page()
        self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        html=(ROOT/'index.html').read_text()
        html=html.replace('<link rel="stylesheet" href="/styles.css">', '<style>'+(ROOT/'styles.css').read_text()+'</style>')
        html=html.replace('<script src="/audit.js" defer></script>', '<script>'+(ROOT/'audit.js').read_text()+'</script>')
        self.page.set_content(html,wait_until='load')
        # about:blank is administratively forced by this test environment and lacks WebCrypto.
        # Bridge digest to Python hashlib for tests only, without changing product code.
        self.page.expose_function('hostSha256', lambda values: list(hashlib.sha256(bytes(values)).digest()))
        self.page.evaluate("""Object.defineProperty(window,'crypto',{configurable:true,value:{subtle:{digest:async(_,data)=>new Uint8Array(await window.hostSha256(Array.from(new Uint8Array(data)))).buffer}}});""")

    def tearDown(self):
        self.assertEqual([],self.errors)
        self.context.close()

    def manifest(self,scope='finite',altered=False):
        return {'schema':'astra-prooflab-evidence/1','name':'Browser integration synthetic test',
          'claims':[{'id':'TEST001','title':'Exact source and CI evidence', 'scope':scope,
           'artifact':'Proof.lean','sha256':('0'*64 if altered else hashlib.sha256(LEAN.encode()).hexdigest()),
           'formal_statement':'theorem toy : 1 + 1 = 2 := by decide',
           'ci_run':{'repository':REPO,'run_id':123,'head_sha':SHA,'workflow_name':'Lean check','repo_path':PATH}}]}
    def mock_ci(self,success=True):
        self.page.route('https://raw.githubusercontent.com/**',lambda route:route.fulfill(status=200,body=LEAN,headers={'Access-Control-Allow-Origin':'*'}))
        self.page.route('https://api.github.com/**',lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps({'head_sha':SHA,'name':'Lean check','status':'completed','conclusion':'success' if success else 'failure','html_url':'https://github.com/public-lab/proof/actions/runs/123'}),headers={'Access-Control-Allow-Origin':'*'}))
    def upload(self,manifest,lean=LEAN):
        self.page.locator('#upload-mode').click()
        self.page.locator('#manifest-file').set_input_files({'name':'manifest.json','mimeType':'application/json','buffer':json.dumps(manifest).encode()})
        self.page.locator('#lean-file').set_input_files({'name':'Proof.lean','mimeType':'text/plain','buffer':lean.encode()})
        self.page.locator('#check').click()
        self.page.locator('#check:enabled').wait_for(timeout=15000)

    def test_01_home_sales_offer_visible(self):
        assert self.page.title().startswith('ASTRA ProofLab')
        assert '€2,900' in self.page.locator('.price').inner_text()
        assert self.page.locator('#request-link').get_attribute('href').startswith('mailto:')
        self.assertEqual(self.page.locator('#current-status').inner_text(),'NOT CHECKED')

    def test_02_mobile_no_horizontal_overflow(self):
        self.page.set_viewport_size({'width':375,'height':812})
        self.assertTrue(self.page.locator('#check').is_visible())
        overflow=self.page.evaluate('document.documentElement.scrollWidth>innerWidth')
        self.assertFalse(overflow)

    def test_03_no_manufactured_pass_offline(self):
        self.page.route('https://api.github.com/**',lambda route:route.abort())
        self.page.route('https://raw.githubusercontent.com/**',lambda route:route.abort())
        self.page.locator('#check').click()
        self.page.locator('#check:enabled').wait_for(timeout=15000)
        self.assertEqual(self.page.locator('#current-status').inner_text(),'UNVERIFIED')

    def test_04_missing_files_fail(self):
        self.page.locator('#upload-mode').click()
        self.page.locator('#check').click()
        self.page.locator('#check:enabled').wait_for(timeout=15000)
        self.assertEqual(self.page.locator('#current-status').inner_text(),'FAIL')

    def test_05_evidence_pass_scoped(self):
        self.mock_ci(); self.upload(self.manifest())
        self.assertEqual(self.page.locator('#current-status').inner_text(),'PASS')
        self.assertIn('Evidence-chain PASS only',self.page.locator('#results').inner_text())
        self.assertTrue(self.page.locator('#export').is_enabled())

    def test_06_asymptotic_not_approved(self):
        self.mock_ci();self.upload(self.manifest(scope='asymptotic'))
        self.assertEqual(self.page.locator('#current-status').inner_text(),'PARTIAL')

    def test_07_wrong_hash_rejected(self):
        self.mock_ci();self.upload(self.manifest(altered=True))
        self.assertEqual(self.page.locator('#current-status').inner_text(),'FAIL')

    def test_08_ci_failure_rejected(self):
        self.mock_ci(success=False);self.upload(self.manifest())
        self.assertEqual(self.page.locator('#current-status').inner_text(),'FAIL')

    def test_09_wrong_source_file_rejected(self):
        self.mock_ci();self.upload(self.manifest(),LEAN+'-- changed after commit\n')
        self.assertEqual(self.page.locator('#current-status').inner_text(),'FAIL')

if __name__=='__main__':unittest.main(verbosity=2)