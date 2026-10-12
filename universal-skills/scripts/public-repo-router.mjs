#!/usr/bin/env node
// Public GitHub repository inventory -> verified generic skills catalog. NO private repository access.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {resolve,dirname} from "node:path";
import {pathToFileURL} from "node:url";
const safe=/^[a-z0-9][a-z0-9._-]{0,99}$/i;
const fixedCategories=new Set(["sport-analysis","domain-archives","scientific-research","quant-analysis","seo-editorial",
"lead-generation","security-intel","media-production","historical-research","application-building","engineering","future"]);
const rules=[
  ["sport-analysis",/\bbetgpt\b|nfl-|football|sports?[-_]/],
  ["domain-archives",/wayback|domain|freehotel|ndd-|archive|recovery|zip-github/],
  ["quant-analysis",/quant|trading|nasdaq|metatrader/],
  ["scientific-research",/bio-mimic|clinical|biomimic|discovery-factory/],
  ["historical-research",/arkseeker|archaeolog|history|time-travel/],
  ["lead-generation",/affil|opportunityforge|affiliate|marketing/],
  ["security-intel",/pentest|redteam|security|cyber|offensive/],
  ["media-production",/video|photo|media|art/],
  ["seo-editorial",/site-|wyylde|bizarre|seo|news|pantomime|regen/],
  ["application-building",/builder|platform|interface|library|agent|deepreasoning|app/]
];
export function categoryOf(repo){
 const hint=(String(repo.name||"")+" "+String(repo.description||"")).toLowerCase();
 const hit=rules.find(([,re])=>re.test(hint));
 return hit?.[0]||"future";
}
export function routePublicRepos(repos,report,{owner="Dr-starck66"}={}){
 if(!Array.isArray(repos)||report?.schema!=="universal-skill-intelligence/report-v1"||report.status!=="PASS")throw Error("INVALID_INPUT");
 const catalog=new Map(report.projects.map(p=>[p.id,p]));
 const result=[],seen=new Set();
 for(const repo of repos){
  if(repo?.private!==false||repo?.owner?.login?.toLowerCase()!==owner.toLowerCase()||typeof repo.name!=="string"||!safe.test(repo.name))continue;
  if(!repo.full_name||repo.full_name.toLowerCase()!==(owner+"/"+repo.name).toLowerCase())continue;
  if(seen.has(repo.full_name.toLowerCase()))continue;
  seen.add(repo.full_name.toLowerCase());
  const category=categoryOf(repo);
  if(!fixedCategories.has(category)||!catalog.has(category))throw Error("UNMAPPED_CATEGORY");
  const candidates=(catalog.get(category)?.candidates||[]).filter(x=>x.status!=="BLOCKED")
    .filter(x=>/^https:\/\/skills\.sh\/[a-z0-9_.-]+\/[a-z0-9_.-]+\/[a-z0-9_.-]+$/i.test(x.skillUrl||"")).slice(0,3)
    .map(x=>({name:String(x.name).slice(0,120),url:x.skillUrl,status:x.status,score:x.score}));
  result.push({repository:owner+"/"+repo.name,category,archived:repo.archived===true,skills:candidates,
    recommendationStatus:candidates.length?"REVIEW_REQUIRED":"UNVERIFIED"});
 }
 result.sort((a,b)=>a.repository.localeCompare(b.repository));
 if(!result.length)throw Error("NO_PUBLIC_REPOS_VERIFIED");
 return {schema:"universal-skill-intelligence/public-repos-v1",timestamp:report.timestamp,owner,
   privacy:"Only already public GitHub repositories. No private repo access or repository secrets.",
   status:result.every(r=>r.skills.length)?"PASS":"PARTIAL",repositories:result,
   summary:{publicRepositories:result.length,recommendations:result.reduce((n,r)=>n+r.skills.length,0),
     withoutCandidates:result.filter(r=>!r.skills.length).length}};
}
export function renderRepos(data){
 const esc=s=>String(s).replace(/[\[\]|\\<>]/g,"").slice(0,100);
 const lines=["# UNIVERSAL SKILLS Ω — dépôts GitHub publics","",
  "Inventaire public : "+data.summary.publicRepositories+" dépôts vérifiés dans l'espace de noms GitHub "+data.owner+".",
  "**Attention : aucune recommandation ne constitue une installation ou une preuve de sécurité.**","",
  "| Dépôt | Domaine | Premier candidat à auditer | État |",
  "| --- | --- | --- | --- |"];
 for(const r of data.repositories){
  const first=r.skills[0];
  lines.push("| ["+esc(r.repository)+"](https://github.com/"+r.repository+") | "+r.category+" | "+
   (first?"["+esc(first.name)+"]("+first.url+")":"Aucun — à rechercher")+" | "+r.recommendationStatus+" |");
 }
 lines.push("","Données complètes : [public-repos.json](./reports/public-repos.json).","",
 "Les dépôts privés ne sont pas interrogés depuis ce service public. Leur correspondance doit rester dans le registre privé.","");
 return lines.join("\n");
}
export async function main(argv=process.argv.slice(2),fetcher=fetch){
 const [reportPath="reports/latest.json",jsonPath="reports/public-repos.json",mdPath="PUBLIC-REPOS.md"]=argv;
 const report=JSON.parse(readFileSync(resolve(reportPath),"utf8"));
 if(report.status!=="PASS")throw Error("DISCOVERY_REPORT_NOT_PASS");
 const owner="Dr-starck66";
 const headers={Accept:"application/vnd.github+json","User-Agent":"universal-skills-public-router/1"};
 if(process.env.GITHUB_TOKEN)headers.Authorization="Bearer "+process.env.GITHUB_TOKEN;
 const resp=await fetcher("https://api.github.com/users/"+owner+"/repos?per_page=100&type=owner",{headers,signal:AbortSignal.timeout(15000)});
 if(!resp.ok)throw Error("PUBLIC_GITHUB_HTTP_"+resp.status);
 const rows=await resp.json(),data=routePublicRepos(rows,report,{owner});
 for(const [dest,content] of [[jsonPath,JSON.stringify(data,null,2)+"\n"],[mdPath,renderRepos(data)]]){
  const target=resolve(dest);mkdirSync(dirname(target),{recursive:true});writeFileSync(target,content);
 }
 console.log("UNIVERSAL_SKILLS_PUBLIC_REPOS "+JSON.stringify({status:data.status,summary:data.summary}));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)
  main().catch(e=>{console.error("UNIVERSAL_SKILLS_PUBLIC_REPOS_FAIL",e.message);process.exitCode=1;});
