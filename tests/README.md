# Testing Framework

This directory contains the comprehensive test suite for the Training Readiness project. The tests are organized by type and data source to ensure proper coverage and maintainability.

## Test Structure

```
tests/
├── README.md                    # This file
├── pytest.ini                   # Pytest configuration
├── unit/                        # Unit tests
│   ├── datasources/             # Data source specific tests
│   │   └── apple_health/        # Apple Health data processing tests
│   │       ├── test_extract_resting_hr_data_from_xml.py
│   │       ├── test_process_resting_hr_data.py
│   │       ├── test_save_resting_hr_analysis.py
│   │       ├── test_extract_sleep_data_from_xml.py
│   │       ├── test_process_sleep_data.py
│   │       ├── test_save_sleep_analysis.py
│   │       └── test_format_datetime.py
│   └── ...                     # Other unit test categories
├── integration/                # Integration tests (future)
└── fixtures/                   # Test fixtures and data (future)
```

## Test Categories

### Unit Tests (`tests/unit/`)
Unit tests focus on testing individual functions and methods in isolation. They use mocking and temporary files to ensure tests are fast and reliable.

**Current Coverage:**
- **Apple Health Data Processing** (`tests/unit/datasources/apple_health/`)
  - **Resting Heart Rate Tests:**
    - `extract_resting_hr_data_from_xml()` - XML parsing and data extraction
    - `process_resting_hr_data()` - Data processing and aggregation
    - `save_resting_hr_analysis()` - CSV file output
  - **Sleep Data Tests:**
    - `extract_sleep_data_from_xml()` - XML parsing and sleep data extraction
    - `process_sleep_data()` - Sleep session processing and aggregation
    - `save_sleep_analysis()` - Sleep analysis CSV file output
  - **Utility Tests:**
    - `format_datetime()` - Date/time formatting utilities

### Integration Tests (`tests/integration/`)
Integration tests verify that different components work together correctly. These tests use real data files and database connections.

*Note: Integration tests are planned for future development.*

## Apple Health Sleep Data Tests

The Apple Health sleep data tests (`tests/unit/datasources/apple_health/`) provide comprehensive coverage for processing sleep data from Apple Health XML exports.

### Test Files Overview

#### `test_extract_sleep_data_from_xml.py`
Tests the XML parsing functionality for sleep data extraction:
- **File Not Found Handling**: Tests proper error handling when XML file doesnt exist
- **Empty XML Files**: Validates handling of empty or malformed XML content
- **Valid Sleep Records**: Tests extraction of different sleep types (InBed, Asleep, Awake, Deep, Core, REM)
- **Mixed Record Types**: Ensures only sleep records are extracted from files with multiple data types
- **Missing Attributes**: Tests graceful handling of records with missing start/end dates or sleep types
- **Different Sleep Types**: Validates extraction of all supported sleep categories

#### `test_process_sleep_data.py`
Tests the sleep data processing and aggregation logic:
- **Empty Data Handling**: Tests processing of empty datasets
- **Single Session Processing**: Validates basic sleep session aggregation
- **Multiple Sessions**: Tests handling of multiple sleep sessions across different days
- **Session Grouping**: Ensures proper grouping of sleep records into sessions with gap detection
- **Sleep Type Classification**: Tests aggregation of different sleep types (Deep, Core, REM, Awake)
- **Data Filtering**: Validates exclusion of sessions with "Unspecified sleep types
- **Value Rounding**: Tests proper decimal place rounding for time calculations
- **Date Formatting**: Ensures correct date formatting for sleep sessions
- **Session Boundaries**: Tests handling of sleep sessions crossing midnight

#### `test_save_sleep_analysis.py`
Tests the CSV output functionality for sleep analysis:
- **Empty Data Saving**: Tests saving empty datasets with proper headers
- **Single Record Output**: Validates saving of individual sleep session records
- **Multiple Records**: Tests saving multiple sleep sessions to CSV
- **Decimal Values**: Ensures proper handling of fractional time values
- **CSV Header Format**: Validates correct column headers and field names
- **File Operations**: Tests file creation, overwriting, and default filename generation
- **Data Integrity**: Ensures all sleep metrics are properly saved (Total_Time_Asleep, Deep_Sleep, Core_Sleep, REM_Sleep, Awake_Time)

### Sleep Data Metrics Tested

The tests validate the following sleep metrics:
- **Total_Time_Asleep**: Total sleep duration excluding awake time
- **Total_Deep_Sleep**: Deep sleep duration (HKCategoryValueSleepAnalysisAsleepDeep)
- **Total_Core_Sleep**: Core sleep duration (HKCategoryValueSleepAnalysisAsleepCore)
- **Total_REM_Sleep**: REM sleep duration (HKCategoryValueSleepAnalysisAsleepREM)
- **Total_Awake_Time**: Awake time during sleep sessions (HKCategoryValueSleepAnalysisAwake)
- **Sleep_Start/Sleep_End**: Session start and end timestamps
- **Sleep_Date**: Date of the sleep session

