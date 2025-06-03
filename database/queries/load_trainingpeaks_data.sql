CREATE OR REPLACE TABLE trainingpeaks_data AS
  SELECT *
    FROM read_xlsx('{{EXCEL_PATH}}', empty_as_varchar = true);

-- Drop existing primary key if it exists
DROP INDEX IF EXISTS "PRIMARY_trainingpeaks_data_workoutday_title_timetotalinhours";

-- Add primary key constraint to prevent duplicate workouts
ALTER TABLE trainingpeaks_data ADD PRIMARY KEY (workoutday, title, timetotalinhours);