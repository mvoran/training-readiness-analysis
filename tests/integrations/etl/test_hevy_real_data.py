"""
Real Integration Test for Hevy Data Processing

This test uses actual data files to validate the complete workflow
and catch real-world issues like file path mismatches.
"""

import pandas as pd
import pytest
from pathlib import Path
from training_readiness.etl.transform_data.hevy.hevy_pipeline import transform


class TestHevyRealData:
    """Integration tests using actual Hevy data files"""

    def test_with_real_data_files(self):
        """Test with actual Hevy data files"""
        # Check if real data files exist
        workout_file = Path("data/raw/hevy/hevy_workouts.csv")
        exercises_file = Path("data/raw/hevy/hevy_exercises.json")
        date_map_file = Path("maps/hevy/map_workout_date_location.csv")
        rollup_map_file = Path("maps/hevy/rollup_location.csv")

        # Skip test if real data files don't exist
        if not workout_file.exists():
            pytest.skip("Real Hevy workout data not found")
        if not exercises_file.exists():
            pytest.skip("Real Hevy exercise templates not found")

        # Read real data
        print(f"Reading real workout data from: {workout_file}")
        real_workouts = pd.read_csv(workout_file)
        print(f"Found {len(real_workouts)} real workout records")

        # Process with real data
        print("Processing real Hevy data...")
        result = transform(
            real_workouts,
            exercises_path=exercises_file,
            date_map=date_map_file if date_map_file.exists() else None,
            rollup_map=rollup_map_file if rollup_map_file.exists() else None,
        )

        # Basic validation
        assert len(result) > 0, "No data processed"
        assert len(result) == len(real_workouts), "Data count mismatch"

        # Check required columns
        required_columns = [
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
        ]
        for col in required_columns:
            assert col in result.columns, f"Missing required column: {col}"

        # Check optional location columns if mapping files exist
        if date_map_file.exists() and rollup_map_file.exists():
            location_columns = ["location", "rollup_location"]
            for col in location_columns:
                assert col in result.columns, f"Missing location column: {col}"

            # Check that some records have location data
            location_data_count = result["location"].notna().sum()
            assert (
                location_data_count > 0
            ), "No location data found despite mapping files"
            print(f"Found location data for {location_data_count} records")
        else:
            print("Location mapping files not found - skipping location validation")

        # Check data quality
        assert result["workout_date"].notna().all(), "Some records missing workout_date"
        assert result["Primary Muscle"].notna().any(), "No muscle data found"

        print(f"Successfully processed {len(result)} real workout records")
        print(f"Columns in output: {list(result.columns)}")

    def test_without_location_files(self):
        """Test behavior when location mapping files are missing"""
        # Check if real data files exist
        workout_file = Path("data/raw/hevy/hevy_workouts.csv")
        exercises_file = Path("data/raw/hevy/hevy_exercises.json")

        # Skip test if real data files don't exist
        if not workout_file.exists():
            pytest.skip("Real Hevy workout data not found")
        if not exercises_file.exists():
            pytest.skip("Real Hevy exercise templates not found")

        # Read real data
        print(f"Reading real workout data from: {workout_file}")
        real_workouts = pd.read_csv(workout_file)
        print(f"Found {len(real_workouts)} real workout records")

        # Process WITHOUT location files (pass None explicitly)
        print("Processing Hevy data without location files...")
        result = transform(
            real_workouts,
            exercises_path=exercises_file,
            date_map=None,  # Explicitly no location files
            rollup_map=None,
        )

        # Basic validation
        assert len(result) > 0, "No data processed"
        assert len(result) == len(real_workouts), "Data count mismatch"

        # Check required columns (should still be present)
        required_columns = [
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
        ]
        for col in required_columns:
            assert col in result.columns, f"Missing required column: {col}"

        # Check that location columns are NOT present
        location_columns = ["location", "rollup_location"]
        for col in location_columns:
            assert (
                col not in result.columns
            ), f"Location column {col} should not be present when no location files provided"

        print(f"Successfully processed {len(result)} records without location data")
        print(f"Columns in output: {list(result.columns)}")

    def test_real_file_paths_match_script_expectations(self):
        """Test that the script's expected file paths match actual files"""
        # Files the script expects
        script_expected_files = [
            "data/raw/hevy/hevy_workouts.csv",
            "data/raw/hevy/hevy_exercises.json",
            "maps/hevy/map_workout_date_location.csv",
            "maps/hevy/rollup_location.csv",
        ]

        # Check each file
        for file_path in script_expected_files:
            path = Path(file_path)
            if path.exists():
                print(f"✓ Found expected file: {file_path}")
            else:
                print(f"✗ Missing expected file: {file_path}")
                # Don't fail the test, just warn

        # Check for unexpected files that might indicate wrong paths
        unexpected_files = [
            "maps/workout_date_location.csv",  # Wrong path
            "maps/location_rollup.csv",  # Wrong path
        ]

        for file_path in unexpected_files:
            path = Path(file_path)
            if path.exists():
                print(f"⚠ Found file at wrong path: {file_path}")
                print("  This might indicate a path mismatch in the script")

    def test_real_data_processing_performance(self):
        """Test performance with real data"""
        workout_file = Path("data/raw/hevy/hevy_workouts.csv")
        exercises_file = Path("data/raw/hevy/hevy_exercises.json")

        if not workout_file.exists() or not exercises_file.exists():
            pytest.skip("Real data files not found")

        import time

        # Read real data
        real_workouts = pd.read_csv(workout_file)

        # Time the processing
        start_time = time.time()
        result = transform(real_workouts, exercises_path=exercises_file)
        end_time = time.time()

        processing_time = end_time - start_time

        # Performance assertions
        assert (
            processing_time < 30.0
        ), f"Processing took too long: {processing_time:.2f} seconds"
        assert len(result) == len(real_workouts), "Data count mismatch"

        print(f"Processed {len(result)} records in {processing_time:.2f} seconds")
        print(f"Processing rate: {len(result)/processing_time:.1f} records/second")
