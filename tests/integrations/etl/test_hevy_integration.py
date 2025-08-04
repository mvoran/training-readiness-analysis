import json
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch
from training_readiness.etl.transform_data.hevy.process_hevy_data import main
from training_readiness.etl.transform_data.hevy.hevy_pipeline import transform


class TestHevyIntegration:
    """Integration tests for complete Hevy data processing workflow"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create test data directory structure
        self.test_data_dir = Path("test_data")
        self.raw_dir = self.test_data_dir / "raw" / "hevy"
        self.processed_dir = self.test_data_dir / "processed" / "hevy"
        self.maps_dir = self.test_data_dir / "maps"

        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.maps_dir.mkdir(parents=True, exist_ok=True)

        # Create sample workout data
        self.sample_workouts = pd.DataFrame(
            {
                "workout_id": [1, 1, 2, 2],
                "title": ["Push Day", "Push Day", "Pull Day", "Pull Day"],
                "description": [
                    "Chest and triceps",
                    "Chest and triceps",
                    "Back and biceps",
                    "Back and biceps",
                ],
                "start_time": [
                    "2024-01-15T10:30:00Z",
                    "2024-01-15T10:30:00Z",
                    "2024-01-16T14:45:00Z",
                    "2024-01-16T14:45:00Z",
                ],
                "end_time": [
                    "2024-01-15T11:30:00Z",
                    "2024-01-15T11:30:00Z",
                    "2024-01-16T15:45:00Z",
                    "2024-01-16T15:45:00Z",
                ],
                "exercise_title": [
                    "Bench Press",
                    "Incline Press",
                    "Pull-up",
                    "Barbell Row",
                ],
                "sets": [3, 3, 3, 3],
                "reps": [10, 8, 8, 10],
                "weight": [135, 115, 0, 95],
                "rpe": [8, 8, 8, 8],
                "workout_name": ["Push Day", "Push Day", "Pull Day", "Pull Day"],
            }
        )

        # Create sample exercise templates
        self.sample_exercises = [
            {
                "title": "Bench Press",
                "primary_muscle_group": "chest",
                "secondary_muscle_groups": ["triceps", "shoulders"],
            },
            {
                "title": "Incline Press",
                "primary_muscle_group": "chest",
                "secondary_muscle_groups": ["triceps", "shoulders"],
            },
            {
                "title": "Pull-up",
                "primary_muscle_group": "lats",
                "secondary_muscle_groups": ["biceps", "upper_back"],
            },
            {
                "title": "Barbell Row",
                "primary_muscle_group": "upper_back",
                "secondary_muscle_groups": ["biceps", "lats"],
            },
        ]

        # Create sample location mapping files
        self.date_location_map = pd.DataFrame(
            {
                "workout_date": ["1/15/24", "1/16/24"],
                "location": ["Primary Gym", "Secondary Gym"],
            }
        )

        self.location_rollup_map = pd.DataFrame(
            {
                "location": ["Primary Gym", "Secondary Gym"],
                "rollup_location": ["Primary", "Secondary"],
            }
        )

    def teardown_method(self):
        """Clean up test files"""
        import shutil

        if self.test_data_dir.exists():
            shutil.rmtree(self.test_data_dir)

    def test_complete_workflow_with_and_without_location_maps(self):
        """Test complete workflow with and without location mapping files"""
        # Write test data files
        self.sample_workouts.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)

        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Test WITH location files
        print("Testing WITH location mapping files...")
        self.date_location_map.to_csv(
            self.maps_dir / "workout_date_location.csv", index=False
        )
        self.location_rollup_map.to_csv(
            self.maps_dir / "location_rollup.csv", index=False
        )

        result_with_location = transform(
            self.sample_workouts,
            exercises_path=self.raw_dir / "hevy_exercises.json",
            date_map=self.maps_dir / "workout_date_location.csv",
            rollup_map=self.maps_dir / "location_rollup.csv",
        )

        # Verify result WITH location contains all expected columns
        expected_columns_with_location = [
            "workout_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "exercise_title",
            "sets",
            "reps",
            "weight",
            "rpe",
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
            "location",
            "rollup_location",
        ]

        for col in expected_columns_with_location:
            assert (
                col in result_with_location.columns
            ), f"Missing column with location: {col}"

        # Verify location processing works
        assert result_with_location.iloc[0]["location"] == "Primary Gym"
        assert result_with_location.iloc[0]["rollup_location"] == "Primary"
        assert result_with_location.iloc[2]["location"] == "Secondary Gym"
        assert result_with_location.iloc[2]["rollup_location"] == "Secondary"

        # Test WITHOUT location files
        print("Testing WITHOUT location mapping files...")
        # Remove location files
        (self.maps_dir / "workout_date_location.csv").unlink(missing_ok=True)
        (self.maps_dir / "location_rollup.csv").unlink(missing_ok=True)

        result_without_location = transform(
            self.sample_workouts,
            exercises_path=self.raw_dir / "hevy_exercises.json",
            date_map=None,
            rollup_map=None,
        )

        # Verify result WITHOUT location contains expected columns (no location columns)
        expected_columns_without_location = [
            "workout_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "exercise_title",
            "sets",
            "reps",
            "weight",
            "rpe",
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
        ]

        for col in expected_columns_without_location:
            assert (
                col in result_without_location.columns
            ), f"Missing column without location: {col}"

        # Verify location columns are NOT present
        location_columns = ["location", "rollup_location"]
        for col in location_columns:
            assert (
                col not in result_without_location.columns
            ), f"Location column {col} should not be present when no location files provided"

        # Verify other processing still works correctly
        assert result_without_location.iloc[0]["workout_date"] == "1/15/24"
        assert result_without_location.iloc[0]["day_of_week"] == "Monday"
        assert result_without_location.iloc[0]["Primary Muscle"] == "chest"
        assert result_without_location.iloc[0]["primary_muscle_group"] == "Chest"

        # Verify data integrity is maintained in both cases
        assert len(result_with_location) == len(self.sample_workouts)
        assert len(result_without_location) == len(self.sample_workouts)

        # Verify original data is preserved in both cases
        assert result_with_location.iloc[0]["exercise_title"] == "Bench Press"
        assert result_with_location.iloc[0]["sets"] == 3
        assert result_with_location.iloc[0]["reps"] == 10
        assert result_without_location.iloc[0]["exercise_title"] == "Bench Press"
        assert result_without_location.iloc[0]["sets"] == 3
        assert result_without_location.iloc[0]["reps"] == 10

        print("Both scenarios tested successfully!")

    def test_complete_workflow_without_location_maps(self):
        """Test complete workflow without location mapping files"""
        # Write test data files (no location maps)
        self.sample_workouts.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)

        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Call transform without location maps
        result = transform(
            self.sample_workouts, exercises_path=self.raw_dir / "hevy_exercises.json"
        )

        # Verify the result contains expected columns (no location columns)
        expected_columns = [
            "workout_id",
            "title",
            "description",
            "start_time",
            "end_time",
            "exercise_title",
            "sets",
            "reps",
            "weight",
            "rpe",
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
        ]

        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"

        # Verify location columns are NOT present
        assert "location" not in result.columns
        assert "rollup_location" not in result.columns

        # Verify other processing still works
        assert result.iloc[0]["workout_date"] == "1/15/24"
        assert result.iloc[0]["Primary Muscle"] == "chest"
        assert result.iloc[0]["primary_muscle_group"] == "Chest"

    def test_workflow_with_unknown_exercises(self):
        """Test workflow with exercises not in the template"""
        # Add unknown exercise to workout data
        workouts_with_unknown = self.sample_workouts.copy()
        workouts_with_unknown.loc[len(workouts_with_unknown)] = [
            3,
            "Leg Day",
            "Legs",
            "2024-01-17T16:00:00Z",
            "2024-01-17T17:00:00Z",
            "Unknown Exercise",
            3,
            12,
            0,
            7,
        ]

        # Write test data files
        workouts_with_unknown.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)

        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Call transform
        result = transform(
            workouts_with_unknown, exercises_path=self.raw_dir / "hevy_exercises.json"
        )

        # Verify unknown exercise has empty muscle groups
        unknown_row = result[result["exercise_title"] == "Unknown Exercise"].iloc[0]
        assert unknown_row["Primary Muscle"] == ""
        assert unknown_row["Secondary Muscles"] == ""
        assert pd.isna(unknown_row["primary_muscle_group"])

        # Verify known exercises still work
        known_row = result[result["exercise_title"] == "Bench Press"].iloc[0]
        assert known_row["Primary Muscle"] == "chest"
        assert known_row["Secondary Muscles"] == "triceps,shoulders"

    def test_workflow_location_inference_from_workout_name(self):
        """Test that location can be inferred from workout_name when date map lacks the date"""
        # Write base sample workouts and exercises JSON
        self.sample_workouts.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)
        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Write mapping files to maps dir
        self.date_location_map.to_csv(
            self.maps_dir / "workout_date_location.csv", index=False
        )
        self.location_rollup_map.to_csv(
            self.maps_dir / "location_rollup.csv", index=False
        )

        # Create a new row: workout on a new date, with workout_name containing canonical location string
        new_row = {
            "workout_id": 3,
            "title": "Leg Day",
            "description": "Legs",
            "start_time": "2024-01-17T16:00:00Z",
            "end_time": "2024-01-17T17:00:00Z",
            "exercise_title": "Squat",
            "sets": 4,
            "reps": 8,
            "weight": 225,
            "rpe": 9,
            "workout_name": "Leg Day @ Secondary Gym",
        }
        workouts_with_inference = pd.concat(
            [self.sample_workouts, pd.DataFrame([new_row])], ignore_index=True
        )

        # Call transform with both mapping files
        result = transform(
            workouts_with_inference,
            exercises_path=self.raw_dir / "hevy_exercises.json",
            date_map=self.maps_dir / "workout_date_location.csv",
            rollup_map=self.maps_dir / "location_rollup.csv",
        )

        # Find the new Squat row
        squat_row = result[result["exercise_title"] == "Squat"].iloc[0]
        assert squat_row["location"] == "Secondary Gym"
        assert squat_row["rollup_location"] == "Secondary"

        # Existing row (Bench Press) still has original location
        bench_row = result[result["exercise_title"] == "Bench Press"].iloc[0]
        assert bench_row["location"] == "Primary Gym"

        # Columns should include location and rollup_location
        assert "location" in result.columns
        assert "rollup_location" in result.columns

    def test_workflow_with_missing_files(self):
        """Test workflow behavior when required files are missing"""
        # Try to call transform with missing files
        with pytest.raises(FileNotFoundError):
            transform(
                self.sample_workouts, exercises_path=Path("/nonexistent/exercises.json")
            )

    def test_workflow_data_integrity(self):
        """Test that data integrity is maintained through the workflow"""
        # Write test data files
        self.sample_workouts.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)

        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Call transform
        result = transform(
            self.sample_workouts, exercises_path=self.raw_dir / "hevy_exercises.json"
        )

        # Verify row count is preserved
        assert len(result) == len(self.sample_workouts)

        # Verify all original columns are preserved
        original_columns = self.sample_workouts.columns.tolist()
        for col in original_columns:
            assert col in result.columns

        # Verify original data values are unchanged
        for col in original_columns:
            pd.testing.assert_series_equal(
                result[col], self.sample_workouts[col], check_names=False
            )

    @pytest.mark.slow
    def test_workflow_performance(self):
        """Test workflow performance with larger dataset"""
        # Create larger dataset
        large_workouts = pd.concat([self.sample_workouts] * 100, ignore_index=True)

        # Write test data files
        large_workouts.to_csv(self.raw_dir / "hevy_workouts.csv", index=False)

        with open(self.raw_dir / "hevy_exercises.json", "w") as f:
            json.dump(self.sample_exercises, f)

        # Time the transform operation
        import time

        start_time = time.time()

        result = transform(
            large_workouts, exercises_path=self.raw_dir / "hevy_exercises.json"
        )

        end_time = time.time()
        processing_time = end_time - start_time

        # Verify result
        assert len(result) == len(large_workouts)
        assert "workout_date" in result.columns
        assert "Primary Muscle" in result.columns

        # Performance assertion (should complete within reasonable time)
        assert processing_time < 10.0, f"Processing took {processing_time:.2f} seconds"
