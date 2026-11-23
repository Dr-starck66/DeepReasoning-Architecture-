import {runResearch,validDay} from '../src/engine.mjs';
export default function handler(req,res){
 if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'METHOD_NOT_ALLOWED'});}
 const day=typeof req.query?.date==='string'?req.query.date:new Date().toISOString().slice(0,10);
 if(!validDay(day))return res.status(400).json({error:'INVALID_DATE'});
 try{const result=runResearch(day);console.log(JSON.stringify({event:'astra_math_run',date:day,status:result.status,domain_count:result.domains.length}));
  res.setHeader('Cache-Control','public,max-age=60,s-maxage=3600');return res.status(200).json(result);
 }catch(e){console.error('ASTRA_MATH_RUN_FAIL',String(e));return res.status(500).json({status:'FAIL',error:'RESEARCH_EXECUTION_FAILED'});}
}
