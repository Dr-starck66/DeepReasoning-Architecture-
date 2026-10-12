import test from "node:test";
import assert from "node:assert/strict";
import {buildCatalog} from "./report-to-catalog.mjs";
const report=()=>({schema:"universal-skill-intelligence/report-v1",status:"PASS",timestamp:"2026-10-12T19:05:00.000Z",
 summary:{failedQueries:0},projects:[{id:"wine-export",label:"International trade",queries:[{q:"trade",status:"PASS"}],candidates:[{name:"Sample skill",skillUrl:"https://skills.sh/vercel-labs/skills/find-skills",status:"UNVERIFIED",installs:1000}]},{id:"future",label:"All future projects",queries:[{q:"research",status:"PASS"}],candidates:[]}]});
test("formats only factual public candidates",()=>{const r=buildCatalog(report());assert.equal(r.rows,1);assert.equal(r.projects,2);assert.match(r.markdown,/Aucun skill n'est installé/);assert.match(r.markdown,/find-skills/);});
test("reject failed or incomplete evidence",()=>{for(const status of ["FAIL","UNVERIFIED"]){const r=report();r.status=status;assert.throws(()=>buildCatalog(r));}const r=report();r.projects[0].queries[0].status="FAIL";assert.throws(()=>buildCatalog(r));});
test("reject injection in URLs and markdown cells",()=>{const r=report();r.projects[0].candidates[0].skillUrl="javascript:alert(1)";r.projects[0].candidates[0].name="<script>bad</script>";assert.throws(()=>buildCatalog(r),/NO_CANDIDATES/);});
test("protect against credential data leakage",()=>{const r=report();r.projects[0].label="token=github_pat_XXX";assert.throws(()=>buildCatalog(r),/POTENTIAL_PRIVATE_DATA/);});
test("reject duplicate categories and invalid schemas",()=>{let r=report();r.projects[1].id="wine-export";assert.throws(()=>buildCatalog(r));r=report();r.schema="bogus";assert.throws(()=>buildCatalog(r));});
