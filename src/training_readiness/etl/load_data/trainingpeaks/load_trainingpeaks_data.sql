-- If {{REPLACE_MODE}} is true, drop and recreate the table
{% if REPLACE_MODE %}
DROP TABLE IF EXISTS trainingpeaks_data;
{% endif %}

-- Create table if it doesn't exist, or append to it if it does
CREATE TABLE IF NOT EXISTS trainingpeaks_data AS
  SELECT *
    FROM {% if FILE_TYPE == 'csv' %}
         read_csv_auto('{{FILE_PATH}}', header=true, nullstr='', sample_size=1000)
         {% else %}
         read_xlsx('{{FILE_PATH}}', empty_as_varchar = true)
         {% endif %};

-- If table already existed, append the new data
{% if not REPLACE_MODE %}
INSERT INTO trainingpeaks_data
  SELECT *
    FROM {% if FILE_TYPE == 'csv' %}
         read_csv_auto('{{FILE_PATH}}', header=true, nullstr='', sample_size=1000)
         {% else %}
         read_xlsx('{{FILE_PATH}}', empty_as_varchar = true)
         {% endif %};
{% endif %}

-- Only handle primary key in replace mode
{% if REPLACE_MODE %}
-- Drop existing primary key if it exists
DROP INDEX IF EXISTS "PRIMARY_trainingpeaks_data_workoutday_title_timetotalinhours";

-- Add primary key constraint to prevent duplicate workouts
ALTER TABLE trainingpeaks_data ADD PRIMARY KEY (workoutday, title, timetotalinhours);
{% endif %}