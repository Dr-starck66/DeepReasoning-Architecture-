import {runResearch} from '../src/engine.mjs';
import {discoverCycle} from '../src/conjecture-engine.mjs';
import {timingSafeEqual} from 'node:crypto';

function equalSecret(header, secret) {
  if (typeof header !== 'string' || typeof secret !== 'string' || !secret) return false;
  const lhs = Buffer.from(header); const rhs=Buffer.from(`Bearer ${secret}`);
  return lhs.length===rhs.length && timingSafeEqual(lhs,rhs);
}

/** Vercel Cron calls only the production deployment. Idempotent DB write. */
export default async function handler(req,res){
  if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'METHOD_NOT_ALLOWED'});}
  if(!process.env.CRON_SECRET || !process.env.DATABASE_URL)
    return res.status(503).json({error:'NOT_CONFIGURED'});
  if(!equalSecret(req.headers?.authorization,process.env.CRON_SECRET))
    return res.status(401).json({error:'UNAUTHORIZED'});
  const day = new Date().toISOString().slice(0,10);
  try {
    const {neon}=await import('@neondatabase/serverless');
    const sql=neon(process.env.DATABASE_URL);
    // Memory across autonomous cycles: avoid regenerating already saved candidates.
    const prior=await sql`SELECT report->'research_cycle'->'candidate_ids' AS ids
      FROM public.astra_math_lab_runs WHERE report ? 'research_cycle' ORDER BY created_at DESC LIMIT 90`;
    const seenIds=prior.flatMap(x=>Array.isArray(x.ids)?x.ids:[]);
    const research_cycle=discoverCycle(day,{seenIds});
    const report={...runResearch(day),research_cycle};
    const inserted = await sql`INSERT INTO public.astra_math_lab_runs (run_day,version,source,status,report)
    VALUES (${day}::date, ${report.version}, 'vercel_cron', ${report.status}, ${JSON.stringify(report)}::jsonb)
    ON CONFLICT (run_day,version) DO NOTHING RETURNING run_day`;
    console.log(JSON.stringify({event:'astra_math_cron',day,inserted:inserted.length,domain_count:report.domains.length,new_candidates:research_cycle.candidate_ids.length}));
    return res.status(200).json({status:'PASS_PERSISTED',day,inserted:inserted.length,domains:report.domains.length,new_candidates:research_cycle.candidate_ids.length});
  } catch (e) {
    console.error('ASTRA_MATH_CRON_FAILURE',String(e?.message||e));
    return res.status(500).json({status:'FAIL',error:'CRON_PERSISTENCE_FAILED'});
  }
}
