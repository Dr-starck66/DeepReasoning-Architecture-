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
function statusLine(st,id,msg){const cls=st==='PASS'?'t-good':st==='FAIL'?'t-bad':'t-warn';return `<span class="${cls}">[${st}]</span> ${String(id).replaceAll('<','&lt;')} — ${String(msg).replaceAll('<','&lt;')}`;}
function cleanStatus(st){return ['PASS','PARTIAL','FAIL','UNVERIFIED'].includes(st)?st:'UNVERIFIED';}
function testSource(source,claim){const code=stripComments(source);const bad=/\b(sorry|admit|sorryAx|axiom|native_decide|unsafe)\b/;if(bad.test(code))return {status:'FAIL',reason:'Common proof escape detected (lexical check; not a semantic proof checker).'};
 const line=String(claim.formal_statement||'').replace(/\s+/g,' ').trim();if(!line||!line.startsWith('theorem ')||!line.includes(':='))return{status:'PARTIAL',reason:'No bounded Lean theorem statement attached.'};if(!code.replace(/\s+/g,' ').includes(line))return {status:'FAIL',reason:'Bounded theorem statement absent from artifact.'};return {status:'PASS',reason:'The bound theorem header exists and common proof escapes are absent.'};}
async function fetchWithTimeout(url,timeout=14000){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),timeout);try{const response=await fetch(url,{signal:controller.signal,headers:{'Accept':'application/vnd.github+json'}});if(!response.ok)throw Error('HTTP '+response.status);return response;}finally{clearTimeout(timer);}}
async function auditClaim(c,uploaded,cache){const outcome={id:String(c.id||'unknown'),scope:String(c.scope||'unknown'),title:String(c.title||''),status:'UNVERIFIED',checks:[],explanation:[]};
 if(!['finite','asymptotic','commercial','product'].includes(c.scope)){outcome.status='FAIL';outcome.explanation.push('Invalid or missing scope');return outcome;}
 if(!/^[a-f0-9]{64}$/.test(String(c.sha256||''))){outcome.status='FAIL';outcome.explanation.push('Invalid SHA-256 checksum');return outcome;}
 const run=c.ci_run;
 if(!run||!validRepo(run.repository)||!Number.isInteger(run.run_id)||run.run_id<1||!/^[a-f0-9]{40}$/.test(String(run.head_sha||''))||!validPath(run.repo_path)||!run.workflow_name){outcome.explanation.push('Missing or invalid independent GitHub CI evidence');return outcome;}
 if(uploaded&&uploaded.name!==String(c.artifact).split('/').pop()){outcome.status='FAIL';outcome.explanation.push('Selected artifact basename does not match manifest');return outcome;}
 let content,raw;
 try{const path=run.repo_path.split('/').map(encodeURIComponent).join('/');const key=run.repository+':'+run.head_sha+':'+run.repo_path;
  if(!cache.sources.has(key))cache.sources.set(key,await (await fetchWithTimeout(`https://raw.githubusercontent.com/${run.repository}/${run.head_sha}/${path}`)).arrayBuffer());
  raw=cache.sources.get(key);const sourceSha=await shahex(raw);
  if(sourceSha!==c.sha256){outcome.status='FAIL';outcome.explanation.push('Immutable GitHub source SHA-256 mismatch');return outcome;}
  outcome.checks.push('IMMUTABLE_SOURCE_SHA_MATCH');
  if(uploaded){const local=await uploaded.arrayBuffer();if(await shahex(local)!==c.sha256){outcome.status='FAIL';outcome.explanation.push('Local artifact SHA-256 mismatch');return outcome;}outcome.checks.push('LOCAL_SOURCE_SHA_MATCH');}
  content=new TextDecoder('utf-8',{fatal:true}).decode(raw);const proof=testSource(content,c);if(proof.status==='FAIL'){outcome.status='FAIL';outcome.explanation.push(proof.reason);return outcome;}if(proof.status==='PASS')outcome.checks.push('THEOREM_HEADER_BOUND');else outcome.explanation.push(proof.reason);
  const runKey=run.repository+':'+run.run_id;
  if(!cache.runs.has(runKey))cache.runs.set(runKey,await (await fetchWithTimeout(`https://api.github.com/repos/${run.repository}/actions/runs/${run.run_id}`)).json());
  const ci=cache.runs.get(runKey);
  if(ci.head_sha!==run.head_sha||ci.name!==run.workflow_name){outcome.status='FAIL';outcome.explanation.push('CI commit SHA or workflow name mismatch');return outcome;}
  if(ci.status!=='completed'){outcome.explanation.push('CI run is not completed');return outcome;}
  if(ci.conclusion!=='success'){outcome.status='FAIL';outcome.explanation.push('CI run was not successful');return outcome;}
  outcome.checks.push('CI_SUCCESS_ON_IMMUTABLE_COMMIT');
  outcome.status=c.scope==='finite'&&proof.status==='PASS'?'PASS':'PARTIAL';
  outcome.explanation.push(outcome.status==='PASS'?'Evidence-chain PASS only: no scientific semantic certification.':'This scope exceeds what the finite Lean evidence establishes.');
  outcome.ci_url=ci.html_url;
  return outcome;
 }catch(error){outcome.status='UNVERIFIED';outcome.explanation.push('Public GitHub could not be independently queried: '+(error.name==='AbortError'?'timeout':String(error.message).slice(0,120)));return outcome;}
}
function displayReceipt(r){const items=r.claims;const lines=[`$ prooflab audit --source ${r.source}`,'',`Audit ${r.name}`,`Timestamp ${r.timestamp}`,`Claims ${items.length}`,''];for(const c of items){lines.push(statusLine(c.status,c.id,c.title));for(const x of c.checks)lines.push('  + '+x);for(const x of c.explanation)lines.push('  > '+x);if(c.ci_url)lines.push('  < '+c.ci_url);lines.push('');}lines.push('Safeguard: green CI verifies only the named evidence chain, not the global mathematical claim.');$('results').innerHTML=lines.join('\n');let overall=items.some(i=>i.status==='FAIL')?'FAIL':items.some(i=>i.status==='UNVERIFIED')?'UNVERIFIED':items.some(i=>i.status==='PARTIAL')?'PARTIAL':items.every(i=>i.status==='PASS')?'PASS':'UNVERIFIED';$('current-status').className='badge '+overall.toLowerCase();$('current-status').textContent=overall;$('current-message').textContent=overall==='PASS'?'The bounded evidence chain was checked against public GitHub.':overall==='PARTIAL'?'Some scientific or business claims exceed the checked evidence.':overall==='UNVERIFIED'?'Public evidence is unavailable or incomplete.':'At least one mandatory evidence check failed.';}
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
$('sample-mode').addEventListener('click',()=>changeMode('sample'));
$('upload-mode').addEventListener('click',()=>changeMode('upload'));
$('check').addEventListener('click',audit);
$('export').addEventListener('click',download);
window.ASTRA_PROOFLAB_TEST={shahex,stripComments,validRepo,validPath,testSource,cleanStatus,auditClaim,changeMode};