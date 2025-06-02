import duckdb
from datetime import datetime

# 1) Connect to your DuckDB (in‐memory or on‐disk)
con = duckdb.connect('../training_readiness.duckdb')

# 2) Build the timestamp string in yyyymmdd_hhmmss format
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
#    e.g. '20250602_153045'

# 3) Construct the full filename
outfile = f'../data/rolling_1wk_stress_{ts}.csv'

# 4) Run the COPY statement with that literal filename
sql = f"""
COPY (
  WITH calendar AS (
    SELECT gs.generate_series::DATE AS day
    FROM generate_series(
      current_date - INTERVAL '179 days',
      current_date,
      INTERVAL '1 day'
    ) AS gs
  ),
  daily_stress AS (
    SELECT
      c.day,
      CAST(COALESCE(SUM(t.timetotalinhours * 60 * COALESCE(t.rpe, 5)), 0) AS INTEGER) as rolling_1wk_stress
    FROM calendar c
    LEFT JOIN trainingpeaks_data t
      ON t.workoutday >= (c.day - INTERVAL '6 days')
      AND t.workoutday < (c.day + INTERVAL '1 day')
    GROUP BY c.day
  )
  SELECT *
  FROM daily_stress
  ORDER BY day
) TO '{outfile}' (HEADER, DELIMITER ',');
"""

con.execute(sql)
print("Wrote CSV to:", outfile)