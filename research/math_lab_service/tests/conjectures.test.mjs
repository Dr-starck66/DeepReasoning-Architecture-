import test from 'node:test';
import assert from 'node:assert/strict';
import {discoverCycle} from '../src/conjecture-engine.mjs';
test('synthesizes exact research in number theory, algebra, graphs',()=>{
 const r=discoverCycle('2026-11-23');assert.deepEqual(r.explored_domains,['number_theory','algebra','graph_theory']);
 assert.equal(r.counts.generated,3);assert.ok(r.candidates.some(x=>x.status==='PROVED_ELEMENTARY'));
 assert.equal(r.prize_solutions,0);assert.equal(r.originality,'UNVERIFIED');
});
test('two dates synthesize different conjectures',()=>{
 const a=discoverCycle('2026-11-23'),b=discoverCycle('2026-11-24');
 assert.notDeepEqual(a.candidate_ids,b.candidate_ids);
});
test('seen hypotheses are not silently reintroduced on same day',()=>{
 const a=discoverCycle('2026-11-23'),b=discoverCycle('2026-11-23',{seenIds:a.candidate_ids});
 assert.ok(b.candidate_ids.every(id=>!a.candidate_ids.includes(id)));
});
test('deterministic and self-audited',()=>{
 assert.deepEqual(discoverCycle('2026-11-23'),discoverCycle('2026-11-23'));
});
test('reject malformed date',()=>{
 for(const v of ['2026-02-30','2026-00-02','2025-13-07'])assert.throws(()=>discoverCycle(v));
});
test('exact polynomial certificate and finite-only graph gate',()=>{
 for(let d=23;d<29;d++){
  const r=discoverCycle(`2026-11-${d}`);
  for(const c of r.candidates){
   if(c.status==='PROVED_ELEMENTARY')assert.equal(c.proof.kind,'UNIVERSAL_EXACT');
   if(c.domain==='graph_theory')assert.ok(['FINITE_COUNTEREXAMPLE','FINITE_ONLY'].includes(c.proof.kind));
  }
 }
});
