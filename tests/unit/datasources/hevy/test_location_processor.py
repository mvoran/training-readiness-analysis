import pandas as pd
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch
from training_readiness.etl.process_data.hevy.processors.location import (
    add_location_columns,
)


class TestLocationProcessor:
    """Test cases for location processor functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        # Sample date-location mapping data
        self.sample_date_map_data = """workout_date,location
1/15/24,Primary Gym
1/16/24,Secondary Gym
1/17/24,Vacation Gym"""

        # Sample location rollup data
        self.sample_rollup_data = """location,rollup_location
Primary Gym,Primary
Secondary Gym,Secondary
Vacation Gym,Other"""

    def test_add_location_columns_basic(self):
        """Test basic location column addition"""
        # Create sample workout data
        df = pd.DataFrame(
            {
                "workout_date": ["1/15/24", "1/16/24", "1/17/24"],
                "exercise_title": ["Bench Press", "Squat", "Deadlift"],
            }
        )

        # Create temporary mapping files
        date_map = Path("temp_date_map.csv")
        rollup_map = Path("temp_rollup_map.csv")

        try:
            # Write test data to temporary files
            date_map.write_text(self.sample_date_map_data)
            rollup_map.write_text(self.sample_rollup_data)

            result = add_location_columns(df, date_map=date_map, rollup_map=rollup_map)

            # Check that new columns were added
            assert "location" in result.columns
            assert "rollup_location" in result.columns

            # Check location mapping
            assert result.iloc[0]["location"] == "Primary Gym"
            assert result.iloc[1]["location"] == "Secondary Gym"
            assert result.iloc[2]["location"] == "Vacation Gym"

            # Check rollup mapping
            assert result.iloc[0]["rollup_location"] == "Primary"
            assert result.iloc[1]["rollup_location"] == "Secondary"
            assert result.iloc[2]["rollup_location"] == "Other"

        finally:
            # Clean up temporary files
            if date_map.exists():
                date_map.unlink()
            if rollup_map.exists():
                rollup_map.unlink()

    def test_add_location_columns_missing_date_map(self):
        """Test handling when date map file is missing"""
        df = pd.DataFrame(
            {"workout_date": ["1/15/24"], "exercise_title": ["Bench Press"]}
        )

        # Only provide rollup map
        rollup_map = Path("temp_rollup_map.csv")

        try:
            rollup_map.write_text(self.sample_rollup_data)

            result = add_location_columns(df, date_map=None, rollup_map=rollup_map)

            # Should return original dataframe unchanged
            assert "location" not in result.columns
            assert "rollup_location" not in result.columns
            assert len(result) == 1
            assert result.iloc[0]["exercise_title"] == "Bench Press"

        finally:
            if rollup_map.exists():
                rollup_map.unlink()

    def test_add_location_columns_missing_rollup_map(self):
        """Test handling when rollup map file is missing"""
        df = pd.DataFrame(
            {"workout_date": ["1/15/24"], "exercise_title": ["Bench Press"]}
        )

        # Only provide date map
        date_map = Path("temp_date_map.csv")

        try:
            date_map.write_text(self.sample_date_map_data)

            result = add_location_columns(df, date_map=date_map, rollup_map=None)

            # Should return original dataframe unchanged
            assert "location" not in result.columns
            assert "rollup_location" not in result.columns
            assert len(result) == 1
            assert result.iloc[0]["exercise_title"] == "Bench Press"

        finally:
            if date_map.exists():
                date_map.unlink()

    def test_add_location_columns_both_files_missing(self):
        """Test handling when both mapping files are missing"""
        df = pd.DataFrame(
            {"workout_date": ["1/15/24"], "exercise_title": ["Bench Press"]}
        )

        result = add_location_columns(df, date_map=None, rollup_map=None)

        # Should return original dataframe unchanged
        assert "location" not in result.columns
        assert "rollup_location" not in result.columns
        assert len(result) == 1
        assert result.iloc[0]["exercise_title"] == "Bench Press"

    def test_add_location_columns_nonexistent_files(self):
        """Test handling when mapping files don't exist"""
        df = pd.DataFrame(
            {"workout_date": ["1/15/24"], "exercise_title": ["Bench Press"]}
        )

        nonexistent_date_map = Path("nonexistent_date_map.csv")
        nonexistent_rollup_map = Path("nonexistent_rollup_map.csv")

        result = add_location_columns(
            df, date_map=nonexistent_date_map, rollup_map=nonexistent_rollup_map
        )

        # Should return original dataframe unchanged
        assert "location" not in result.columns
        assert "rollup_location" not in result.columns
        assert len(result) == 1
        assert result.iloc[0]["exercise_title"] == "Bench Press"

    def test_add_location_columns_unmatched_dates(self):
        """Test handling of workout dates not in the mapping"""
        df = pd.DataFrame(
            {
                "workout_date": ["1/15/24", "1/18/24"],  # 1/18/24 not in mapping
                "exercise_title": ["Bench Press", "Squat"],
            }
        )

        date_map = Path("temp_date_map.csv")
        rollup_map = Path("temp_rollup_map.csv")

        try:
            date_map.write_text(self.sample_date_map_data)
            rollup_map.write_text(self.sample_rollup_data)

            result = add_location_columns(df, date_map=date_map, rollup_map=rollup_map)

            # First row should have location data
            assert result.iloc[0]["location"] == "Primary Gym"
            assert result.iloc[0]["rollup_location"] == "Primary"

            # Second row should have NaN for location data (left join)
            assert pd.isna(result.iloc[1]["location"])
            assert pd.isna(result.iloc[1]["rollup_location"])

        finally:
            if date_map.exists():
                date_map.unlink()
            if rollup_map.exists():
                rollup_map.unlink()

    def test_add_location_columns_preserves_original_data(self):
        """Test that original data is preserved"""
        df = pd.DataFrame(
            {
                "workout_date": ["1/15/24"],
                "exercise_title": ["Bench Press"],
                "sets": [3],
                "reps": [10],
            }
        )

        date_map = Path("temp_date_map.csv")
        rollup_map = Path("temp_rollup_map.csv")

        try:
            date_map.write_text(self.sample_date_map_data)
            rollup_map.write_text(self.sample_rollup_data)

            result = add_location_columns(df, date_map=date_map, rollup_map=rollup_map)

            # Original columns should be preserved
            assert "workout_date" in result.columns
            assert "exercise_title" in result.columns
            assert "sets" in result.columns
            assert "reps" in result.columns

            # Original data should be unchanged
            assert result.iloc[0]["exercise_title"] == "Bench Press"
            assert result.iloc[0]["sets"] == 3
            assert result.iloc[0]["reps"] == 10

        finally:
            if date_map.exists():
                date_map.unlink()
            if rollup_map.exists():
                rollup_map.unlink()

    def test_add_location_columns_empty_dataframe(self):
        """Test handling of empty dataframe"""
        df = pd.DataFrame(columns=["workout_date"])

        date_map = Path("temp_date_map.csv")
        rollup_map = Path("temp_rollup_map.csv")

        try:
            date_map.write_text(self.sample_date_map_data)
            rollup_map.write_text(self.sample_rollup_data)

            result = add_location_columns(df, date_map=date_map, rollup_map=rollup_map)

            assert "location" in result.columns
            assert "rollup_location" in result.columns
            assert len(result) == 0

        finally:
            if date_map.exists():
                date_map.unlink()
            if rollup_map.exists():
                rollup_map.unlink()

    def test_add_location_columns_malformed_csv(self):
        """Test handling of malformed CSV files"""
        df = pd.DataFrame(
            {"workout_date": ["1/15/24"], "exercise_title": ["Bench Press"]}
        )

        # Create malformed CSV (missing required columns)
        malformed_date_map = Path("temp_malformed_date_map.csv")
        rollup_map = Path("temp_rollup_map.csv")

        try:
            malformed_date_map.write_text(
                "workout_date\n1/15/24"
            )  # Missing location column
            rollup_map.write_text(self.sample_rollup_data)

            # Should raise an error due to missing column
            with pytest.raises(KeyError):
                add_location_columns(
                    df, date_map=malformed_date_map, rollup_map=rollup_map
                )

        finally:
            if malformed_date_map.exists():
                malformed_date_map.unlink()
            if rollup_map.exists():
                rollup_map.unlink()
