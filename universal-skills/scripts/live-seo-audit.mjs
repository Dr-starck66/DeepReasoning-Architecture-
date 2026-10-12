#!/usr/bin/env node
// Read-only application of pinned MIT seo-audit guidance. Not a third-party executable.
// https://github.com/coreyhaines31/marketingskills/blob/1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff/skills/seo-audit/SKILL.md
import {mkdirSync,writeFileSync} from "node:fs";
import {dirname,resolve} from "node:path";
import {pathToFileURL} from "node:url";
const ORIGIN="https://betgpt.live";
const PATHS=["/","/actualites","/robots.txt","/sitemap.xml","/news-sitemap.xml","/sitemap-images.xml"];
const source={repository:"coreyhaines31/marketingskills",commit:"1efedbc5148b54b2f0f6c6c9fe0be62e151c7fff",skill:"seo-audit",license:"MIT",mode:"checklist-only; no external code run"};
const crop=x=>String(x??"").replace(/[\u0000-\u001f]/g," ").slice(0,220);
const locs=s=>[...s.matchAll(/<loc>\s*([^<]+?)\s*<\/loc>/gi)].map(m=>m[1].replace(/&amp;/g,"&").trim());
export function evaluate(responses,{now=Date.now()}={}){
 const checks=[];
 const add=(id,status,detail)=>checks.push({id,status,detail:crop(detail)});
 for(const path of PATHS){
  const p=responses[path];
  if(!p){add("endpoint:"+path,"UNVERIFIED","Missing response");continue;}
  const ok=p.status===200&&typeof p.url==="string"&&p.url.startsWith(ORIGIN);
  const status=p.status===0?"UNVERIFIED":ok?"PASS":"FAIL";
  add("endpoint:"+path,status,"HTTP "+p.status+" URL "+p.url+(p.durationMs?" in "+p.durationMs+"ms":"")+(p.error?"; "+p.error:""));
  if(ok&&!(p.body||"").length)add("body:"+path,"FAIL","Empty body");
 }
 const robots=responses["/robots.txt"];
 if(robots?.status===200){
  const s=robots.body||"";
  add("robots-not-global-block",/^\s*Disallow:\s*\/\s*$/im.test(s)?"FAIL":"PASS","Global disallow");
  add("robots-sitemap",/^\s*Sitemap:\s*https:\/\/betgpt\.live\/sitemap\.xml/im.test(s)?"PASS":"FAIL","Sitemap reference");
 }
 const sitemap=responses["/sitemap.xml"];
 if(sitemap?.status===200){
  const urls=locs(sitemap.body||"");
  add("sitemap-xml",/<(?:urlset|sitemapindex)\b/i.test(sitemap.body||"")?"PASS":"FAIL","XML root");
  add("sitemap-nonempty",urls.length?"PASS":"FAIL",String(urls.length)+" loc URLs");
  const foreign=urls.filter(url=>{try{const u=new URL(url);return u.origin!==ORIGIN||u.protocol!=="https:";}catch{return true;}});
  add("sitemap-same-origin",foreign.length===0?"PASS":"FAIL",
    String(foreign.length)+" foreign/malformed URLs; examples: "+foreign.slice(0,5).join(", "));
  add("sitemap-duplicates",new Set(urls).size===urls.length?"PASS":"FAIL",String(urls.length-new Set(urls).size)+" duplicates");
 }
 const news=responses["/news-sitemap.xml"];
 if(news?.status===200){
  const dates=[...(news.body||"").matchAll(/<news:publication_date>([^<]+)<\/news:publication_date>/gi)].map(m=>Date.parse(m[1]));
  const invalid=dates.filter(x=>!Number.isFinite(x)).length,stale=dates.filter(x=>Number.isFinite(x)&&x<now-48*3600000).length;
  const future=dates.filter(x=>Number.isFinite(x)&&x>now+300000).length;
  add("news-fresh-dates",invalid||stale||future?"FAIL":"PASS",String(dates.length)+" dates, invalid "+invalid+", stale "+stale+", future "+future);
  add("news-size",locs(news.body||"").length<=1000?"PASS":"FAIL",String(locs(news.body||"").length)+" URLs");
 }
 for(const path of ["/","/actualites"]){
  const page=responses[path];if(page?.status!==200)continue;
  const html=page.body||"";
  const canon=[...html.matchAll(/<link\b[^>]*rel=["']canonical["'][^>]*>/gi)]
    .map(m=>(m[0].match(/\bhref=["']([^"']+)["']/i)||[])[1]).filter(Boolean);
  let good=false;
  if(canon.length===1){try{const u=new URL(canon[0],ORIGIN);good=u.origin===ORIGIN&&(path==="/"?u.pathname==="/":u.pathname.replace(/\/$/,"")===path);}catch{good=false;}}
  add("canonical:"+path,good?"PASS":canon.length?"FAIL":"UNVERIFIED",canon.join(",")||"Not in static HTML; confirm rendered DOM");
  const metas=[...html.matchAll(/<meta\b[^>]*name=["'](?:robots|googlebot)["'][^>]*>/gi)].map(m=>m[0]);
  add("noindex:"+path,metas.some(m=>/noindex/i.test(m))?"FAIL":"PASS","Static HTML meta scan");
  const h1=(html.match(/<h1\b/gi)||[]).length;
  add("h1:"+path,h1===1?"PASS":h1===0?"UNVERIFIED":"FAIL",String(h1)+" static H1");
  add("schema:"+path,"UNVERIFIED","Needs DOM rendering or Google Rich Results Test");
 }
 const failed=checks.filter(c=>c.status==="FAIL").length,unverified=checks.filter(c=>c.status==="UNVERIFIED").length;
 return {schema:"universal-skills/seo-pilot-v1",at:new Date(now).toISOString(),origin:ORIGIN,skillSource:source,
 scope:"HTTP-only audit, not Google indexing, Discover entry, site speed or schema proof",
 checks,summary:{pass:checks.length-failed-unverified,fail:failed,unverified},
 status:failed?"FAIL":unverified?"PARTIAL":"PASS"};
}
export async function probe(fetcher=fetch){
 const responses={};
 await Promise.all(PATHS.map(async path=>{
  const timeoutMs=path==="/sitemap-images.xml"?20000:12000;
  for(let attempt=1;attempt<=2;attempt++){
   const started=Date.now();
   try{
    const r=await fetcher(ORIGIN+path,{redirect:"follow",signal:AbortSignal.timeout(timeoutMs),headers:{"user-agent":"UNIVERSAL-SKILL-SEO-PILOT/1"}});
    responses[path]={status:r.status,url:r.url,body:(await r.text()).slice(0,1000000),durationMs:Date.now()-started,attempt};
    break;
   }catch(e){
    responses[path]={status:0,url:ORIGIN+path,body:"",durationMs:Date.now()-started,attempt,error:crop(e.message)};
    if(attempt<2)await new Promise(done=>setTimeout(done,500));
   }
  }
 }));
 const out=evaluate(responses);
 out.fetchErrors=Object.values(responses).filter(r=>r.error).map(r=>({url:r.url,error:r.error}));
 return out;
}
export function markdown(report){
 const lines=["# BetGPT — evidence-based SEO pilot","","At "+report.at+", status: "+report.status,"",
  "Reference: MIT seo-audit guidance, commit "+source.commit+". No third-party execution.","",
  "| Check | Result | Evidence |","| --- | --- | --- |"];
 for(const c of report.checks)lines.push("| "+c.id+" | "+c.status+" | "+c.detail.replaceAll("|"," ")+" |");
 lines.push("","HTTP success does not prove Search Console indexing, News or Discover visibility, Core Web Vitals or rendered schema.");
 return lines.join("\n")+"\n";
}
export async function main(){
 const result=await probe();
 for(const [p,content] of [["artifacts/seo-pilot/report.json",JSON.stringify(result,null,2)+"\n"],["artifacts/seo-pilot/report.md",markdown(result)]]){
  const dest=resolve(p);mkdirSync(dirname(dest),{recursive:true});writeFileSync(dest,content);
 }
 console.log("UNIVERSAL_SEO_PILOT "+JSON.stringify({status:result.status,summary:result.summary}));
 if(result.status==="FAIL")process.exitCode=1;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href)
 main().catch(e=>{console.error("UNIVERSAL_SEO_PILOT_FAIL",crop(e.message));process.exitCode=1;});
