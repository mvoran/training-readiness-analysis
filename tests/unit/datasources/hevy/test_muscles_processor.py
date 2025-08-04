import json
import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import patch
from training_readiness.etl.transform_data.hevy.processors.muscles import (
    add_muscle_groups,
)


class TestMusclesProcessor:
    """Test cases for muscles processor functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Sample exercise templates
        self.sample_exercises = [
            {
                "title": "Bench Press",
                "primary_muscle_group": "chest",
                "secondary_muscle_groups": ["triceps", "shoulders"],
            },
            {
                "title": "Squat",
                "primary_muscle_group": "quadriceps",
                "secondary_muscle_groups": ["glutes", "hamstrings"],
            },
            {
                "title": "Deadlift",
                "primary_muscle_group": "lower_back",
                "secondary_muscle_groups": ["hamstrings", "glutes"],
            },
            {
                "title": "Pull-up",
                "primary_muscle_group": "lats",
                "secondary_muscle_groups": ["biceps", "upper_back"],
            },
        ]

        # Sample rollup data as DataFrame
        self.sample_rollup_df = pd.DataFrame(
            {
                "primary_muscle": [
                    "chest",
                    "quadriceps",
                    "lower_back",
                    "lats",
                    "biceps",
                    "triceps",
                    "shoulders",
                    "glutes",
                    "hamstrings",
                    "upper_back",
                ],
                "primary_muscle_rollup": [
                    "Chest",
                    "Legs",
                    "Back",
                    "Back",
                    "Arms",
                    "Arms",
                    "Shoulders",
                    "Legs",
                    "Legs",
                    "Back",
                ],
            }
        )

    def test_add_muscle_groups_basic(self):
        """Test basic muscle group addition"""
        # Create sample workout data
        df = pd.DataFrame({"exercise_title": ["Bench Press", "Squat", "Deadlift"]})

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        # Check that new columns were added
        assert "Primary Muscle" in result.columns
        assert "Secondary Muscles" in result.columns
        assert "primary_muscle_group" in result.columns

        # Check primary muscle mapping
        assert result.iloc[0]["Primary Muscle"] == "chest"
        assert result.iloc[1]["Primary Muscle"] == "quadriceps"
        assert result.iloc[2]["Primary Muscle"] == "lower_back"

        # Check secondary muscles
        assert result.iloc[0]["Secondary Muscles"] == "triceps,shoulders"
        assert result.iloc[1]["Secondary Muscles"] == "glutes,hamstrings"
        assert result.iloc[2]["Secondary Muscles"] == "hamstrings,glutes"

    def test_add_muscle_groups_unknown_exercise(self):
        """Test handling of unknown exercises"""
        df = pd.DataFrame({"exercise_title": ["Unknown Exercise", "Bench Press"]})

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        # Unknown exercise should have empty muscle groups
        assert result.iloc[0]["Primary Muscle"] == ""
        assert result.iloc[0]["Secondary Muscles"] == ""

        # Known exercise should be mapped correctly
        assert result.iloc[1]["Primary Muscle"] == "chest"

    def test_add_muscle_groups_empty_secondary_muscles(self):
        """Test exercises with no secondary muscle groups"""
        exercises_no_secondary = [
            {
                "title": "Isolation Exercise",
                "primary_muscle_group": "biceps",
                "secondary_muscle_groups": None,
            }
        ]

        df = pd.DataFrame({"exercise_title": ["Isolation Exercise"]})

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(exercises_no_secondary)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        assert result.iloc[0]["Primary Muscle"] == "biceps"
        assert result.iloc[0]["Secondary Muscles"] == ""

    def test_add_muscle_groups_rollup_mapping(self):
        """Test that muscle rollup mapping works correctly"""
        df = pd.DataFrame({"exercise_title": ["Bench Press", "Squat"]})

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        # Check rollup mapping
        assert result.iloc[0]["primary_muscle_group"] == "Chest"
        assert result.iloc[1]["primary_muscle_group"] == "Legs"

    def test_add_muscle_groups_preserves_original_data(self):
        """Test that original data is preserved"""
        df = pd.DataFrame(
            {"exercise_title": ["Bench Press"], "sets": [3], "reps": [10]}
        )

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        # Original columns should be preserved
        assert "exercise_title" in result.columns
        assert "sets" in result.columns
        assert "reps" in result.columns

        # Original data should be unchanged
        assert result.iloc[0]["sets"] == 3
        assert result.iloc[0]["reps"] == 10

    def test_add_muscle_groups_empty_dataframe(self):
        """Test handling of empty dataframe"""
        df = pd.DataFrame(columns=["exercise_title"])

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df)

        assert "Primary Muscle" in result.columns
        assert "Secondary Muscles" in result.columns
        assert "primary_muscle_group" in result.columns
        assert len(result) == 0

    def test_add_muscle_groups_custom_exercises_path(self):
        """Test using custom exercises file path"""
        df = pd.DataFrame({"exercise_title": ["Bench Press"]})

        custom_path = Path("/custom/path/exercises.json")

        with patch(
            "pathlib.Path.read_text", return_value=json.dumps(self.sample_exercises)
        ):
            with patch("pandas.read_csv", return_value=self.sample_rollup_df):
                result = add_muscle_groups(df, exercises_path=custom_path)

        assert result.iloc[0]["Primary Muscle"] == "chest"

    def test_add_muscle_groups_missing_exercises_file(self):
        """Test handling of missing exercises file"""
        df = pd.DataFrame({"exercise_title": ["Bench Press"]})

        with pytest.raises(FileNotFoundError):
            add_muscle_groups(df, exercises_path=Path("/nonexistent/file.json"))
