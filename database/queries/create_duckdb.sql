-- duckdb: ../training_readiness.duckdb

INSTALL excel;
LOAD excel;

CREATE OR REPLACE TABLE trainingpeaks_data AS
SELECT * FROM read_xlsx('../../source_data/TrainingPeaksExport_2023_2025.xlsx', empty_as_varchar = true);

-- Add primary key constraint
ALTER TABLE trainingpeaks_data ADD PRIMARY KEY (workoutday, title, timetotalinhours);