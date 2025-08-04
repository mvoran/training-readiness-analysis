import pandas as pd
import pytest
from training_readiness.etl.transform_data.hevy.processors.time import add_time_columns


class TestTimeProcessor:
    """Test cases for time processor functionality"""

    def test_add_time_columns_basic(self):
        """Test basic time column addition"""
        # Create sample data
        df = pd.DataFrame(
            {"start_time": ["2024-01-15T10:30:00Z", "2024-12-25T14:45:00Z"]}
        )

        result = add_time_columns(df)

        # Check that new columns were added
        assert "workout_date" in result.columns
        assert "day_of_week" in result.columns

        # Check date formatting (m/d/yy without leading zeros)
        assert result.iloc[0]["workout_date"] == "1/15/24"
        assert result.iloc[1]["workout_date"] == "12/25/24"

        # Check day of week
        assert result.iloc[0]["day_of_week"] == "Monday"
        assert result.iloc[1]["day_of_week"] == "Wednesday"

    def test_add_time_columns_edge_cases(self):
        """Test edge cases for time processing"""
        # Test single digit month and day
        df = pd.DataFrame(
            {"start_time": ["2024-01-01T00:00:00Z", "2024-12-31T23:59:59Z"]}
        )

        result = add_time_columns(df)

        assert result.iloc[0]["workout_date"] == "1/1/24"
        assert result.iloc[1]["workout_date"] == "12/31/24"

    def test_add_time_columns_leap_year(self):
        """Test leap year handling"""
        df = pd.DataFrame({"start_time": ["2024-02-29T12:00:00Z"]})

        result = add_time_columns(df)

        assert result.iloc[0]["workout_date"] == "2/29/24"
        assert result.iloc[0]["day_of_week"] == "Thursday"

    def test_add_time_columns_timezone_handling(self):
        """Test that UTC timestamps are handled correctly"""
        df = pd.DataFrame(
            {"start_time": ["2024-01-15T10:30:00+00:00", "2024-01-15T10:30:00Z"]}
        )

        result = add_time_columns(df)

        # Both should produce the same result
        assert result.iloc[0]["workout_date"] == result.iloc[1]["workout_date"]
        assert result.iloc[0]["day_of_week"] == result.iloc[1]["day_of_week"]

    def test_add_time_columns_preserves_original_data(self):
        """Test that original data is preserved"""
        df = pd.DataFrame(
            {
                "start_time": ["2024-01-15T10:30:00Z"],
                "exercise_title": ["Bench Press"],
                "sets": [3],
            }
        )

        result = add_time_columns(df)

        # Original columns should be preserved
        assert "start_time" in result.columns
        assert "exercise_title" in result.columns
        assert "sets" in result.columns

        # Original data should be unchanged
        assert result.iloc[0]["exercise_title"] == "Bench Press"
        assert result.iloc[0]["sets"] == 3

    def test_add_time_columns_empty_dataframe(self):
        """Test handling of empty dataframe"""
        df = pd.DataFrame(columns=["start_time"])

        result = add_time_columns(df)

        assert "workout_date" in result.columns
        assert "day_of_week" in result.columns
        assert len(result) == 0

    def test_add_time_columns_invalid_dates(self):
        """Test handling of invalid date strings"""
        df = pd.DataFrame({"start_time": ["invalid-date", "2024-01-15T10:30:00Z"]})

        # Should raise an error for invalid dates
        with pytest.raises(Exception):
            add_time_columns(df)
