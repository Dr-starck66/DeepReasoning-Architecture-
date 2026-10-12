import test from "node:test";
import assert from "node:assert/strict";
import {evaluateRepo,publicRepoInventory,auditFleet,githubJSON,renderFleet} from "./fleet-audit.mjs";
const sha="a".repeat(40),owner={login:"Dr-starck66"};
const repo=(name,priv=false)=>({name,full_name:"Dr-starck66/"+name,owner,private:priv,default_branch:"main",archived:false});
const catalog={schema:"universal-skill-intelligence/report-v1",timestamp:"2026-10-12T19:00:00.000Z",status:"PASS",
 projects:["future","sport-analysis","application-building"].map(id=>({id,status:"PASS",candidates:[
  {name:"Sample",skillUrl:"https://skills.sh/vercel-labs/skills/find-skills",status:"CANDIDATE_REVIEW_REQUIRED",score:50}]}))};
const tree=(paths=["README.md","package.json",".github/workflows/ci.yml","src/check.test.mjs"])=>({sha,tree:paths.map(path=>({path,type:"blob"})),truncated:false});
const fake=async url=>{
 const path=new URL(url).pathname;
 let data;
 if(path==="/users/Dr-starck66/repos")data=[repo("new-future-project"),repo("betgpt-railway"),repo("secret-project",true)];
 else if(path.endsWith("/new-future-project/git/trees/main"))data=tree(["README.md"]);
 else if(path.endsWith("/betgpt-railway/git/trees/main"))data=tree();
 else return {ok:false,status:404};
 return {ok:true,json:async()=>data};
};
test("complete source tree is PASS only within narrowly defined audit scope",()=>{
 const x=evaluateRepo(repo("betgpt-railway"),{category:"sport-analysis",skills:[]},tree());
 assert.equal(x.status,"PASS");
 assert.equal(x.controls.find(c=>c.name==="test-files").status,"PASS");
 assert.equal(x.controls.find(c=>c.name==="ci-workflows").status,"PASS");
 assert.equal(x.controls.find(c=>c.name==="skill-applied-and-proven").status,"UNVERIFIED");
 assert.equal(x.controls.find(c=>c.name==="real-deployment-health").status,"UNVERIFIED");
});
test("empty tree, missing sha, and truncated source cannot fake a full source PASS",()=>{
 assert.equal(evaluateRepo(repo("x"),null,{sha:"fake",tree:[]}).status,"UNVERIFIED");
 assert.equal(evaluateRepo(repo("x"),null,{...tree(),truncated:true}).status,"PARTIAL");
 assert.equal(evaluateRepo(repo("x"),null,tree([])).status,"UNVERIFIED");
});
test("private and foreign repo inputs never enter audit report",()=>{
 assert.throws(()=>evaluateRepo(repo("secret",true),null,tree()));
 assert.throws(()=>evaluateRepo({...repo("a"),owner:{login:"attacker"}},null,tree()));
});
test("GitHub API is allowlisted; no third party destination possible",async()=>{
 await assert.rejects(()=>githubJSON("/repos/evil/secret",{fetcher:fake}));
 await assert.rejects(()=>githubJSON("//evil.example/steal",{fetcher:fake}));
});
test("automatically onboards future public repos, excludes private, and audits each separately",async()=>{
 const r=await auditFleet(catalog,{fetcher:fake,clock:()=>"2026-10-12T19:00:00.000Z"});
 assert.equal(r.summary.publicRepositories,2);
 assert.equal(r.summary.treePass,2);
 assert.equal(r.summary.withTestFiles,1);
 assert.equal(r.summary.withCIConfiguration,1);
 assert.equal(r.summary.approvedSkillInstallations,0);
 assert.equal(r.projects[0].repository,"Dr-starck66/betgpt-railway");
 assert.match(renderFleet(r),/new-future-project/);
 assert.doesNotMatch(renderFleet(r),/secret-project/);
});
test("network failure affects only corresponding project proof, never produces false PASS",async()=>{
 const f=async url=>String(url).includes("/betgpt-railway/git/trees/main?recursive=1")?{ok:false,status:404}:fake(url);
 const r=await auditFleet(catalog,{fetcher:f,clock:()=>"2026-10-12T19:00:00.000Z"});
 assert.equal(r.status,"PARTIAL");
 assert.equal(r.summary.unverified,1);
 assert.match(r.projects.find(p=>p.repository.endsWith("betgpt-railway")).evidenceError,/HTTP_404/);
});
test("transient 503 is retried before recording the final project result",async()=>{
 let attempts=0;
 const f=async url=>{
  if(String(url).includes("/betgpt-railway/git/trees/main?recursive=1")&&attempts++===0)return {ok:false,status:503};
  return fake(url);
 };
 const r=await auditFleet(catalog,{fetcher:f,wait:async()=>{},clock:()=>"2026-10-12T19:00:00.000Z"});
 assert.equal(r.summary.treePass,2);
 assert.equal(attempts,2);
});
test("invalid catalog is rejected before touching GitHub",async()=>{
 await assert.rejects(()=>auditFleet({...catalog,status:"FAIL"},{fetcher:fake}));
});
