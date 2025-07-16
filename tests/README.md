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
  - `extract_resting_hr_data_from_xml()` - XML parsing and data extraction
  - `process_resting_hr_data()` - Data processing and aggregation
  - `save_resting_hr_analysis()` - CSV file output
  - `format_datetime()` - Date/time formatting utilities

### Integration Tests (`tests/integration/`)
Integration tests verify that different components work together correctly. These tests use real data files and database connections.

*Note: Integration tests are planned for future development.*

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
