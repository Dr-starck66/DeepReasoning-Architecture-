import {discoverCycle} from '../src/conjecture-engine.mjs';
import {validDay} from '../src/engine.mjs';
/** Read-only public research proposal endpoint. Does NOT write to persistent DB. */
export default function handler(req,res){
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'METHOD_NOT_ALLOWED'});}
 const date=typeof req.query?.date==='string'?req.query.date:new Date().toISOString().slice(0,10);
 const raw=req.query?.round??'0';
 if(!validDay(date)||!/^\d{1,3}$/.test(String(raw))||Number(raw)>100)return res.status(400).json({error:'INVALID_DATE_OR_ROUND'});
 try{const report=discoverCycle(date,{round:Number(raw)});res.setHeader('Cache-Control','no-store');return res.status(200).json({api:'ASTRA MATH LAB Ω / discovery',...report});}
 catch(e){console.error('ASTRA_DISCOVER_FAIL',String(e?.message||e));return res.status(500).json({error:'DISCOVERY_FAILED'});}
}
