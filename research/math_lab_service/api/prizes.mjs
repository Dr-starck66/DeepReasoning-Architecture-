import {prizeCycle} from '../src/prize-engine.mjs';
import {validDay} from '../src/engine.mjs';
/** Public read-only exact research; does not write to the DB or run arbitrary code. */
export default function handler(req,res){
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'METHOD_NOT_ALLOWED'});}
 const day=typeof req.query?.date==='string'?req.query.date:new Date().toISOString().slice(0,10);
 const raw=req.query?.round??'0';
 if(!validDay(day)||!/^(0|[1-9]\d{0,2})$/.test(String(raw))||Number(raw)>100)return res.status(400).json({error:'INVALID_DATE_OR_ROUND'});
 try {const result=prizeCycle(day,{round:Number(raw)});res.setHeader('Cache-Control','no-store');
 return res.status(200).json({api:'ASTRA MATH LAB / prize-directed research',...result});
 }catch(e){console.error('ASTRA_BEAL_RESEARCH_FAIL',String(e?.message||e));return res.status(500).json({error:'RESEARCH_FAILED'});}
}
