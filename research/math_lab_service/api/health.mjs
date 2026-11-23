import {VERSION} from '../src/engine.mjs';
export default function handler(req,res){if(req.method!=='GET')return res.status(405).json({error:'METHOD_NOT_ALLOWED'});
return res.status(200).json({name:'ASTRA MATH LAB Ω',status:'UP',version:VERSION,capabilities:['number_theory','graph_theory','combinatorics','sat_logic','conjecture_synthesis','exact_polynomial_certificates','counterexample_search','memory_aware_scheduled_research'],execution:'on_request_or_daily_vercel_cron',persistence:'Neon PostgreSQL for scheduled executions; see /api/history',prices_eur:0});}
