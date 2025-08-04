import csv
import os
import sys
import tempfile

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.transform_data.apple_health.process_resting_hr_data import (  # noqa: E402
    save_resting_hr_analysis,
)


class TestSaveRestingHrAnalysis:
    """Test cases for save_resting_hr_analysis function"""

    def test_save_empty_data(self):
        """Test saving empty data to CSV"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_resting_hr_analysis([], temp_file)

            # Check that file was created and has header
            with open(temp_file, "r") as f:
                content = f.read()
                assert "Resting_HR_Date" in content
                assert "Resting_HR_Value" in content
                # Should only have header, no data rows
                lines = content.strip().split("\n")
                assert len(lines) == 1
        finally:
            os.unlink(temp_file)

    def test_save_single_record(self):
        """Test saving single record to CSV"""
        test_data = [{"Resting_HR_Date": "01/01/2024", "Resting_HR_Value": 65.0}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_resting_hr_analysis(test_data, temp_file)

            # Read and verify the CSV content
            with open(temp_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 1
                assert rows[0]["Resting_HR_Date"] == "01/01/2024"
                assert rows[0]["Resting_HR_Value"] == "65.0"
        finally:
            os.unlink(temp_file)

    def test_save_multiple_records(self):
        """Test saving multiple records to CSV"""
        test_data = [
            {"Resting_HR_Date": "01/01/2024", "Resting_HR_Value": 65.0},
            {"Resting_HR_Date": "01/02/2024", "Resting_HR_Value": 68.0},
            {"Resting_HR_Date": "01/03/2024", "Resting_HR_Value": 62.0},
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_resting_hr_analysis(test_data, temp_file)

            # Read and verify the CSV content
            with open(temp_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 3
                assert rows[0]["Resting_HR_Date"] == "01/01/2024"
                assert rows[0]["Resting_HR_Value"] == "65.0"
                assert rows[1]["Resting_HR_Date"] == "01/02/2024"
                assert rows[1]["Resting_HR_Value"] == "68.0"
                assert rows[2]["Resting_HR_Date"] == "01/03/2024"
                assert rows[2]["Resting_HR_Value"] == "62.0"
        finally:
            os.unlink(temp_file)

    def test_save_with_decimal_values(self):
        """Test saving records with decimal values"""
        test_data = [{"Resting_HR_Date": "01/01/2024", "Resting_HR_Value": 65.5}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_resting_hr_analysis(test_data, temp_file)

            # Read and verify the CSV content
            with open(temp_file, "r") as f:
                reader = csv.DictReader(f)
                rows = list(reader)

                assert len(rows) == 1
                assert rows[0]["Resting_HR_Date"] == "01/01/2024"
                assert rows[0]["Resting_HR_Value"] == "65.5"
        finally:
            os.unlink(temp_file)

    def test_csv_header_format(self):
        """Test that CSV header is correctly formatted"""
        test_data = [{"Resting_HR_Date": "01/01/2024", "Resting_HR_Value": 65.0}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            save_resting_hr_analysis(test_data, temp_file)

            # Read and verify the header
            with open(temp_file, "r") as f:
                first_line = f.readline().strip()
                expected_header = "Resting_HR_Date,Resting_HR_Value"
                assert first_line == expected_header
        finally:
            os.unlink(temp_file)

    def test_default_filename(self):
        """Test that function works with default filename"""
        test_data = [{"Resting_HR_Date": "01/01/2024", "Resting_HR_Value": 65.0}]

        # Create a temporary directory to avoid conflicts
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                save_resting_hr_analysis(test_data)

                # Check that default file was created
                assert os.path.exists("resting_hr_analysis.csv")

                # Verify content
                with open("resting_hr_analysis.csv", "r") as f:
                    reader = csv.DictReader(f)
                    rows = list(reader)
                    assert len(rows) == 1
                    assert rows[0]["Resting_HR_Date"] == "01/01/2024"
                    assert rows[0]["Resting_HR_Value"] == "65.0"
            finally:
                os.chdir(original_cwd)
