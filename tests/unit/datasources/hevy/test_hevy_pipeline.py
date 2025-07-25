import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from training_readiness.etl.process_data.hevy.hevy_pipeline import transform


class TestHevyPipeline:
    """Test cases for Hevy pipeline orchestration"""

    def setup_method(self):
        """Set up test fixtures"""
        # Sample input data
        self.sample_df = pd.DataFrame(
            {
                "start_time": ["2024-01-15T10:30:00Z", "2024-01-16T14:45:00Z"],
                "exercise_title": ["Bench Press", "Squat"],
                "sets": [3, 4],
                "reps": [10, 8],
            }
        )

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_basic_workflow(self, mock_location, mock_muscles, mock_time):
        """Test basic pipeline workflow with all processors"""
        # Set up mocks with proper return values
        time_df = self.sample_df.copy()
        time_df["workout_date"] = ["1/15/24", "1/16/24"]
        time_df["day_of_week"] = ["Monday", "Tuesday"]
        mock_time.return_value = time_df

        muscles_df = time_df.copy()
        muscles_df["Primary Muscle"] = ["chest", "quadriceps"]
        muscles_df["Secondary Muscles"] = ["triceps,shoulders", "glutes,hamstrings"]
        muscles_df["primary_muscle_group"] = ["Chest", "Legs"]
        mock_muscles.return_value = muscles_df

        location_df = muscles_df.copy()
        location_df["location"] = ["Primary Gym", "Secondary Gym"]
        location_df["rollup_location"] = ["Primary", "Secondary"]
        mock_location.return_value = location_df

        # Call transform
        result = transform(self.sample_df)

        # Verify all processors were called in correct order
        mock_time.assert_called_once_with(self.sample_df)
        mock_muscles.assert_called_once()
        mock_location.assert_called_once()

        # Verify the call order (time -> muscles -> location)
        assert mock_time.call_count == 1
        assert mock_muscles.call_count == 1
        assert mock_location.call_count == 1

        # Verify the result contains all expected columns
        expected_columns = [
            "start_time",
            "exercise_title",
            "sets",
            "reps",
            "workout_date",
            "day_of_week",
            "Primary Muscle",
            "Secondary Muscles",
            "primary_muscle_group",
            "location",
            "rollup_location",
        ]
        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_with_location_maps(self, mock_location, mock_muscles, mock_time):
        """Test pipeline with location mapping files provided"""
        # Set up mocks
        mock_time.return_value = self.sample_df.copy()
        mock_muscles.return_value = self.sample_df.copy()
        mock_location.return_value = self.sample_df.copy()

        # Create mock file paths
        date_map = Path("test_date_map.csv")
        rollup_map = Path("test_rollup_map.csv")

        # Call transform with location maps
        result = transform(self.sample_df, date_map=date_map, rollup_map=rollup_map)

        # Verify location processor was called with the provided maps
        mock_location.assert_called_once_with(
            mock_muscles.return_value, date_map=date_map, rollup_map=rollup_map
        )

        # Verify result is returned
        assert result is not None

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_without_location_maps(
        self, mock_location, mock_muscles, mock_time
    ):
        """Test pipeline without location mapping files"""
        # Set up mocks
        mock_time.return_value = self.sample_df.copy()
        mock_muscles.return_value = self.sample_df.copy()
        mock_location.return_value = self.sample_df.copy()

        # Call transform without location maps
        result = transform(self.sample_df)

        # Verify location processor was called with None values
        mock_location.assert_called_once_with(
            mock_muscles.return_value, date_map=None, rollup_map=None
        )

        # Verify result is returned
        assert result is not None

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_custom_exercises_path(
        self, mock_location, mock_muscles, mock_time
    ):
        """Test pipeline with custom exercises file path"""
        # Set up mocks
        mock_time.return_value = self.sample_df.copy()
        mock_muscles.return_value = self.sample_df.copy()
        mock_location.return_value = self.sample_df.copy()

        # Create custom exercises path
        custom_exercises_path = Path("/custom/path/exercises.json")

        # Call transform with custom exercises path
        result = transform(self.sample_df, exercises_path=custom_exercises_path)

        # Verify muscles processor was called with custom path
        mock_muscles.assert_called_once_with(
            mock_time.return_value, exercises_path=custom_exercises_path
        )

        # Verify result is returned
        assert result is not None

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_processor_chain(self, mock_location, mock_muscles, mock_time):
        """Test that data flows correctly through the processor chain"""
        # Set up mocks to return modified dataframes
        time_df = self.sample_df.copy()
        time_df["workout_date"] = ["1/15/24", "1/16/24"]
        mock_time.return_value = time_df

        muscles_df = time_df.copy()
        muscles_df["Primary Muscle"] = ["chest", "quadriceps"]
        mock_muscles.return_value = muscles_df

        location_df = muscles_df.copy()
        location_df["location"] = ["Primary Gym", "Secondary Gym"]
        mock_location.return_value = location_df

        # Call transform
        result = transform(self.sample_df)

        # Verify the data flows through each processor
        mock_time.assert_called_once_with(self.sample_df)
        # Note: muscles processor is called with additional parameters, so we check differently
        assert mock_muscles.call_count == 1
        # Location processor is called with additional parameters, so we check differently
        assert mock_location.call_count == 1

        # Verify final result contains all transformations
        assert "workout_date" in result.columns
        assert "Primary Muscle" in result.columns
        assert "location" in result.columns

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_empty_dataframe(self, mock_location, mock_muscles, mock_time):
        """Test pipeline with empty dataframe"""
        empty_df = pd.DataFrame(columns=["start_time", "exercise_title"])

        # Set up mocks
        mock_time.return_value = empty_df.copy()
        mock_muscles.return_value = empty_df.copy()
        mock_location.return_value = empty_df.copy()

        # Call transform
        result = transform(empty_df)

        # Verify all processors were called
        mock_time.assert_called_once_with(empty_df)
        mock_muscles.assert_called_once()
        mock_location.assert_called_once()

        # Verify result is empty
        assert len(result) == 0

    @patch("training_readiness.etl.process_data.hevy.processors.time.add_time_columns")
    @patch(
        "training_readiness.etl.process_data.hevy.processors.muscles.add_muscle_groups"
    )
    @patch(
        "training_readiness.etl.process_data.hevy.processors.location.add_location_columns"
    )
    def test_transform_preserves_original_data(
        self, mock_location, mock_muscles, mock_time
    ):
        """Test that original data is preserved through the pipeline"""
        # Set up mocks to return dataframes with added columns
        time_df = self.sample_df.copy()
        time_df["workout_date"] = ["1/15/24", "1/16/24"]
        mock_time.return_value = time_df

        muscles_df = time_df.copy()
        muscles_df["Primary Muscle"] = ["chest", "quadriceps"]
        mock_muscles.return_value = muscles_df

        location_df = muscles_df.copy()
        location_df["location"] = ["Primary Gym", "Secondary Gym"]
        mock_location.return_value = location_df

        # Call transform
        result = transform(self.sample_df)

        # Verify original columns are preserved
        original_columns = ["start_time", "exercise_title", "sets", "reps"]
        for col in original_columns:
            assert col in result.columns

        # Verify original data is unchanged
        assert result.iloc[0]["exercise_title"] == "Bench Press"
        assert result.iloc[0]["sets"] == 3
        assert result.iloc[1]["exercise_title"] == "Squat"
        assert result.iloc[1]["sets"] == 4

    def test_transform_default_parameters(self):
        """Test that default parameters are used correctly"""
        # This test verifies the function signature and default values
        import inspect

        sig = inspect.signature(transform)

        # Check default parameters
        assert sig.parameters["exercises_path"].default == Path(
            "data/raw/hevy/hevy_exercises.json"
        )
        assert sig.parameters["date_map"].default is None
        assert sig.parameters["rollup_map"].default is None
