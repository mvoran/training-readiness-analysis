import duckdb
from datetime import datetime

# 1) Connect to your DuckDB (in‐memory or on‐disk)
con = duckdb.connect('../training_readiness.duckdb')

# 2) Build the timestamp string in yyyymmdd_hhmmss format
ts = datetime.now().strftime('%Y%m%d_%H%M%S')
#    e.g. '20250602_153045'

# 3) Construct the full filename
outfile = f'../data/rolling_1wk_4wk_stress_ratio_{ts}.csv'

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
      CAST(COALESCE(SUM(t.timetotalinhours * 60 * COALESCE(t.rpe, 5)), 0) AS INTEGER) as daily_stress
    FROM calendar c
    LEFT JOIN trainingpeaks_data t
      ON t.workoutday = c.day
    GROUP BY c.day
  ),
  rolling_averages AS (
    SELECT
      day,
      daily_stress,
      CAST(AVG(daily_stress) OVER (
        ORDER BY day
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
      ) AS INTEGER) as rolling_7d_stress,
      CAST(AVG(daily_stress) OVER (
        ORDER BY day
        ROWS BETWEEN 27 PRECEDING AND CURRENT ROW
      ) AS INTEGER) as rolling_28d_stress
    FROM daily_stress
  )
  SELECT
    day,
    daily_stress,
    rolling_7d_stress,
    rolling_28d_stress,
    CASE 
      WHEN rolling_28d_stress = 0 THEN 0
      ELSE CAST(ROUND(rolling_7d_stress::FLOAT / rolling_28d_stress::FLOAT, 2) AS FLOAT)
    END as stress_ratio
  FROM rolling_averages
  ORDER BY day
) TO '{outfile}' (HEADER, DELIMITER ',');
"""

con.execute(sql)
print("Wrote CSV to:", outfile)