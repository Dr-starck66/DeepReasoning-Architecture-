#!/usr/bin/env python3
"""TOPOQUANTUM -> existing ASTRA ProofGate contract (fail-closed).

`proof_gate.py` is deliberately imported from the pre-existing sibling module,
never copied, replaced, or silently bypassed. Without independent GitHub Actions
SHA evidence the ProofGate claims must remain UNVERIFIED.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from majorana import assess

HERE=Path(__file__).resolve().parent
GATE_PARENT=HERE.parent


def sha(data: bytes)->str:
    return hashlib.sha256(data).hexdigest()


def build_bundle(out:Path)->tuple[Path,dict]:
    out=Path(out)
    out.mkdir(parents=True,exist_ok=True)
    receipt=assess()
    receipt_path=out/'topoquantum_finite.json'
    raw=(json.dumps(receipt,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
    receipt_path.write_bytes(raw)
    formal_source=HERE/'TopoQuantumFinite.lean'
    formal_snapshot=out/formal_source.name
    shutil.copyfile(formal_source,formal_snapshot)
    # Gate manifest is intentionally CI-free. Never claim a Lean PASS without a real run.
    manifest={
       'schema':'astra-prooflab-evidence/1',
       'name':'ASTRA TOPOQUANTUM finite BdG to existing ASTRA ProofGate',
       'claims':[
          {'id':'TOPOQUANTUM-BDG-EXACT-LOCAL',
           'title':'BdG exact finite checks (local computational evidence, not formal)',
           'scope':'finite','artifact':receipt_path.name,'sha256':sha(raw)},
          {'id':'TOPOQUANTUM-LEAN-N2',
           'title':'Lean N=2 explicit BdG left/right kernel checks (compilation pending)',
           'scope':'finite','artifact':formal_snapshot.name,'sha256':sha(formal_snapshot.read_bytes()),
           'formal_statement':'theorem left_exact_zero : ∀ i : Fin 4, h2 i 0 - h2 i 2 = 0 := by decide'},
       ],
    }
    p=out/'proofgate_manifest.json'
    p.write_text(json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False)+'\n')
    return p,receipt


def call_existing_gate(manifest_path:Path)->dict:
    if not (GATE_PARENT/'proof_gate.py').is_file():
        return {'status':'UNVERIFIED','reason':'Existing ASTRA proof_gate.py unavailable in this checkout'}
    sys.path.insert(0,str(GATE_PARENT))
    try:
        from proof_gate import audit
        result=audit(manifest_path)
        # An accidentally green local hash must not promote the absent-CI proof.
        if any(c['status']=='PASS' for c in result['claims']):
            return {'status':'FAIL','reason':'Unexpected PASS without verified independent CI'}
        return {'status':'PASS' if all(c['status']=='UNVERIFIED' for c in result['claims']) else 'FAIL',
                'gate_claims':result['claims'],'summary':result['summary'],
                'interpretation':'Integration with ASTRA ProofGate ran; substantive claims remain UNVERIFIED without real Lean CI.'}
    except Exception as exc:
        return {'status':'FAIL','reason':type(exc).__name__+': '+str(exc)}


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(argv)
    manifest,finite=build_bundle(args.out)
    gate=call_existing_gate(manifest)
    report={'schema':'astra-topoquantum-bridge/1','finite_computation_status':finite['finite_computation_status'],
            'existing_proofgate_integration':gate,'lean_compilation':'UNVERIFIED','external_independent_validation':'UNVERIFIED'}
    (args.out/'bridge_result.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True,indent=2))
    return 2 if finite['finite_computation_status']=='FAIL' or gate['status']=='FAIL' else 0

if __name__=='__main__': raise SystemExit(main())
