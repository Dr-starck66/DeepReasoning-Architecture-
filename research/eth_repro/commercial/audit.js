'use strict';
/* Browser-only evidence verifier. NEVER treats a green CI as proof of a natural-language theorem. */
const R = 'Dr-starck66/DeepReasoning-Architecture-';
const SAMPLE = {
  schema:'astra-prooflab-evidence/1',name:'ASTRA low-rank finite replica — live public sample',
  claims:[{
    id:'LOWRANK-FINITE-001', title:'Four-coordinate rank-one factorization (finite Lean statement)',
    scope:'finite', artifact:'LowRankExact.lean',
    sha256:'70f700f825f6ed8a24fcc55243bfb7a1e83ac3412c773cce63dca26d7494a640',
    formal_statement:'theorem rank_one_factor : ∀ i j : Fin 4, matrixDifference i j = sign i * sign j := by decide',
    ci_run:{repository:R,run_id:41289478387,head_sha:'5f0521ad8e2a127ba9f147372ddd73fa78757d3d',workflow_name:'ASTRA MATH LAB - Lean 4 formal check',repo_path:'research/eth_repro/LowRankExact.lean'}
  },{
    id:'LOWRANK-ASYMPTOTIC-002',title:'Claim that the general subexponential bound is reproduced',scope:'asymptotic',
    artifact:'LowRankExact.lean',sha256:'70f700f825f6ed8a24fcc55243bfb7a1e83ac3412c773cce63dca26d7494a640',
    formal_statement:'theorem rank_one_factor : ∀ i j : Fin 4, matrixDifference i j = sign i * sign j := by decide',
    ci_run:{repository:R,run_id:41289478387,head_sha:'5f0521ad8e2a127ba9f147372ddd73fa78757d3d',workflow_name:'ASTRA MATH LAB - Lean 4 formal check',repo_path:'research/eth_repro/LowRankExact.lean'}
  }]
};
const $ = id => document.getElementById(id);
const text = new TextEncoder();
let mode='sample', receipt=null;
function shahex(buffer){return crypto.subtle.digest('SHA-256',buffer).then(a=>Array.from(new Uint8Array(a),n=>n.toString(16).padStart(2,'0')).join(''));}
function stripComments(src){let out='', i=0, depth=0;while(i<src.length){if(src.slice(i,i+2)==='/-'){depth++;i+=2;continue;}if(depth&&src.slice(i,i+2)==='-/'){depth--;i+=2;continue;}if(depth){i++;continue;}if(src.slice(i,i+2)==='--'){while(i<src.length&&src[i]!=='\n')i++;continue;}out+=src[i];i++;}if(depth)throw Error('Unterminated Lean comment');return out;}
function validRepo(s){return typeof s==='string'&&/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(s);}
function validPath(s){return typeof s==='string'&&/^[\w.\-/]+$/.test(s)&&!s.startsWith('/')&&!s.split('/').includes('..')&&!s.split('/').includes('.');}
function statusLine(st, id, msg) {
  return '[' + cleanStatus(st) + '] ' + String(id) + ' — ' + String(msg);
}
function displayReceipt(r){const items=r.claims;const lines=[`$ prooflab audit --source ${r.source}`,'',`Audit ${r.name}`,`Timestamp ${r.timestamp}`,`Claims ${items.length}`,''];for(const c of items){lines.push(statusLine(c.status,c.id,c.title));for(const x of c.checks)lines.push('  + '+x);for(const x of c.explanation)lines.push('  > '+x);if(c.ci_url)lines.push('  < '+c.ci_url);lines.push('');}lines.push('Safeguard: green CI verifies only the named evidence chain, not the global mathematical claim.');$('results').textContent=lines.join('\n');let overall=items.some(i=>i.status==='FAIL')?'FAIL':items.some(i=>i.status==='UNVERIFIED')?'UNVERIFIED':items.some(i=>i.status==='PARTIAL')?'PARTIAL':items.every(i=>i.status==='PASS')?'PASS':'UNVERIFIED';$('current-status').className='badge '+overall.toLowerCase();$('current-status').textContent=overall;$('current-message').textContent=overall==='PASS'?'The bounded evidence chain was checked against public GitHub.':overall==='PARTIAL'?'Some scientific or business claims exceed the checked evidence.':overall==='UNVERIFIED'?'Public evidence is unavailable or incomplete.':'At least one mandatory evidence check failed.';}
async function audit(){const btn=$('check');btn.disabled=true;$('export').disabled=true;receipt=null;$('current-status').textContent='CHECKING';$('current-status').className='badge pending';$('current-message').textContent='Checking GitHub immutable source and CI...';$('results').textContent='$ Connecting to public GitHub endpoints...';
 try{let manifest,artifact=null;if(mode==='sample')manifest=structuredClone(SAMPLE);else{const mf=$('manifest-file').files[0];artifact=$('lean-file').files[0];if(!mf||!artifact)throw Error('Select both the JSON manifest and a Lean file.');if(mf.size>1024*1024||artifact.size>1024*1024)throw Error('Upload limited to 1 MB per file.');manifest=JSON.parse(await mf.text());}
  if(manifest.schema!=='astra-prooflab-evidence/1'||!Array.isArray(manifest.claims)||!manifest.claims.length||manifest.claims.length>10)throw Error('Unsupported evidence manifest: expected 1–10 claims.');
  const cache={runs:new Map(),sources:new Map()};const claims=[];for(const c of manifest.claims)claims.push(await auditClaim(c,artifact,cache));
  receipt={schema:'astra-prooflab-audit/1',generated_by:'ASTRA ProofLab browser verifier v1',name:String(manifest.name||'unnamed'),timestamp:new Date().toISOString(),source:mode,claims,warnings:['A green GitHub CI run does not prove the scientific scope of a natural-language claim.','No accreditation, economic valuation, exclusivity or originality is certified.','This JSON export is not digitally signed.']};displayReceipt(receipt);$('export').disabled=false;
 }catch(error){$('current-status').textContent='FAIL';$('current-status').className='badge fail';$('current-message').textContent=String(error.message);$('results').textContent='Input validation failure: '+String(error.message);}
 finally{btn.disabled=false;}
}
function changeMode(which){mode=which;$('sample-panel').hidden=which!=='sample';$('upload-panel').hidden=which!=='upload';for(const x of ['sample','upload']){$(x+'-mode').classList.toggle('selected',x===which);$(x+'-mode').setAttribute('aria-pressed',String(x===which));}$('results').textContent='$ Select an evidence source and run an independent check.';$('current-status').className='badge pending';$('current-status').textContent='NOT CHECKED';$('current-message').textContent='Run a live check to obtain a receipt.';$('export').disabled=true;receipt=null;}
function download(){if(!receipt)return;const url=URL.createObjectURL(new Blob([JSON.stringify(receipt,null,2)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download='astra-prooflab-audit-'+new Date().toISOString().slice(0,10)+'.json';document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);}

/* Live evidence checks. Every PASS is limited to the identified public
   artifact + checksum + GitHub CI metadata, not theorem semantics. */
function cleanStatus(s){
  return ['PASS','PARTIAL','FAIL','UNVERIFIED'].includes(s)?s:'UNVERIFIED';
}
function testSource(src,claim){
  const checks=[], explanation=[];
  if(typeof src!=='string'||!src.trim())return {status:'FAIL',checks,explanation:['EMPTY_LEAN_SOURCE']};
  if(typeof claim?.formal_statement!=='string'||!claim.formal_statement.trim())
    return {status:'FAIL',checks,explanation:['MISSING_FORMAL_STATEMENT']};
  let uncommented;
  try {uncommented=stripComments(src);}catch(e){
    return {status:'FAIL',checks,explanation:[String(e.message)]};
  }
  const norm=s=>s.replace(/\s+/g,' ').trim();
  if(!norm(uncommented).includes(norm(claim.formal_statement)))
    return {status:'FAIL',checks,explanation:['FORMAL_STATEMENT_NOT_FOUND_IN_EXACT_SOURCE']};
  checks.push('Exact normalized theorem statement located outside Lean comments');
  if(/\b(?:sorry|admit|axiom|native_decide|unsafe)\b/.test(uncommented))
    return {status:'FAIL',checks,explanation:['POTENTIAL_PROOF_ESCAPE_IN_SOURCE_REQUIRES_EXPERT_REVIEW']};
  checks.push('No lexical sorry/admit/axiom/native_decide/unsafe tokens detected outside comments');
  return {status:'PASS',checks,explanation:['Lexical inspection is not Lean kernel verification; imported axioms and semantics need independent review.']};
}
async function auditClaim(c,artifact,cache){
  const out={id:String(c?.id||'UNKNOWN'),title:String(c?.title||'Untitled claim'),
    status:'UNVERIFIED',checks:[],explanation:[],ci_url:null};
  const fail=msg=>{out.status='FAIL';out.explanation.push(msg);return out;};
  const unknown=msg=>{out.status='UNVERIFIED';out.explanation.push(msg);return out;};
  const run=c?.ci_run;
  if(!run||!validRepo(run.repository)||!Number.isSafeInteger(run.run_id)||run.run_id<=0||
    typeof run.head_sha!=='string'||!/^[0-9a-f]{40}$/i.test(run.head_sha)||
    !validPath(run.repo_path)||typeof run.workflow_name!=='string'||!run.workflow_name.trim()||
    typeof c.sha256!=='string'||!/^[0-9a-f]{64}$/i.test(c.sha256))
    return fail('MALFORMED_REPOSITORY_RUN_PATH_OR_CHECKSUM');
  if(artifact&&artifact.name!==String(c.artifact||''))
    return fail('UPLOADED_ARTIFACT_NAME_MISMATCH');
  const root='https://api.github.com/repos/'+run.repository;
  const runUrl=root+'/actions/runs/'+run.run_id;
  const srcUrl='https://raw.githubusercontent.com/'+run.repository+'/'+run.head_sha+'/'+run.repo_path;
  out.ci_url='https://github.com/'+run.repository+'/actions/runs/'+run.run_id;
  const fetchOnce=async (url,map)=>{
    if(!map.has(url)){
      map.set(url,(async()=>{
        const ac=new AbortController(),tid=setTimeout(()=>ac.abort(),12000);
        try{
          const response=await fetch(url,{headers:{'Accept':'application/vnd.github+json'},signal:ac.signal});
          if(response.status===404)return {ok:false,kind:'NOT_FOUND'};
          if(!response.ok)return {ok:false,kind:'HTTP_'+response.status};
          return {ok:true,content:await response.text()};
        }finally{clearTimeout(tid);}
      })());
    }
    return map.get(url);
  };
  let runResult,sourceResult;
  try {
    [runResult,sourceResult]=await Promise.all([
      fetchOnce(runUrl,cache.runs),fetchOnce(srcUrl,cache.sources)
    ]);
  }catch(error){
    return unknown('LIVE_PUBLIC_GITHUB_REQUEST_FAILED: '+String(error.message||error));
  }
  if(!runResult.ok)return runResult.kind==='NOT_FOUND'?fail('CI_RUN_NOT_FOUND'):unknown('CI_RUN_'+runResult.kind);
  if(!sourceResult.ok)return sourceResult.kind==='NOT_FOUND'?fail('PINNED_LEAN_SOURCE_NOT_FOUND'):unknown('PINNED_SOURCE_'+sourceResult.kind);
  let evidence;
  try{evidence=JSON.parse(runResult.content);}catch(_){return unknown('INVALID_GITHUB_RUN_RESPONSE');}
  if(evidence.id!==undefined&&Number(evidence.id)!==run.run_id)
    return fail('CI_RUN_ID_MISMATCH');
  if(evidence.repository?.full_name&&evidence.repository.full_name!==run.repository)
    return fail('CI_REPOSITORY_MISMATCH');
  if(evidence.head_sha!==run.head_sha)return fail('CI_HEAD_COMMIT_MISMATCH');
  if(evidence.name!==run.workflow_name)return fail('CI_WORKFLOW_NAME_MISMATCH');
  if(evidence.status!=='completed')return unknown('CI_NOT_COMPLETED');
  if(evidence.conclusion!=='success')return fail('CI_NOT_SUCCESSFUL');
  out.checks.push('Completed successful CI run matched repository, workflow and pinned head SHA');
  const source=sourceResult.content;
  let digest;
  try{digest=await shahex(text.encode(source));}catch(error){
    return unknown('WEBCRYPTO_SHA256_UNAVAILABLE: '+String(error.message||error));
  }
  if(digest.toLowerCase()!==c.sha256.toLowerCase())return fail('PINNED_LEAN_FILE_SHA256_MISMATCH');
  out.checks.push('Immutable public Lean source SHA-256 matches supplied manifest');
  if(artifact){
    let uploadedHash;
    try{uploadedHash=await shahex(await artifact.arrayBuffer());}
    catch(error){return unknown('LOCAL_ARTIFACT_READ_FAILED: '+String(error.message||error));}
    if(uploadedHash!==digest)return fail('UPLOADED_LEAN_FILE_SHA256_MISMATCH');
    out.checks.push('Local supplied Lean artifact matches pinned source and manifest');
  }
  const lexical=testSource(source,c);
  out.checks.push(...lexical.checks);out.explanation.push(...lexical.explanation);
  if(lexical.status!=='PASS')return fail('SOURCE_LEXICAL_GATE_FAILED');
  if(c.scope!=='finite'){
    out.status='PARTIAL';
    out.explanation.push('Asymptotic or unbounded scientific claims are NOT established by a finite Lean example.');
  }else{
    out.status='PASS';
    out.explanation.push('Evidence-chain PASS only: matching source, hash, theorem header and run metadata; no guarantee of theorem semantics or IP.');
  }
  return out;
}

$('sample-mode').addEventListener('click',()=>changeMode('sample'));
$('upload-mode').addEventListener('click',()=>changeMode('upload'));
$('check').addEventListener('click',audit);
$('export').addEventListener('click',download);
window.ASTRA_PROOFLAB_TEST={shahex,stripComments,validRepo,validPath,testSource,cleanStatus,auditClaim,changeMode};