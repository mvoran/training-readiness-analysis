import os
import sys
from datetime import datetime

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.process_data.apple_health.process_resting_hr_data import (  # noqa: E402
    format_datetime,
)


class TestFormatDatetime:
    """Test cases for format_datetime function"""

    def test_basic_datetime_formatting(self):
        """Test basic datetime formatting"""
        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_datetime(dt)
        assert result == "01/15/2024 14:30:45"

    def test_single_digit_month_and_day(self):
        """Test formatting with single digit month and day"""
        dt = datetime(2024, 3, 5, 9, 5, 10)
        result = format_datetime(dt)
        assert result == "03/05/2024 09:05:10"

    def test_midnight_time(self):
        """Test formatting with midnight time"""
        dt = datetime(2024, 12, 31, 0, 0, 0)
        result = format_datetime(dt)
        assert result == "12/31/2024 00:00:00"

    def test_end_of_day_time(self):
        """Test formatting with end of day time"""
        dt = datetime(2024, 6, 15, 23, 59, 59)
        result = format_datetime(dt)
        assert result == "06/15/2024 23:59:59"

    def test_year_boundary(self):
        """Test formatting around year boundary"""
        dt = datetime(2023, 12, 31, 23, 59, 59)
        result = format_datetime(dt)
        assert result == "12/31/2023 23:59:59"

        dt = datetime(2024, 1, 1, 0, 0, 0)
        result = format_datetime(dt)
        assert result == "01/01/2024 00:00:00"

    def test_leap_year(self):
        """Test formatting with leap year date"""
        dt = datetime(2024, 2, 29, 12, 30, 0)
        result = format_datetime(dt)
        assert result == "02/29/2024 12:30:00"

    def test_consistent_format(self):
        """Test that format is consistent across different dates"""
        test_cases = [
            (datetime(2024, 1, 1, 1, 1, 1), "01/01/2024 01:01:01"),
            (datetime(2024, 12, 31, 12, 30, 45), "12/31/2024 12:30:45"),
            (datetime(2024, 6, 15, 18, 45, 30), "06/15/2024 18:45:30"),
        ]

        for dt, expected in test_cases:
            result = format_datetime(dt)
            assert (
                result == expected
            ), f"Failed for {dt}: expected {expected}, got {result}"
