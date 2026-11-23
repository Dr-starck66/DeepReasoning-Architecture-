/** Read-only, bounded SQL query. Never accepts SQL or arbitrary query strings. */
export default async function handler(req,res){
  if(req.method!=='GET'){res.setHeader('Allow','GET');return res.status(405).json({error:'METHOD_NOT_ALLOWED'});}
  if(!process.env.DATABASE_URL)return res.status(503).json({error:'NOT_CONFIGURED'});
  try {
    const {neon}=await import('@neondatabase/serverless');
    const sql=neon(process.env.DATABASE_URL);
    const rows=await sql`SELECT run_day::text AS day, version,source,status,created_at,
    report->'domains' AS domains,report->'evidence' AS evidence
    FROM public.astra_math_lab_runs ORDER BY run_day DESC LIMIT 14`;
    res.setHeader('Cache-Control','public,max-age=30,s-maxage=60');
    return res.status(200).json({service:'ASTRA MATH LAB Ω',storage:'Neon PostgreSQL persistent',rows});
  }catch(e){console.error('ASTRA_MATH_HISTORY_FAIL',String(e?.message||e));
    return res.status(500).json({error:'PERSISTENCE_READ_FAILED'});}
}
