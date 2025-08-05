import os
import sys
import tempfile

import pytest

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.stage_data.apple_health.load_resting_hr_data import (  # noqa: E402
    extract_resting_hr_data_from_xml,
)


class TestExtractRestingHrDataFromXml:
    """Test cases for extract_resting_hr_data_from_xml function"""

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised when XML file doesn't exist"""
        with pytest.raises(FileNotFoundError, match="XML file not found"):
            extract_resting_hr_data_from_xml("nonexistent_file.xml")

    def test_empty_xml_file(self):
        """Test handling of empty XML file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><HealthData></HealthData>')
            temp_file = f.name

        try:
            result = extract_resting_hr_data_from_xml(temp_file)
            assert result == []
        finally:
            os.unlink(temp_file)

    def test_xml_with_no_resting_hr_records(self):
        """Test XML file with no resting heart rate records"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierStepCount" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="1000" unit="count"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_resting_hr_data_from_xml(temp_file)
            assert result == []
        finally:
            os.unlink(temp_file)

    def test_xml_with_valid_resting_hr_records(self):
        """Test XML file with valid resting heart rate records"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierRestingHeartRate" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="65" unit="count/min"/>
            <Record type="HKQuantityTypeIdentifierRestingHeartRate" startDate="2024-01-02 00:00:00 +0000" endDate="2024-01-02 00:00:00 +0000" value="68" unit="count/min"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_resting_hr_data_from_xml(temp_file)

            assert len(result) == 2
            assert result[0]["start_date"] == "2024-01-01 00:00:00 +0000"
            assert result[0]["end_date"] == "2024-01-01 00:00:00 +0000"
            assert result[0]["value"] == 65.0
            assert result[0]["unit"] == "count/min"

            assert result[1]["start_date"] == "2024-01-02 00:00:00 +0000"
            assert result[1]["end_date"] == "2024-01-02 00:00:00 +0000"
            assert result[1]["value"] == 68.0
            assert result[1]["unit"] == "count/min"
        finally:
            os.unlink(temp_file)

    def test_xml_with_invalid_resting_hr_records(self):
        """Test XML file with resting heart rate records missing values"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierRestingHeartRate" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" unit="count/min"/>
            <Record type="HKQuantityTypeIdentifierRestingHeartRate" startDate="2024-01-02 00:00:00 +0000" endDate="2024-01-02 00:00:00 +0000" value="68"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_resting_hr_data_from_xml(temp_file)
            # Should skip records with missing value or unit
            assert result == []
        finally:
            os.unlink(temp_file)

    def test_xml_with_mixed_record_types(self):
        """Test XML file with mixed record types including resting heart rate"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierStepCount" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="1000" unit="count"/>
            <Record type="HKQuantityTypeIdentifierRestingHeartRate" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="65" unit="count/min"/>
            <Record type="HKQuantityTypeIdentifierActiveEnergyBurned" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="500" unit="kcal"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_resting_hr_data_from_xml(temp_file)

            assert len(result) == 1
            assert result[0]["start_date"] == "2024-01-01 00:00:00 +0000"
            assert result[0]["value"] == 65.0
            assert result[0]["unit"] == "count/min"
        finally:
            os.unlink(temp_file)
