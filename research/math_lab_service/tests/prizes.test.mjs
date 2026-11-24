import test from 'node:test';
import assert from 'node:assert/strict';
import {fltReduction,verifyPowerEquality,verifyPrimitiveCounterexample,searchTriple,independentOracle,prizeCycle} from '../src/prize-engine.mjs';
import handler from '../api/prizes.mjs';
const mock=()=>({code:0,body:null,headers:{},setHeader(k,v){this.headers[k]=v;},status(v){this.code=v;return this;},json(v){this.body=v;return this;}});
test('Beal classical reduction exact for triples sharing exponent divisor >=3',()=>{
 const p=fltReduction(6,9,12);assert.equal(p.common_exponent_divisor,3);
 assert.equal(p.reduced_equation,'X^3+Y^3=Z^3');
 assert.equal(p.status,'CLASSICAL_CASE_CLOSED');
 assert.equal(fltReduction(4,6,8).status,'NOT_CLOSED_BY_THIS_REDUCTION');
 assert.equal(fltReduction(3,4,5).status,'NOT_CLOSED_BY_THIS_REDUCTION');
});
test('known Beal equality is NOT a primitive counterexample',()=>{
 const w={A:3,B:6,C:3,x:3,y:3,z:5};
 assert(verifyPowerEquality(w));assert.equal(verifyPrimitiveCounterexample(w),false);
 assert.equal(verifyPowerEquality({...w,C:4}),false);
 assert.equal(verifyPrimitiveCounterexample({...w,A:1,B:1,C:1}),false);
});
test('optimized search matches independent 3-loop BigInt oracle',()=>{
 for(const t of [[3,3,3],[3,3,5],[4,6,8],[3,4,5]]){
  const s=searchTriple(...t,{maxBase:9}),ind=independentOracle(...t,9);
  assert.equal(s.exact_equalities,ind.equalities);assert.equal(s.primitive_counterexamples,ind.primitive);
 }
});
test('finite no-hit never becomes a proof or prize claim',()=>{
 const r=searchTriple(3,3,5,{maxBase:9});assert(r.nonprimitive_equalities>0);
 assert.equal(r.scope,'FINITE_BASES_ONLY');assert.equal(r.general_case,'UNVERIFIED');assert.equal(r.prize_solution,false);
});
test('216 exponent patterns, 18 classical reductions, 6 exact explored',()=>{
 const a=prizeCycle('2026-11-24'),b=prizeCycle('2026-11-24');
 assert.deepEqual(a,b);assert.equal(a.exponent_triples_total,216);
 assert.equal(a.exponent_triples_classically_closed,18);assert.equal(a.exponent_triples_not_closed_by_flt,198);
 assert.equal(a.exact_triples_checked,6);assert.equal(a.conclusions.primitive_witnesses_found,0);
 assert.equal(a.prize_eligible,false);
});
test('memory rotation avoids studied exponent triples',()=>{
 const a=prizeCycle('2026-11-24'),b=prizeCycle('2026-11-24',{seenIds:a.candidate_ids});
 assert.equal(b.candidate_ids.filter(x=>a.candidate_ids.includes(x)).length,0);
});
test('public API rejects malformed data and invalid methods',()=>{
 let r=mock();handler({method:'GET',query:{date:'2026-11-24',round:'0'}},r);
 assert.equal(r.code,200);assert.equal(r.body.award_problem,'Beal conjecture');
 for(const q of [{date:'2026-02-30'},{date:'2026-11-24',round:'../../../'},{date:'2026-11-24',round:'101'}]){
  r=mock();handler({method:'GET',query:q},r);assert.equal(r.code,400);
 }
 r=mock();handler({method:'POST',query:{}},r);assert.equal(r.code,405);
});
test('resource bounds reject unsuitable inputs',()=>{
 assert.throws(()=>searchTriple(3,3,3,{maxBase:200}),RangeError);
 assert.throws(()=>fltReduction(2,3,4),RangeError);
 assert.throws(()=>prizeCycle('2026-11-24',{maxBase:1000}),RangeError);
});
