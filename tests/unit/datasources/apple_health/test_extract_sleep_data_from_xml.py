import os
import sys
import tempfile

import pytest

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../src"))

from training_readiness.etl.transform_data.apple_health.process_sleep_data import (  # noqa: E402
    extract_sleep_data_from_xml,
)


class TestExtractSleepDataFromXml:
    """Test cases for extract_sleep_data_from_xml function"""

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised when XML file doesn't exist"""
        with pytest.raises(FileNotFoundError, match="XML file not found"):
            extract_sleep_data_from_xml("nonexistent_file.xml")

    def test_empty_xml_file(self):
        """Test handling of empty XML file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?><HealthData></HealthData>')
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)
            assert result == []
        finally:
            os.unlink(temp_file)

    def test_xml_with_no_sleep_records(self):
        """Test XML file with no sleep records"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierStepCount" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="1000" unit="count"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)
            assert result == []
        finally:
            os.unlink(temp_file)

    def test_xml_with_valid_sleep_records(self):
        """Test XML file with valid sleep records"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 22:00:00 +0000" endDate="2024-01-01 23:00:00 +0000" value="HKCategoryValueSleepAnalysisInBed"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 23:00:00 +0000" endDate="2024-01-02 02:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-02 02:00:00 +0000" endDate="2024-01-02 06:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)

            assert len(result) == 3
            assert result[0]["start_date"] == "2024-01-01 22:00:00 +0000"
            assert result[0]["end_date"] == "2024-01-01 23:00:00 +0000"
            assert result[0]["sleep_type"] == "HKCategoryValueSleepAnalysisInBed"

            assert result[1]["start_date"] == "2024-01-01 23:00:00 +0000"
            assert result[1]["end_date"] == "2024-01-02 02:00:00 +0000"
            assert result[1]["sleep_type"] == "HKCategoryValueSleepAnalysisAsleep"

            assert result[2]["start_date"] == "2024-01-02 02:00:00 +0000"
            assert result[2]["end_date"] == "2024-01-02 06:00:00 +0000"
            assert result[2]["sleep_type"] == "HKCategoryValueSleepAnalysisAsleep"
        finally:
            os.unlink(temp_file)

    def test_xml_with_different_sleep_types(self):
        """Test XML file with different sleep types"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 22:00:00 +0000" endDate="2024-01-01 23:00:00 +0000" value="HKCategoryValueSleepAnalysisInBed"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 23:00:00 +0000" endDate="2024-01-02 01:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-02 01:00:00 +0000" endDate="2024-01-02 02:00:00 +0000" value="HKCategoryValueSleepAnalysisAwake"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-02 02:00:00 +0000" endDate="2024-01-02 04:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)

            assert len(result) == 4
            sleep_types = [record["sleep_type"] for record in result]
            assert "HKCategoryValueSleepAnalysisInBed" in sleep_types
            assert "HKCategoryValueSleepAnalysisAsleep" in sleep_types
            assert "HKCategoryValueSleepAnalysisAwake" in sleep_types
        finally:
            os.unlink(temp_file)

    def test_xml_with_mixed_record_types(self):
        """Test XML file with mixed record types including sleep"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKQuantityTypeIdentifierStepCount" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="1000" unit="count"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 22:00:00 +0000" endDate="2024-01-01 23:00:00 +0000" value="HKCategoryValueSleepAnalysisInBed"/>
            <Record type="HKQuantityTypeIdentifierActiveEnergyBurned" startDate="2024-01-01 00:00:00 +0000" endDate="2024-01-01 00:00:00 +0000" value="500" unit="kcal"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 23:00:00 +0000" endDate="2024-01-02 06:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)

            assert len(result) == 2
            # Should only extract sleep records, ignore other types
            sleep_types = [record["sleep_type"] for record in result]
            assert "HKCategoryValueSleepAnalysisInBed" in sleep_types
            assert "HKCategoryValueSleepAnalysisAsleep" in sleep_types
        finally:
            os.unlink(temp_file)

    def test_xml_with_missing_attributes(self):
        """Test XML file with sleep records missing attributes"""
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
        <HealthData>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 22:00:00 +0000" endDate="2024-01-01 23:00:00 +0000"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" startDate="2024-01-01 23:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
            <Record type="HKCategoryTypeIdentifierSleepAnalysis" endDate="2024-01-02 06:00:00 +0000" value="HKCategoryValueSleepAnalysisAsleep"/>
        </HealthData>"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as f:
            f.write(xml_content)
            temp_file = f.name

        try:
            result = extract_sleep_data_from_xml(temp_file)
            # Should handle missing attributes gracefully
            assert len(result) == 3
            # Records with missing attributes should have None values
            assert result[0]["sleep_type"] is None
            assert result[1]["end_date"] is None
            assert result[2]["start_date"] is None
        finally:
            os.unlink(temp_file)
