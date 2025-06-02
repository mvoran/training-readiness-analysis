-- duckdb: ../training_readiness.duckdb

INSTALL excel;
LOAD excel;

-- First ensure the table exists with proper constraints
CREATE TABLE IF NOT EXISTS trainingpeaks_data (
    workoutday DATE,
    timetotalinhours DOUBLE,
    rpe INTEGER,
    feeling VARCHAR,
    -- Add other columns as needed
    UNIQUE(workoutday, timetotalinhours, rpe)  -- This creates a unique constraint
);

-- Then insert new data, ignoring duplicates
INSERT OR IGNORE INTO trainingpeaks_data
SELECT * FROM read_xlsx('../../source_data/TrainingPeaksExport_2023_2025.xlsx', empty_as_varchar = true);