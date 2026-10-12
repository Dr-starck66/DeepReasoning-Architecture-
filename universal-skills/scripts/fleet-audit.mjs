#!/usr/bin/env node
/**
 * UNIVERSAL SKILLS Omega — evidence-first fleet audits for every accessible public repo.
 * Read only. Does not execute remote code, write other repos, install skills, or expose secrets.
 * Private project mapping stays in private Dr-starck66/indexation.
 */
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {pathToFileURL} from "node:url";
import {routePublicRepos} from "./public-repo-router.mjs";

const OWNER="Dr-starck66",API="https://api.github.com",SHA=/^[0-9a-f]{40}$/i;
const safeName=/^[a-zA-Z0-9_.-]{1,100}$/;
const headers=()=>({"Accept":"application/vnd.github+json","User-Agent":"universal-skills-fleet/1",
 ...(process.env.GITHUB_TOKEN?{Authorization:"Bearer "+process.env.GITHUB_TOKEN}:{})});
const short=x=>String(x??"").replace(/[\u0000-\u001f\u007f<>]/g," ").slice(0,140);
export async function githubJSON(path,{fetcher=fetch,wait=ms=>new Promise(r=>setTimeout(r,ms)),timeoutMs=11000}={}){
 if(!/^\/(?:users\/Dr-starck66\/repos|repos\/Dr-starck66\/[a-zA-Z0-9_.-]+\/git\/trees\/[a-zA-Z0-9_.%/-]+)(?:\?[a-zA-Z0-9=&_-]+)?$/i.test(path))
   throw Error("NON_ALLOWLISTED_GITHUB_PATH");
 const url=API+path;
 for(let i=0;i<3;i++){
  const abort=new AbortController(),timer=setTimeout(()=>abort.abort(),timeoutMs);
  try{
   const resp=await fetcher(url,{headers:headers(),signal:abort.signal});
   if(resp.ok)return await resp.json();
   const err=Error("HTTP_"+resp.status);err.status=resp.status;throw err;
  }catch(err){
   if(i>=2||!(err.status===429||err.status===502||err.status===503||err.status===504||err.status===500||err.name==="AbortError"||err.name==="TypeError"))throw err;
  }finally{clearTimeout(timer);}
  await wait(400*2**i);
 }
 throw Error("REQUEST_RETRY_EXHAUSTED");
}
export async function publicRepoInventory(opts={}){
 const repos=[],seen=new Set();
 for(let page=1;page<=10;page++){
  const data=await githubJSON("/users/"+OWNER+"/repos?per_page=100&type=owner&page="+page,opts);
  if(!Array.isArray(data))throw Error("BAD_REPOSITORY_LIST");
  for(const r of data){
   if(r?.private!==false||r?.owner?.login?.toLowerCase()!==OWNER.toLowerCase()||
     !safeName.test(r?.name||"")||r.full_name?.toLowerCase()!==(OWNER+"/"+r.name).toLowerCase())continue;
   if(seen.has(r.full_name.toLowerCase()))continue;
   seen.add(r.full_name.toLowerCase());repos.push(r);
  }
  if(data.length<100)break;
  if(page===10)throw Error("INCOMPLETE_REPOSITORY_PAGINATION");
 }
 return repos;
}
export function evaluateRepo(repo,matched,tree,{timestamp=new Date().toISOString()}={}){
 if(repo?.private!==false||repo?.owner?.login?.toLowerCase()!==OWNER.toLowerCase()||
   !safeName.test(repo?.name||"")||repo.full_name?.toLowerCase()!==(OWNER+"/"+repo.name).toLowerCase())
   throw Error("REPO_IDENTITY_NOT_PROVEN");
 const result={repository:OWNER+"/"+repo.name,category:matched?.category||"future",
   checkedAt:timestamp,publicUrl:"https://github.com/"+OWNER+"/"+repo.name,
   categorySelection:"HEURISTIC_REVIEW_REQUIRED",
   skillCandidates:(matched?.skills||[]).slice(0,2).map(s=>({name:short(s.name),url:s.url,
    verification:s.status==="BLOCKED"?"BLOCKED":"REVIEW_REQUIRED"})),
   controls:[],status:"UNVERIFIED"};
 const check=(name,status,evidence)=>result.controls.push({name,status,evidence:short(evidence)});
 check("public-repo-identity","PASS","Authenticated listing matched public "+result.repository);
 if(repo.archived===true){
  check("active-maintenance","N/A","Repository is archived");
 }else{
  check("active-maintenance","UNVERIFIED","No deployment or activity verification performed");
 }
 if(!tree||!SHA.test(tree.sha||"")||!Array.isArray(tree.tree)){
  check("source-tree","UNVERIFIED","GitHub tree unavailable or invalid");
  result.nextAction="Retrieve source tree and prove artifacts";
  return result;
 }
 const entries=tree.tree.filter(x=>x&&typeof x.path==="string"&&x.type==="blob").map(x=>x.path);
 const tests=entries.filter(x=>/(?:^|\/)(?:tests?\/|__tests__\/)|\.(?:test|spec)\.[cm]?[jt]sx?$|test_[^/]+\.py$/.test(x));
 const workflows=entries.filter(x=>/^\.github\/workflows\/[^/]+\.(?:yml|yaml)$/i.test(x));
 const manifests=entries.filter(x=>/(?:^|\/)(?:package\.json|pyproject\.toml|requirements\.txt|go\.mod|Cargo\.toml|pom\.xml|Dockerfile|index\.html)$/i.test(x)).slice(0,12);
 check("source-tree",tree.truncated?"PARTIAL":"PASS",
   "Git tree SHA "+tree.sha.slice(0,12)+", "+entries.length+" visible files"+(tree.truncated?", truncated":""));
 check("project-files",entries.length?"PASS":"UNVERIFIED",entries.length+" visible Git files");
 check("test-files",tests.length?"PASS":"UNVERIFIED",tests.length+" declarations present; execution NOT checked");
 check("ci-workflows",workflows.length?"PASS":"UNVERIFIED",workflows.length+" workflow files present; execution NOT checked");
 check("build-manifest",manifests.length?"PASS":"UNVERIFIED",manifests.length?manifests.slice(0,4).join(", "):"No recognized build manifest");
 check("real-deployment-health","UNVERIFIED","Public Git tree is not a deployed site or functional test");
 check("skill-applied-and-proven","UNVERIFIED","Candidate suggestions are not installed or evaluated");
 result.status=tree.truncated?"PARTIAL":entries.length?"PASS":"UNVERIFIED";
 result.nextAction=result.category==="seo-editorial"
  ?"Identify official site URL, then run HTTP/SEO/indexability proof; no unverified domain assumptions"
  :tests.length?"Run declared tests in an isolated project CI, then test benefit of approved skill"
  :"Identify project-specific acceptance tests before trying a skill";
 return result;
}
export async function auditFleet(catalog,{fetcher=fetch,wait,timeoutMs=11000,clock=()=>new Date().toISOString()}={}){
 if(catalog?.schema!=="universal-skill-intelligence/report-v1"||catalog.status!=="PASS")throw Error("NO_VALID_SKILL_CATALOG");
 const repos=await publicRepoInventory({fetcher,wait,timeoutMs});
 const routed=routePublicRepos(repos,catalog,{owner:OWNER});
 const map=new Map(routed.repositories.map(x=>[x.repository.toLowerCase(),x]));
 const projects=new Array(repos.length);
 let next=0;
 const worker=async()=>{
  while(next<repos.length){
   const idx=next++,repo=repos[idx],mapped=map.get(repo.full_name.toLowerCase());
   let tree=null,error=null;
   if(repo.default_branch&&repo.default_branch.length<=100){
    try{
     tree=await githubJSON("/repos/"+OWNER+"/"+repo.name+"/git/trees/"+encodeURIComponent(repo.default_branch)+"?recursive=1",{fetcher,wait,timeoutMs});
    }catch(err){error=short(err.message);}
   }else error="Default branch missing";
   const result=evaluateRepo(repo,mapped,tree,{timestamp:clock()});
   if(error)result.evidenceError=error;
   projects[idx]=result;
  }
 };
 await Promise.all(Array.from({length:Math.min(4,repos.length)},worker));
 projects.sort((a,b)=>a.repository.localeCompare(b.repository));
 const summary={publicRepositories:projects.length,treePass:projects.filter(x=>x.status==="PASS").length,
  partial:projects.filter(x=>x.status==="PARTIAL").length,
  unverified:projects.filter(x=>x.status==="UNVERIFIED").length,
  withTestFiles:projects.filter(x=>x.controls.find(c=>c.name==="test-files")?.status==="PASS").length,
  withCIConfiguration:projects.filter(x=>x.controls.find(c=>c.name==="ci-workflows")?.status==="PASS").length,
  approvedSkillInstallations:0};
 return {schema:"universal-skills/fleet-v1",timestamp:clock(),sourceCatalogDate:catalog.timestamp,
  status:summary.treePass===projects.length?"PASS":"PARTIAL",
  statusScope:"PASS means public source-tree inventory fetched; NEVER site health, skills adoption or success",
  privacy:"Only existing public GitHub repositories. No private data queried or printed.",
  summary,projects};
}
export function renderFleet(report){
 const safe=s=>short(s).replace(/[\[\]|\\]/g,"");
 const lines=["# UNIVERSAL SKILLS Ω — audit automatique du portefeuille GitHub public","",
  "**Dernier contrôle :** "+report.timestamp+"  |  **Inventaire source :** "+report.status,
  "",
  "Cet audit parcourt réellement les sources de chaque dépôt public. Il ne prouve ni l'installation de skills, ni le bon fonctionnement de l'application, ni l'indexation Google.",
  "**Succès d'inventaire ≠ succès opérationnel.** Les preuves de tests et de santé restent UNVERIFIED tant qu'elles ne sont pas exécutées.",
  "",
  "Dépôts : "+report.summary.publicRepositories+" — arbres sources confirmés : "+report.summary.treePass+
   " — projets avec fichiers de tests : "+report.summary.withTestFiles+
   " — projets avec workflows CI : "+report.summary.withCIConfiguration+".",
  "",
  "| Projet | Domaine | Arbre source | Tests déclarés | CI déclarée | Première action |",
  "| --- | --- | --- | --- | --- | --- |"];
 for(const p of report.projects){
  const c=name=>p.controls.find(x=>x.name===name)?.status||"UNVERIFIED";
  lines.push("| ["+safe(p.repository)+"]("+p.publicUrl+") | "+safe(p.category)+" | "+c("source-tree")+
   " | "+c("test-files")+" | "+c("ci-workflows")+" | "+safe(p.nextAction)+" |");
 }
 lines.push("","Rapport par projet : [reports/fleet.json](./reports/fleet.json).",
  "Les projets privés et initiatives sans dépôt ne figurent pas dans cette page publique; registre séparé et confidentiel.",
  "Chaque nouveau dépôt public de Dr-starck66 est détecté au prochain cycle sans inscription manuelle.","");
 return lines.join("\n");
}
export async function main(argv=process.argv.slice(2)){
 const [input="reports/latest.json",reportPath="reports/fleet.json",markdownPath="FLEET.md"]=argv;
 const catalog=JSON.parse(readFileSync(resolve(input),"utf8"));
 const audit=await auditFleet(catalog);
 for(const [p,s] of [[reportPath,JSON.stringify(audit,null,2)+"\n"],[markdownPath,renderFleet(audit)]]){
  const target=resolve(p);mkdirSync(dirname(target),{recursive:true});writeFileSync(target,s);
 }
 console.log("UNIVERSAL_SKILLS_FLEET "+JSON.stringify({status:audit.status,summary:audit.summary}));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)
 main().catch(e=>{console.error("UNIVERSAL_SKILLS_FLEET_FAIL",short(e.message));process.exitCode=1;});
