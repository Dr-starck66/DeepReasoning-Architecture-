import test from 'node:test';import assert from 'node:assert/strict';
import handler from '../api/discover.mjs';
const mock=()=>({code:0,body:null,headers:{},setHeader(k,v){this.headers[k]=v;},status(v){this.code=v;return this;},json(v){this.body=v;return this;}});
test('public discovery route runs and distinguishes rounds',()=>{
 let a=mock(),b=mock();handler({method:'GET',query:{date:'2026-11-23',round:'0'}},a);
 handler({method:'GET',query:{date:'2026-11-23',round:'1'}},b);
 assert.equal(a.code,200);assert.equal(b.code,200);assert.equal(a.body.candidates.length,3);
 assert.notDeepEqual(a.body.candidate_ids,b.body.candidate_ids);
});
test('discovery endpoint rejects hostile inputs and methods',()=>{
 for(const q of [{date:'2026-02-30',round:0},{date:'2026-11-23',round:101},{date:'2026-11-23',round:'../../'}]){
   const r=mock();handler({method:'GET',query:q},r);assert.equal(r.code,400);
 }const r=mock();handler({method:'POST',query:{}},r);assert.equal(r.code,405);
});
