-- Isolated, idempotent, additive migration. Do not drop or modify other ASTRA tables.
CREATE TABLE IF NOT EXISTS public.astra_math_lab_runs (
  run_day DATE NOT NULL,
  version TEXT NOT NULL,
  source TEXT NOT NULL CHECK (source IN ('manual_seed','vercel_cron')),
  status TEXT NOT NULL,
  report JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (run_day,version)
);
