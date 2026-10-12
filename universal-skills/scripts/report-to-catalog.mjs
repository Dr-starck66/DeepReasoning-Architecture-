#!/usr/bin/env node
// Publish a public-only evidence catalog. No third-party code execution.
import {readFileSync,writeFileSync,mkdirSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {pathToFileURL} from "node:url";
const tick=String.fromCharCode(96);
const clean=s=>String(s??"").replace(/[\u0000-\u001f\u007f]/g," ").slice(0,180);
const md=s=>clean(s).split("").map(c=>"\\<>|[]()*_!".includes(c)||c===tick?"\\"+c:c).join("");
const safeUrl=u=>/^https:\/\/skills\.sh\/[a-z0-9_.-]+\/[a-z0-9_.-]+\/[a-z0-9_.-]+$/i.test(u||"")?u:null;
export function buildCatalog(report){
  if(!report||report.schema!=="universal-skill-intelligence/report-v1"||!Array.isArray(report.projects))
    throw Error("INVALID_REPORT");
  if(report.status!=="PASS"||report.projects.length<2||report.summary?.failedQueries!==0)
    throw Error("CATALOG_EVIDENCE_NOT_PASS");
  if(report.projects.some(p=>p.queries?.some(q=>q.status!=="PASS")))
    throw Error("CATALOG_FAILED_QUERY");
  if(!Number.isFinite(Date.parse(report.timestamp)))throw Error("INVALID_TIMESTAMP");
  const ids=new Set();
  let rows=0;
  const lines=[
    "# UNIVERSAL SKILL INTELLIGENCE Ω — catalogue public",
    "",
    "Dernier relevé : **"+md(report.timestamp)+"**.",
    "",
    "**Périmètre :** recherches par catégories publiques : développement, médias, export, recherche, patrimoine et projets futurs.",
    "**Preuve :** appels au registre skills.sh. **Aucun skill n'est installé, homologué ou garanti.**",
    "Les vérifications statiques ne remplacent pas l'audit de sécurité et de licence.",
    "",
    "| Domaine | Skill repéré | Installations indicatives | Statut |",
    "| --- | --- | ---: | --- |"
  ];
  for(const project of report.projects){
    if(!/^[a-z0-9-]{1,80}$/.test(project.id)||ids.has(project.id))throw Error("INVALID_PROJECT_ID");
    ids.add(project.id);
    if(/private|secret|password|token/i.test(JSON.stringify(project)))throw Error("POTENTIAL_PRIVATE_DATA");
    for(const item of (Array.isArray(project.candidates)?project.candidates.slice(0,3):[])){
      const url=safeUrl(item.skillUrl);
      if(!url)continue;
      const status=["UNVERIFIED","BLOCKED","CANDIDATE_REVIEW_REQUIRED","REVIEW_REQUIRED"].includes(item.status)?item.status:"UNVERIFIED";
      const n=Number.isSafeInteger(item.installs)&&item.installs>=0?item.installs:0;
      lines.push("| "+md(project.label)+" | ["+md(item.name)+"]("+url+") | "+n.toLocaleString("fr-FR")+" | "+status+" |");
      rows++;
    }
  }
  if(!rows)throw Error("NO_CANDIDATES");
  lines.push("","**"+rows+" candidats affichés**, au plus 3 par domaine. Rapport détaillé : ["+tick+"latest.json"+tick+"](./reports/latest.json).",
   "","## Avant toute adoption", "",
   "Vérifier SKILL.md et dépendances à un commit immuable, les licences, les coûts, la sécurité et l'utilité avec un test isolé.",
   "","Moteur : ["+tick+"universal-skill-intelligence.mjs"+tick+"](./scripts/universal-skill-intelligence.mjs).","");
  return {markdown:lines.join("\n"),rows,projects:report.projects.length};
}
export function main(argv=process.argv.slice(2)){
 const [input="artifacts/public-proof/report.json",jsonPath="reports/latest.json",mdPath="CATALOG.md"]=argv;
 const report=JSON.parse(readFileSync(resolve(input),"utf8"));
 const result=buildCatalog(report);
 for(const [path,data] of [[jsonPath,JSON.stringify(report,null,2)+"\n"],[mdPath,result.markdown]]){
   const target=resolve(path);mkdirSync(dirname(target),{recursive:true});writeFileSync(target,data);
 }
 console.log("UNIVERSAL_SKILLS_CATALOG "+JSON.stringify({status:"PASS",projects:result.projects,rows:result.rows}));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)
 try{main();}catch(e){console.error("UNIVERSAL_SKILLS_CATALOG_FAIL",e.message);process.exitCode=1;}
