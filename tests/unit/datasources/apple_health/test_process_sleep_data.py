import os
import sys
from unittest.mock import MagicMock

import pytest

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.stage_data.apple_health.load_sleep_data import (  # noqa: E402
    process_sleep_data,
)


class TestProcessSleepData:
    """Test cases for process_sleep_data function"""

    def test_empty_data(self):
        """Test processing empty data"""
        result = process_sleep_data([])
        assert result == []

    def test_single_session_single_record(self):
        """Test processing single record for one sleep session"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert result[0]["Total_Time_Asleep"] == 7.0  # 7 hours
        assert result[0]["Total_Deep_Sleep"] == 0.0
        assert result[0]["Total_Core_Sleep"] == 0.0
        assert result[0]["Total_REM_Sleep"] == 0.0
        assert result[0]["Total_Awake_Time"] == 0.0

    def test_multiple_sessions(self):
        """Test processing multiple sleep sessions"""
        input_data = [
            # Session 1: Jan 1
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
            # Session 2: Jan 2
            {
                "start_date": "2024-01-02 22:00:00 +0000",
                "end_date": "2024-01-02 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-02 23:00:00 +0000",
                "end_date": "2024-01-03 07:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 2
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert result[0]["Total_Time_Asleep"] == 7.0
        assert result[1]["Sleep_Date"] == "01/02/2024"
        assert result[1]["Total_Time_Asleep"] == 8.0

    def test_session_grouping_with_gaps(self):
        """Test that records with gaps are grouped into separate sessions"""
        input_data = [
            # Session 1: Jan 1
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
            # Gap of 2 hours - should start new session
            {
                "start_date": "2024-01-02 08:00:00 +0000",
                "end_date": "2024-01-02 10:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 2
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert result[0]["Total_Time_Asleep"] == 7.0
        assert result[1]["Sleep_Date"] == "01/02/2024"
        assert result[1]["Total_Time_Asleep"] == 2.0

    def test_different_sleep_types(self):
        """Test processing different sleep types (Deep, Core, REM, Awake)"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 01:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleepDeep",
            },
            {
                "start_date": "2024-01-02 01:00:00 +0000",
                "end_date": "2024-01-02 03:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleepCore",
            },
            {
                "start_date": "2024-01-02 03:00:00 +0000",
                "end_date": "2024-01-02 04:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleepREM",
            },
            {
                "start_date": "2024-01-02 04:00:00 +0000",
                "end_date": "2024-01-02 05:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAwake",
            },
            {
                "start_date": "2024-01-02 05:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert (
            result[0]["Total_Time_Asleep"] == 6.0
        )  # 2+2+1+1 hours (InBed filtered out)
        assert result[0]["Total_Deep_Sleep"] == 2.0
        assert result[0]["Total_Core_Sleep"] == 2.0
        assert result[0]["Total_REM_Sleep"] == 1.0
        assert result[0]["Total_Awake_Time"] == 1.0

    def test_exclude_unspecified_sleep_sessions(self):
        """Test that sessions containing Unspecified sleep type are excluded"""
        input_data = [
            # Session 1: Valid session
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
            # Session 2: Contains Unspecified - should be excluded
            {
                "start_date": "2024-01-02 22:00:00 +0000",
                "end_date": "2024-01-02 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-02 23:00:00 +0000",
                "end_date": "2024-01-03 02:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleepUnspecified",
            },
            {
                "start_date": "2024-01-03 02:00:00 +0000",
                "end_date": "2024-01-03 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1  # Only the first session should be included
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert result[0]["Total_Time_Asleep"] == 7.0

    def test_value_rounding(self):
        """Test that values are rounded to 2 decimal places"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:30:00 +0000",  # 7.5 hours
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        assert result[0]["Total_Time_Asleep"] == 7.5

    def test_debug_mode(self):
        """Test that debug mode creates debug file"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        # Mock the file writing to avoid creating actual debug files
        with pytest.MonkeyPatch().context() as m:
            mock_file = MagicMock()
            mock_file.__enter__.return_value = mock_file
            mock_file.__exit__.return_value = None
            m.setattr("builtins.open", lambda *args, **kwargs: mock_file)
            result = process_sleep_data(input_data, debug=True)

        assert len(result) == 1
        assert result[0]["Sleep_Date"] == "01/01/2024"
        assert result[0]["Total_Time_Asleep"] == 7.0

    def test_date_formatting(self):
        """Test that dates are formatted correctly"""
        input_data = [
            {
                "start_date": "2024-12-25 22:00:00 +0000",
                "end_date": "2024-12-25 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-12-25 23:00:00 +0000",
                "end_date": "2024-12-26 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        assert result[0]["Sleep_Date"] == "12/25/2024"  # MM/DD/YYYY format

    def test_filter_inbed_records(self):
        """Test that InBed records are filtered out"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        assert result[0]["Total_Time_Asleep"] == 7.0
        # InBed time should not be counted in any sleep metrics
        assert result[0]["Total_Awake_Time"] == 0.0

    def test_session_boundary_crossing_midnight(self):
        """Test session that crosses midnight boundary"""
        input_data = [
            {
                "start_date": "2024-01-01 22:00:00 +0000",
                "end_date": "2024-01-01 23:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisInBed",
            },
            {
                "start_date": "2024-01-01 23:00:00 +0000",
                "end_date": "2024-01-02 06:00:00 +0000",
                "sleep_type": "HKCategoryValueSleepAnalysisAsleep",
            },
        ]

        result = process_sleep_data(input_data)

        assert len(result) == 1
        # Should use the date of the earliest record (Jan 1)
        assert result[0]["Sleep_Date"] == "01/01/2024"
        # Sleep start should be the earliest start time after filtering InBed records
        assert result[0]["Sleep_Start"] == "01/01/2024 23:00:00"
        assert result[0]["Sleep_End"] == "01/02/2024 06:00:00"
