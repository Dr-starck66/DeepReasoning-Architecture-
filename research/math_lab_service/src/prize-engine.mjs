/** ASTRA MATH LAB Ω — Beal prize-directed finite research / case reductions.
 * No prize claim: exhaustive search is bounded; general no-go uses known FLT.
 * All finite equality checks use exact BigInt, never floating point.
 */
import { createHash } from 'node:crypto';
const hash = x => createHash('sha256').update(JSON.stringify(x)).digest('hex');
export function gcd(a,b){while(b)[a,b]=[b,a%b];return Math.abs(a);}
export function validTriple(x,y,z) {return [x,y,z].every(v=>Number.isInteger(v)&&v>=3&&v<=100);}

export function fltReduction(x,y,z){
 if(!validTriple(x,y,z))throw new RangeError('Exponents must be integers 3..100');
 const d=gcd(gcd(x,y),z);
 if(d<3)return {exponents:[x,y,z],common_exponent_divisor:d,status:'NOT_CLOSED_BY_THIS_REDUCTION',prize_solution:false};
 return {exponents:[x,y,z],common_exponent_divisor:d,
  substitution:[`X=A^${x/d}`,`Y=B^${y/d}`,`Z=C^${z/d}`],
  reduced_equation:`X^${d}+Y^${d}=Z^${d}`,
  external_theorem:'Fermat Last Theorem (positive integer exponent d>2)',
  proof_kind:'VALID_REDUCTION_USING_EXTERNAL_ESTABLISHED_THEOREM',
  status:'CLASSICAL_CASE_CLOSED',academic_novelty:'KNOWN_RESULT',prize_solution:false};
}

export function verifyPowerEquality(w){
 const {A,B,C,x,y,z}=w??{};
 if(![A,B,C,x,y,z].every(v=>Number.isSafeInteger(v))||![A,B,C].every(v=>v>0)||!validTriple(x,y,z))return false;
 return BigInt(A)**BigInt(x)+BigInt(B)**BigInt(y)===BigInt(C)**BigInt(z);
}
export function verifyPrimitiveCounterexample(w){return verifyPowerEquality(w)&&gcd(gcd(w.A,w.B),w.C)===1;}

/** Exact bounded search for one exponent triple, all 1..maxBase. */
export function searchTriple(x,y,z,{maxBase=40}={}){
 if(!validTriple(x,y,z)||!Number.isInteger(maxBase)||maxBase<2||maxBase>150)throw new RangeError('Invalid exact scan bounds');
 const d=gcd(gcd(x,y),z); const powersC=new Map();
 for(let c=1;c<=maxBase;c++){const value=(BigInt(c)**BigInt(z)).toString();
   const a=powersC.get(value)??[];a.push(c);powersC.set(value,a);}
 const pwA=Array.from({length:maxBase},(_,i)=>BigInt(i+1)**BigInt(x));
 const pwB=Array.from({length:maxBase},(_,i)=>BigInt(i+1)**BigInt(y));
 let equalities=0, primitiveHits=0, nonprimitiveHits=0, modularRejected=0;
 const examples=[];const primitiveWitnesses=[];
 for(let a=1;a<=maxBase;a++)for(let b=1;b<=maxBase;b++){
  const sum=pwA[a-1]+pwB[b-1]; const cs=powersC.get(sum.toString());
  if(!cs){modularRejected++;continue;}
  for(const c of cs){const w={A:a,B:b,C:c,x,y,z};
    if(!verifyPowerEquality(w))throw Error('Exact arithmetic mismatch');
    equalities++;
    if(verifyPrimitiveCounterexample(w)){primitiveHits++;primitiveWitnesses.push(w);}
    else{nonprimitiveHits++;if(examples.length<3)examples.push(w);}
  }
 }
 const result={x,y,z,common_exponent_divisor:d,bounds:{base_min:1,base_max:maxBase},
  exact_A_B_pairs_checked:maxBase*maxBase,exact_equalities:equalities,
  primitive_counterexamples:primitiveHits,nonprimitive_equalities:nonprimitiveHits,
  nonprimitive_examples:examples,primitive_witnesses:primitiveWitnesses,
  scope:'FINITE_BASES_ONLY',general_case:'UNVERIFIED',prize_solution:false};
 if(d>=3){result.classical_reduction=fltReduction(x,y,z);}
 return result;
}

