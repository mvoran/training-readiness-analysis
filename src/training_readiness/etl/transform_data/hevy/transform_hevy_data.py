"""
Transform Hevy Data Script

This script transforms raw Hevy workout data by:
1. Adding time-based columns (workout_date, day_of_week)
2. Mapping exercises to muscle groups using exercise templates
3. Optionally adding location data using mapping files
4. Outputting processed data with timestamped filenames

Required files:
- data/raw_data/hevy/hevy_workouts.csv: Raw workout data from Hevy API
- data/raw_data/hevy/hevy_exercises.json: Exercise templates from Hevy API

Optional files:
- maps/workout_date_location.csv: Maps workout dates to locations
- maps/location_rollup.csv: Rolls up locations into categories

Output:
- data/transformed_data/hevy/hevy_workouts_processed_YYYYMMDD_HHMMSS.csv
"""

from datetime import datetime
from pathlib import Path
import pandas as pd
import os
import sys

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.transform_data.hevy.hevy_pipeline import (  # noqa: E402
    transform,
)


def main():
    try:
        # Read input files
        workout_file = "data/raw_data/hevy/hevy_workouts.csv"
        exercises_file = "data/raw_data/hevy/hevy_exercises.json"
        date_map = Path("maps/hevy/map_workout_date_location.csv")
        rollup_map = Path("maps/hevy/rollup_location.csv")

        print(f"Reading Hevy workout data from: {workout_file}")
        raw_df = pd.read_csv(workout_file)
        print(f"Extracted {len(raw_df)} workout records")

        print(f"Reading Hevy exercise templates from: {exercises_file}")
        exercises_path = Path(exercises_file)
        if not exercises_path.exists():
            raise FileNotFoundError(
                f"Exercise templates file not found: {exercises_file}"
            )

        # Check for optional location mapping files
        if date_map.exists() and rollup_map.exists():
            print(f"Using location mapping files: {date_map} and {rollup_map}")
        else:
            print("Location mapping files not found - processing without location data")

        # Process the data
        print("Processing Hevy data...")
        final_df = transform(
            raw_df,
            exercises_path=exercises_path,
            date_map=date_map if date_map.exists() else None,
            rollup_map=rollup_map if rollup_map.exists() else None,
        )
        print(f"Processed {len(final_df)} workout records")

        # Save output
        out_dir = Path("data/transformed_data/hevy")
        out_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = out_dir / f"hevy_workouts_processed_{timestamp}.csv"

        print(f"Saving processed Hevy data to: {output_file}")
        final_df.to_csv(output_file, index=False)
        print(f"Successfully saved {len(final_df)} workout records to {output_file}")

        print("Hevy data processing completed successfully!")

    except FileNotFoundError as e:
        print(f"Error: Input file not found: {e}")
        raise
    except Exception as e:
        print(f"Error processing Hevy data: {str(e)}")
        raise


if __name__ == "__main__":
    main()
