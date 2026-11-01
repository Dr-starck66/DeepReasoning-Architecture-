#!/usr/bin/env python3
"""ASTRA ProofLab evidence gate. Standard library only; conservative, auditable.

This checks artifact integrity, easy-to-miss proof escapes and independently
retrieved GitHub Actions statuses. It CANNOT establish mathematical meaning,
innovation, patentability, customer demand, or commercial valuation.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import urllib.request

STATES = ("PASS", "PARTIAL", "FAIL", "UNVERIFIED")
FORBIDDEN = re.compile(r'\b(sorry|admit|sorryAx|axiom|native_decide|unsafe)\b')
VALID_SCOPE = {"finite", "asymptotic", "product", "commercial"}


def strip_lean_comments(code: str) -> str:
    """Remove Lean /- -/ nested block and -- line comments, preserve string contents.

    Conservative: strings may be scanned for forbidden words. This creates
    false negatives for PASS, never makes unproven code PASS.
    """
    out = []
    i, depth = 0, 0
    while i < len(code):
        if code.startswith('/-', i):
            depth += 1; i += 2
        elif depth and code.startswith('-/', i):
            depth -= 1; i += 2
        elif depth:
            i += 1
        elif code.startswith('--', i):
            end = code.find('\n', i)
            i = len(code) if end == -1 else end
        else:
            out.append(code[i]); i += 1
    if depth:
        raise ValueError('Unterminated Lean block comment')
    return ''.join(out)


def resolve_within(base: Path, reference: str) -> Path:
    root = base.resolve()
    path = (base / reference).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Artifact escapes manifest directory')
    return path


def github_run(repo: str, run_id: int, fetcher=None):
    if not re.fullmatch(r'[\w.\-]+/[\w.\-]+', repo):
        raise ValueError('Invalid repository name')
    if not isinstance(run_id, int) or run_id < 1:
        raise ValueError('Invalid run ID')
    url = f'https://api.github.com/repos/{repo}/actions/runs/{run_id}'
    if fetcher is not None:
        return fetcher(url)
    request = urllib.request.Request(url, headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'ASTRA-ProofLab-Evidence-Gate'})
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def audit(manifest_path: Path, fetcher=None) -> dict:
    manifest_path = Path(manifest_path)
    data = json.loads(manifest_path.read_text(encoding='utf-8'))
    if data.get('schema') != 'astra-prooflab-evidence/1':
        raise ValueError('Unsupported manifest schema')
    base = manifest_path.parent
    claims = []
    for c in data.get('claims', []):
        if not all(k in c for k in ('id', 'title', 'scope', 'artifact', 'sha256')):
            raise ValueError('Missing mandatory claim field')
        if c['scope'] not in VALID_SCOPE:
            raise ValueError('Invalid claim scope')
        report = {'id': str(c['id']), 'title': str(c['title']), 'scope': c['scope'],
                  'status': 'UNVERIFIED', 'checks': [], 'rationale': []}
        try:
            artifact = resolve_within(base, c['artifact'])
            content = artifact.read_bytes()
        except Exception as exc:
            report['status'] = 'FAIL'
            report['rationale'].append(f'Artifact read failed: {type(exc).__name__}')
            claims.append(report)
            continue
        digest = hashlib.sha256(content).hexdigest()
        if not re.fullmatch('[a-f0-9]{64}', str(c['sha256'])) or digest != c['sha256']:
            report['status'] = 'FAIL'
            report['rationale'].append('Artifact SHA-256 mismatch')
            claims.append(report)
            continue
        report['checks'].append('SHA256_MATCH')
        if artifact.suffix == '.lean':
            try:
                code = strip_lean_comments(content.decode('utf-8'))
            except Exception as exc:
                report['status'] = 'FAIL'; report['rationale'].append(f'Lean parse failed: {exc}')
                claims.append(report); continue
            bad = sorted(set(FORBIDDEN.findall(code)))
            if bad:
                report['status'] = 'FAIL'; report['rationale'].append('Forbidden proof escapes: ' + ', '.join(bad))
                claims.append(report); continue
            report['checks'].append('NO_COMMON_PROOF_ESCAPES')
        ci = c.get('ci_run')
        if not isinstance(ci, dict) or not all(k in ci for k in ('repository', 'run_id', 'head_sha')):
            report['status'] = 'UNVERIFIED'
            report['rationale'].append('No independent CI evidence; hash alone does not verify proofs')
        else:
            try:
                record = github_run(ci['repository'], ci['run_id'], fetcher)
                if record.get('head_sha') != ci['head_sha']:
                    report['status'] = 'FAIL'
                    report['rationale'].append('GitHub CI SHA mismatch')
                elif record.get('conclusion') != 'success' or record.get('status') != 'completed':
                    report['status'] = 'FAIL' if record.get('status') == 'completed' else 'UNVERIFIED'
                    report['rationale'].append(f'GitHub CI state: {record.get("status")}/{record.get("conclusion")}')
                else:
                    report['status'] = 'PASS' if c['scope'] == 'finite' else 'PARTIAL'
                    report['checks'].append('GITHUB_CI_SUCCESS_ON_EXACT_SHA')
            except Exception as exc:
                report['status'] = 'UNVERIFIED'
                report['rationale'].append(f'Independent CI unavailable: {type(exc).__name__}')
        if c['scope'] != 'finite':
            if report['status'] == 'PASS':
                report['status'] = 'PARTIAL'
            report['rationale'].append('Scope is not established by artifact hash + CI alone')
        if c['scope'] == 'finite' and report['status'] == 'PASS':
            report['rationale'].append('Only specified finite-file CI checks pass; scientific equivalence needs expert review')
        claims.append(report)
    summary = {s: sum(c['status'] == s for c in claims) for s in STATES}
    return {'schema': 'astra-prooflab-audit/1', 'name': data.get('name','unnamed'),
            'summary':summary, 'claims':claims, 'valuation_usd_verified':False,
            'warnings':['A CI success is not a proof of natural-language scope.',
                        'The verifier cannot certify economic value, IP novelty, or customer demand.',
                        'Without an independently fetched CI response the status is UNVERIFIED.']}


def render_html(report: dict):
    items=''.join('<tr><td>'+html.escape(c['id'])+'</td><td>'+html.escape(c['title'])+
        '</td><td>'+html.escape(c['scope'])+'</td><td class="'+c['status'].lower()+'">'+c['status']+
        '</td><td>'+html.escape('; '.join(c['rationale']))+'</td></tr>' for c in report['claims'])
    return '<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>ASTRA ProofLab — Audit</title><style>body{font:16px system-ui;background:#071522;color:#f0f9ff;max-width:1000px;padding:2rem;margin:auto}table{width:100%;border-collapse:collapse}td,th{border:1px solid #2f4662;text-align:left;padding:12px}.pass{color:#68edab}.fail{color:#ff8a8a}.partial,.unverified{color:#ffd084}p{line-height:1.6}</style><h1>ASTRA ProofLab · Rapport d’audit</h1><p>Rapport reproductible. Une validation de fichier ou de CI ne valide ni le théorème global, ni la propriété intellectuelle, ni une valorisation financière.</p><table><thead><tr><th>ID</th><th>Affirmation</th><th>Périmètre</th><th>Statut</th><th>Limites</th></tr></thead><tbody>'+items+'</tbody></table></html>'


def main(argv=None):
    parser=argparse.ArgumentParser(description='Verify ASTRA claim artifacts against independent GitHub CI')
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--html',type=Path)
    args=parser.parse_args(argv)
    report=audit(args.manifest)
    encoded=json.dumps(report,ensure_ascii=False,indent=2)+'\n'
    if args.output:
        args.output.write_text(encoded,encoding='utf-8')
    if args.html:
        args.html.write_text(render_html(report),encoding='utf-8')
    print(encoded)
    return 2 if report['summary']['FAIL'] else (1 if report['summary']['UNVERIFIED'] else 0)
if __name__ == '__main__':
    sys.exit(main())