/** Separate exhaustive oracle, intentionally tiny, for negative controls. */
export function independentOracle(x,y,z,maxBase){
 let found=0, primitive=0;
 for(let A=1;A<=maxBase;A++)for(let B=1;B<=maxBase;B++)for(let C=1;C<=maxBase;C++){
  if(BigInt(A)**BigInt(x)+BigInt(B)**BigInt(y)===BigInt(C)**BigInt(z)){
   found++;if(gcd(gcd(A,B),C)===1)primitive++;
  }
 }
 return {equalities:found,primitive};
}

/** Select previously-unexplored exponent triples; avoid deterministic repeats.
 * Each daily run searches 6 frontier triples with exact integer arithmetic.
 */
export function prizeCycle(day,{seenIds=[],round=0,maxBase=40}={}){
 if(!/^20\d\d-\d\d-\d\d$/.test(day)||new Date(day+'T00:00:00Z').toISOString().slice(0,10)!==day)throw new RangeError('Bad day');
 if(!Number.isInteger(round)||round<0||round>100)throw new RangeError('Bad round');
 if(!Number.isInteger(maxBase)||maxBase<2||maxBase>150)throw new RangeError('Bad bound');
 const seen=new Set(seenIds),all=[];
 for(let x=3;x<=8;x++)for(let y=3;y<=8;y++)for(let z=3;z<=8;z++){
  const id=hash(['beal-exponent-triple',x,y,z,maxBase]);
  const d=gcd(gcd(x,y),z);
  all.push({id,x,y,z,d});
 }
 const closed=all.filter(t=>t.d>=3),frontier=all.filter(t=>t.d<3);
 const unseen=frontier.filter(t=>!seen.has(t.id));
 const seed=(Date.parse(day+'T00:00:00Z')/86400000+round*31)%Math.max(unseen.length,1);
 const rotated=unseen.slice(seed).concat(unseen.slice(0,seed));
 const selection=rotated.slice(0,6);
 const cases=selection.map(t=>({id:t.id,...searchTriple(t.x,t.y,t.z,{maxBase})}));
 const controls={known_solution:{A:3,B:6,C:3,x:3,y:3,z:5},
   known_solution_valid:verifyPowerEquality({A:3,B:6,C:3,x:3,y:3,z:5}),
   known_solution_nonprimitive:!verifyPrimitiveCounterexample({A:3,B:6,C:3,x:3,y:3,z:5}),
   known_false_primitive_rejected:!verifyPrimitiveCounterexample({A:1,B:1,C:1,x:3,y:3,z:3})};
 if(!Object.values(controls).slice(1).every(Boolean))throw Error('Positive/negative controls failed');
 return {version:'0.6.0',award_problem:'Beal conjecture',award_usd:1000000,
  rules_url:'https://www.bealbank.com/who-we-are/our-founder/the-beal-conjecture/',
  day,round,finite_base_max:maxBase,exponent_triples_total:all.length,
  exponent_triples_classically_closed:closed.length,
  exponent_triples_not_closed_by_flt:frontier.length,
  exact_triples_checked:cases.length,candidates:cases,candidate_ids:cases.map(c=>c.id),
  controls,conclusions:{primitive_witnesses_found:cases.reduce((n,c)=>n+c.primitive_counterexamples,0),
   finite_equalities_found:cases.reduce((n,c)=>n+c.exact_equalities,0)},
  originality:'UNVERIFIED',global_Beal_solution:'UNVERIFIED',prize_eligible:false,
  hypothesis_scope:'EXACT_BOUNDED_SEARCH_AND_KNOWN_FERMAT_REDUCTION_ONLY',
  next_research_obligation:'Develop rigorously justified constraints for gcd(exponents)<=2 beyond finite enumeration; independently formalize any proposed lemma in Lean/Mathlib.'};
}