### Running Sleep Data Tests

```bash
# Run all Apple Health sleep tests
pytest tests/unit/datasources/apple_health/test_extract_sleep_data_from_xml.py
pytest tests/unit/datasources/apple_health/test_process_sleep_data.py
pytest tests/unit/datasources/apple_health/test_save_sleep_analysis.py

# Run specific sleep test categories
pytest tests/unit/datasources/apple_health/ -k "sleep"

# Run with verbose output for detailed test information
pytest tests/unit/datasources/apple_health/ -v -k "sleep"
```

## Running Tests

### Prerequisites
Ensure you have the test dependencies installed:
```bash
pip install -e ".[dev]"
```

### Basic Test Execution
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/training_readiness --cov-report=html
```

### Running Specific Tests
```bash
# Run all Apple Health tests
pytest tests/unit/datasources/apple_health/

# Run specific test file
pytest tests/unit/datasources/apple_health/test_extract_resting_hr_data_from_xml.py

# Run specific test class
pytest tests/unit/datasources/apple_health/test_process_resting_hr_data.py::TestProcessRestingHrData

# Run specific test method
pytest tests/unit/datasources/apple_health/test_process_resting_hr_data.py::TestProcessRestingHrData::test_multiple_days

# Run sleep data specific tests
pytest tests/unit/datasources/apple_health/test_extract_sleep_data_from_xml.py
pytest tests/unit/datasources/apple_health/test_process_sleep_data.py::TestProcessSleepData
pytest tests/unit/datasources/apple_health/test_save_sleep_analysis.py::TestSaveSleepAnalysis::test_save_multiple_records
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run slow tests
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Test Configuration

### pytest.ini
The `pytest.ini` file configures the test framework with:
- Test discovery patterns
- Output formatting
- Warning filters
- Custom markers

### Test Dependencies
Tests use the following key dependencies:
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **tempfile** - Temporary file creation
- **unittest.mock** - Mocking and patching

## Writing Tests

### Test Naming Convention
- **Files**: `test_<function_name>.py`
- **Classes**: `Test<ClassName>`
- **Methods**: `test_<description>`

### Test Structure
```python
import pytest
from your_module import your_function

class TestYourFunction:
    """Test cases for your_function"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        # Arrange
        input_data = "test"

        # Act
        result = your_function(input_data)

        # Assert
        assert result == "expected"

    def test_edge_case(self):
        """Test edge case handling"""
        # Test edge cases like empty input, invalid data, etc.
        pass
```

### Best Practices
1. **Isolation** - Each test should be independent
2. **Descriptive Names** - Test names should clearly describe what they test
3. **Documentation** - Use docstrings to explain test purpose
4. **Temporary Files** - Use `tempfile` for file-based tests
5. **Mocking** - Mock external dependencies and file I/O
6. **Coverage** - Aim for high test coverage of business logic

## Test Data

### Temporary Files
Tests use temporary files to avoid polluting the filesystem:
```python
import tempfile
import os

def test_file_operation():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name

    try:
        # Test with temp_file
        pass
    finally:
        os.unlink(temp_file)  # Clean up
```

### Mock Data
Use realistic but minimal test data:
```python
test_data = [{
    'start_date': '2024-01-01 08:00:00 +0000',
    'end_date': '2024-01-01 08:00:00 +0000',
    'value': 65.0,
    'unit': 'count/min'
}]
```

## Coverage Reports

Generate coverage reports to identify untested code:
```bash
# Generate HTML coverage report
pytest --cov=src/training_readiness --cov-report=html

# View coverage in terminal
pytest --cov=src/training_readiness --cov-report=term-missing
```

The HTML report will be generated in `htmlcov/index.html`.

## Continuous Integration

Tests are designed to run in CI/CD pipelines:
- Fast execution (< 30 seconds for full suite)
- No external dependencies
- Clear pass/fail results
- Coverage reporting

## Troubleshooting

### Common Issues

**Import Errors**
- Ensure you're running tests from the project root
- Check that `src/` is in the Python path
- Verify virtual environment is activated

**File Path Issues**
- Tests use relative paths from the project root
- Use `os.path.join()` for cross-platform compatibility
- Check file permissions for temporary files

**Test Failures**
- Read the test output carefully for specific error messages
- Check that test data matches expected format
- Verify that mocked functions are called correctly

### Debugging Tests
```bash
# Run tests with debug output
pytest -v -s

# Run single test with debugger
pytest tests/unit/datasources/apple_health/test_process_resting_hr_data.py::TestProcessRestingHrData::test_multiple_days -s
```

## Contributing

When adding new functionality:
1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve coverage
4. Update this README if adding new test categories

## Future Enhancements

- Integration tests for database operations
- Performance tests for large datasets
- End-to-end tests for complete workflows
- Test fixtures for common data scenarios
- Automated test data generation
