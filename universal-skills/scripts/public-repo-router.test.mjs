import test from "node:test";
import assert from "node:assert/strict";
import {routePublicRepos,categoryOf,renderRepos} from "./public-repo-router.mjs";
const report={schema:"universal-skill-intelligence/report-v1",status:"PASS",timestamp:"2026-10-12T19:00:00Z",
 projects:["future","scientific-research","sport-analysis"].map(id=>({id,candidates:[{name:"Example",status:"UNVERIFIED",score:20,skillUrl:"https://skills.sh/vercel-labs/skills/find-skills"}]}))};
const obj=(name,priv=false)=>({name,full_name:"Dr-starck66/"+name,private:priv,owner:{login:"Dr-starck66"},archived:false});
test("maps existing public BetGPT and BIO-MIMIC repositories",()=>{
 assert.equal(categoryOf(obj("betgpt-railway")),"sport-analysis");
 assert.equal(categoryOf(obj("bio-mimic-x-discovery-factory")),"scientific-research");
});
test("never includes private, foreign or malformed repository",()=>{
 const repos=[obj("betgpt-railway"),obj("secret-internal",true),{...obj("other"),owner:{login:"other"}},obj("../traversal")];
 const out=routePublicRepos(repos,report);
 assert.equal(out.summary.publicRepositories,1);
 assert.equal(out.repositories[0].repository,"Dr-starck66/betgpt-railway");
});
test("uses safety statuses and only allowlisted links",()=>{
 const p=structuredClone(report);p.projects[2].candidates=[
 {name:"Unsafe",status:"BLOCKED",skillUrl:"https://skills.sh/vercel-labs/skills/unsafe"},
 {name:"Bad link",status:"UNVERIFIED",skillUrl:"javascript:alert(1)"},
 {name:"Good",status:"CANDIDATE_REVIEW_REQUIRED",score:90,skillUrl:"https://skills.sh/vercel-labs/skills/find-skills"}];
 const out=routePublicRepos([obj("betgpt-railway")],p);
 assert.equal(out.repositories[0].skills.length,1);
 assert.match(renderRepos(out),/Good/);
});
test("no fake PASS for missing category candidates",()=>{
 const p=structuredClone(report);p.projects[0].candidates=[];
 const out=routePublicRepos([obj("misc")],p);
 assert.equal(out.status,"PARTIAL");
 assert.equal(out.summary.withoutCandidates,1);
});
test("reject unavailable evidence",()=>{
 assert.throws(()=>routePublicRepos([],null));
 assert.throws(()=>routePublicRepos([],report));
});
