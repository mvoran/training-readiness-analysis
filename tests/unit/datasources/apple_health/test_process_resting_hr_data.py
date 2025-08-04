import os
import sys
from unittest.mock import MagicMock

import pytest

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.load_data.apple_health.load_resting_hr_data import (  # noqa: E402
    process_resting_hr_data,
)


class TestProcessRestingHrData:
    """Test cases for process_resting_hr_data function"""

    def test_empty_data(self):
        """Test processing empty data"""
        result = process_resting_hr_data([])
        assert result == []

    def test_single_day_single_record(self):
        """Test processing single record for one day"""
        input_data = [
            {
                "start_date": "2024-01-01 08:00:00 +0000",
                "end_date": "2024-01-01 08:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            }
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 1
        assert result[0]["Resting_HR_Date"] == "01/01/2024"
        assert result[0]["Resting_HR_Value"] == 65.0

    def test_single_day_multiple_records(self):
        """Test processing multiple records for one day - should take the last one"""
        input_data = [
            {
                "start_date": "2024-01-01 08:00:00 +0000",
                "end_date": "2024-01-01 08:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            },
            {
                "start_date": "2024-01-01 20:00:00 +0000",
                "end_date": "2024-01-01 20:00:00 +0000",
                "value": 68.0,
                "unit": "count/min",
            },
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 1
        assert result[0]["Resting_HR_Date"] == "01/01/2024"
        assert result[0]["Resting_HR_Value"] == 68.0  # Should take the later record

    def test_multiple_days(self):
        """Test processing records for multiple days"""
        input_data = [
            {
                "start_date": "2024-01-01 08:00:00 +0000",
                "end_date": "2024-01-01 08:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            },
            {
                "start_date": "2024-01-02 08:00:00 +0000",
                "end_date": "2024-01-02 08:00:00 +0000",
                "value": 68.0,
                "unit": "count/min",
            },
            {
                "start_date": "2024-01-03 08:00:00 +0000",
                "end_date": "2024-01-03 08:00:00 +0000",
                "value": 62.0,
                "unit": "count/min",
            },
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 3
        assert result[0]["Resting_HR_Date"] == "01/01/2024"
        assert result[0]["Resting_HR_Value"] == 65.0
        assert result[1]["Resting_HR_Date"] == "01/02/2024"
        assert result[1]["Resting_HR_Value"] == 68.0
        assert result[2]["Resting_HR_Date"] == "01/03/2024"
        assert result[2]["Resting_HR_Value"] == 62.0

    def test_multiple_records_per_day_takes_latest(self):
        """Test that when multiple records exist for a day, it takes the latest one"""
        input_data = [
            {
                "start_date": "2024-01-01 06:00:00 +0000",
                "end_date": "2024-01-01 06:00:00 +0000",
                "value": 70.0,
                "unit": "count/min",
            },
            {
                "start_date": "2024-01-01 12:00:00 +0000",
                "end_date": "2024-01-01 12:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            },
            {
                "start_date": "2024-01-01 18:00:00 +0000",
                "end_date": "2024-01-01 18:00:00 +0000",
                "value": 68.0,
                "unit": "count/min",
            },
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 1
        assert result[0]["Resting_HR_Date"] == "01/01/2024"
        assert result[0]["Resting_HR_Value"] == 68.0  # Should take the latest (18:00)

    def test_value_rounding(self):
        """Test that values are rounded to 1 decimal place"""
        input_data = [
            {
                "start_date": "2024-01-01 08:00:00 +0000",
                "end_date": "2024-01-01 08:00:00 +0000",
                "value": 65.123456,
                "unit": "count/min",
            }
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 1
        assert result[0]["Resting_HR_Value"] == 65.1

    def test_debug_mode(self):
        """Test that debug mode creates debug file"""
        input_data = [
            {
                "start_date": "2024-01-01 08:00:00 +0000",
                "end_date": "2024-01-01 08:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            }
        ]

        # Mock the file writing to avoid creating actual debug files
        with pytest.MonkeyPatch().context() as m:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            m.setattr("builtins.open", lambda *args, **kwargs: mock_file)
            result = process_resting_hr_data(input_data, debug=True)

        assert len(result) == 1
        assert result[0]["Resting_HR_Date"] == "01/01/2024"
        assert result[0]["Resting_HR_Value"] == 65.0

    def test_date_formatting(self):
        """Test that dates are formatted correctly"""
        input_data = [
            {
                "start_date": "2024-12-25 08:00:00 +0000",
                "end_date": "2024-12-25 08:00:00 +0000",
                "value": 65.0,
                "unit": "count/min",
            }
        ]

        result = process_resting_hr_data(input_data)

        assert len(result) == 1
        assert result[0]["Resting_HR_Date"] == "12/25/2024"  # MM/DD/YYYY format
