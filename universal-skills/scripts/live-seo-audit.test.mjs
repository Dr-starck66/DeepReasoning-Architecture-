import test from "node:test";
import assert from "node:assert/strict";
import {evaluate,markdown,probe} from "./live-seo-audit.mjs";
const o="https://betgpt.live";
const base=()=>({
 "/":{status:200,url:o+"/",body:'<html><link rel="canonical" href="https://betgpt.live/"><h1>Site</h1></html>'},
 "/actualites":{status:200,url:o+"/actualites",body:'<html><link rel="canonical" href="https://betgpt.live/actualites"><h1>News</h1></html>'},
 "/robots.txt":{status:200,url:o+"/robots.txt",body:"User-agent: *\nAllow: /\nSitemap: https://betgpt.live/sitemap.xml"},
 "/sitemap.xml":{status:200,url:o+"/sitemap.xml",body:"<urlset><loc>https://betgpt.live/</loc></urlset>"},
 "/news-sitemap.xml":{status:200,url:o+"/news-sitemap.xml",body:"<urlset></urlset>"},
 "/sitemap-images.xml":{status:200,url:o+"/sitemap-images.xml",body:"<urlset></urlset>"}
});
test("partial not false PASS because schema needs rendered DOM",()=>{let x=evaluate(base());assert.equal(x.status,"PARTIAL");assert.equal(x.summary.fail,0);assert.match(markdown(x),/does not prove Search Console/);});
test("sitewide Disallow blocks gate",()=>{let b=base();b["/robots.txt"].body="Disallow: /\nSitemap: https://betgpt.live/sitemap.xml";assert.equal(evaluate(b).status,"FAIL");});
test("foreign sitemap and duplicate URLs fail",()=>{let b=base();b["/sitemap.xml"].body="<urlset><loc>https://other.example/</loc><loc>https://other.example/</loc></urlset>";assert.equal(evaluate(b).status,"FAIL");});
test("missing pages cannot PASS",()=>{let b=base();b["/actualites"].status=404;assert.equal(evaluate(b).status,"FAIL");});
test("missing static canonical is UNVERIFIED not fake failure",()=>{let b=base();b["/"].body="<html></html>";assert.equal(evaluate(b).checks.find(x=>x.id==="canonical:/").status,"UNVERIFIED");});

test("root canonical without trailing slash is accepted",()=>{let b=base();b["/"].body='<link rel="canonical" href="https://betgpt.live"><h1>Site</h1>';const x=evaluate(b);assert.equal(x.checks.find(c=>c.id==="canonical:/").status,"PASS");});
test("sitemap URLs at the exact root origin are not falsely rejected",()=>{let b=base();b["/sitemap.xml"].body="<urlset><loc>https://betgpt.live</loc></urlset>";const x=evaluate(b);assert.equal(x.checks.find(c=>c.id==="sitemap-same-origin").status,"PASS");});
test("real foreign sitemap URLs include bounded evidence",()=>{let b=base();b["/sitemap.xml"].body="<urlset><loc>https://other.example/path</loc></urlset>";const x=evaluate(b);assert.match(x.checks.find(c=>c.id==="sitemap-same-origin").detail,/other.example/);});

test("timeout is UNVERIFIED rather than claiming an HTTP failure",()=>{let b=base();b["/sitemap-images.xml"]={status:0,url:o+"/sitemap-images.xml",body:"",error:"Timeout",durationMs:12000};const x=evaluate(b);assert.equal(x.status,"PARTIAL");assert.equal(x.checks.find(c=>c.id==="endpoint:/sitemap-images.xml").status,"UNVERIFIED");});
test("real HTTP 404 is still FAIL",()=>{let b=base();b["/sitemap-images.xml"].status=404;const x=evaluate(b);assert.equal(x.status,"FAIL");});
test("retried temporary transport error recovers from first failure",async()=>{
 const b=base(),counts={};
 const response=await probe(async url=>{
  const path=new URL(url).pathname;
  counts[path]=(counts[path]||0)+1;
  if(path==="/sitemap-images.xml"&&counts[path]===1)throw new Error("temporary timeout");
  return {status:b[path].status,url:b[path].url,text:async()=>b[path].body};
 });
 assert.equal(response.status,"PARTIAL");
 assert.equal(counts["/sitemap-images.xml"],2);
 assert.equal(response.checks.find(c=>c.id==="endpoint:/sitemap-images.xml").status,"PASS");
});
