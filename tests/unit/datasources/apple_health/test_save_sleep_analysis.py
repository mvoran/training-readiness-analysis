import os
import sys
import tempfile
import csv

import pytest

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.load_data.apple_health.load_sleep_data import (  # noqa: E402
    save_sleep_analysis,
)


class TestSaveSleepAnalysis:
    """Test cases for save_sleep_analysis function"""

    def test_save_empty_data(self):
        """Test saving empty data"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis([], temp_file)

            # Check that file was created and has header
            assert os.path.exists(temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                assert len(rows) == 0
        finally:
            os.unlink(temp_file)

    def test_save_single_record(self):
        """Test saving single sleep session record"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.5,
                "Total_Deep_Sleep": 2.0,
                "Total_Core_Sleep": 4.0,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.5,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/02/2024 06:00:00",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis(input_data, temp_file)

            # Check that file was created
            assert os.path.exists(temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                assert len(rows) == 1
                row = rows[0]
                assert row["Sleep_Date"] == "01/01/2024"
                assert float(row["Total_Time_Asleep"]) == 7.5
                assert float(row["Total_Deep_Sleep"]) == 2.0
                assert float(row["Total_Core_Sleep"]) == 4.0
                assert float(row["Total_REM_Sleep"]) == 1.0
                assert float(row["Total_Awake_Time"]) == 0.5
                assert row["Sleep_Start"] == "01/01/2024 22:00:00"
                assert row["Sleep_End"] == "01/02/2024 06:00:00"
        finally:
            os.unlink(temp_file)

    def test_save_multiple_records(self):
        """Test saving multiple sleep session records"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.5,
                "Total_Deep_Sleep": 2.0,
                "Total_Core_Sleep": 4.0,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.5,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/02/2024 06:00:00",
            },
            {
                "Sleep_Date": "01/02/2024",
                "Total_Time_Asleep": 8.0,
                "Total_Deep_Sleep": 2.5,
                "Total_Core_Sleep": 4.5,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.0,
                "Sleep_Start": "01/02/2024 22:30:00",
                "Sleep_End": "01/03/2024 06:30:00",
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis(input_data, temp_file)

            # Check that file was created
            assert os.path.exists(temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                assert len(rows) == 2

                # Check first record
                row1 = rows[0]
                assert row1["Sleep_Date"] == "01/01/2024"
                assert float(row1["Total_Time_Asleep"]) == 7.5

                # Check second record
                row2 = rows[1]
                assert row2["Sleep_Date"] == "01/02/2024"
                assert float(row2["Total_Time_Asleep"]) == 8.0
        finally:
            os.unlink(temp_file)

    def test_save_with_decimal_values(self):
        """Test saving records with decimal values"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.25,
                "Total_Deep_Sleep": 1.75,
                "Total_Core_Sleep": 3.5,
                "Total_REM_Sleep": 1.25,
                "Total_Awake_Time": 0.75,
                "Sleep_Start": "01/01/2024 22:15:00",
                "Sleep_End": "01/02/2024 05:30:00",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis(input_data, temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                assert len(rows) == 1
                row = rows[0]
                assert float(row["Total_Time_Asleep"]) == 7.25
                assert float(row["Total_Deep_Sleep"]) == 1.75
                assert float(row["Total_Core_Sleep"]) == 3.5
                assert float(row["Total_REM_Sleep"]) == 1.25
                assert float(row["Total_Awake_Time"]) == 0.75
        finally:
            os.unlink(temp_file)

    def test_csv_header_format(self):
        """Test that CSV header contains all expected fields"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.5,
                "Total_Deep_Sleep": 2.0,
                "Total_Core_Sleep": 4.0,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.5,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/02/2024 06:00:00",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis(input_data, temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)

                # Check that all expected fields are present
                expected_fields = [
                    "Sleep_Date",
                    "Total_Time_Asleep",
                    "Total_Deep_Sleep",
                    "Total_Core_Sleep",
                    "Total_REM_Sleep",
                    "Total_Awake_Time",
                    "Sleep_Start",
                    "Sleep_End",
                ]

                assert reader.fieldnames == expected_fields
        finally:
            os.unlink(temp_file)

    def test_default_filename(self):
        """Test that default filename is used when not specified"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.5,
                "Total_Deep_Sleep": 2.0,
                "Total_Core_Sleep": 4.0,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.5,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/02/2024 06:00:00",
            }
        ]

        # Use default filename
        save_sleep_analysis(input_data)

        # Check that default file was created
        assert os.path.exists("sleep_analysis.csv")

        # Clean up
        os.unlink("sleep_analysis.csv")

    def test_file_overwrite(self):
        """Test that existing file is overwritten"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 7.5,
                "Total_Deep_Sleep": 2.0,
                "Total_Core_Sleep": 4.0,
                "Total_REM_Sleep": 1.0,
                "Total_Awake_Time": 0.5,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/02/2024 06:00:00",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            # Create initial file with different content
            with open(temp_file, "w") as f:
                f.write("old,content\n")

            # Save new data
            save_sleep_analysis(input_data, temp_file)

            # Check that file was overwritten with new content
            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                assert len(rows) == 1
                assert rows[0]["Sleep_Date"] == "01/01/2024"
        finally:
            os.unlink(temp_file)

    def test_zero_values(self):
        """Test saving records with zero values"""
        input_data = [
            {
                "Sleep_Date": "01/01/2024",
                "Total_Time_Asleep": 0.0,
                "Total_Deep_Sleep": 0.0,
                "Total_Core_Sleep": 0.0,
                "Total_REM_Sleep": 0.0,
                "Total_Awake_Time": 0.0,
                "Sleep_Start": "01/01/2024 22:00:00",
                "Sleep_End": "01/01/2024 22:00:00",
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_sleep_analysis(input_data, temp_file)

            with open(temp_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                assert len(rows) == 1
                row = rows[0]
                assert float(row["Total_Time_Asleep"]) == 0.0
                assert float(row["Total_Deep_Sleep"]) == 0.0
                assert float(row["Total_Core_Sleep"]) == 0.0
                assert float(row["Total_REM_Sleep"]) == 0.0
                assert float(row["Total_Awake_Time"]) == 0.0
        finally:
            os.unlink(temp_file)
