import test from "node:test";
import assert from "node:assert/strict";
import {evaluate,markdown} from "./live-seo-audit.mjs";
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
