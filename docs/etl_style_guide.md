# ETL Script Style Guide

This document defines the standards and patterns for ETL (Extract, Transform, Load) scripts in the Training Readiness project.

## File Structure

### Script Organization
```
src/training_readiness/etl/
├── transform_data/
│   ├── hevy/
│   │   ├── transform_hevy_data.py
│   │   ├── hevy_pipeline.py
│   │   └── processors/
│   │       ├── time.py
│   │       ├── muscles.py
│   │       └── location.py
│   └── trainingpeaks/
│       └── process_trainingpeaks_data.py
├── load_data/
│   ├── apple_health/
│   │   ├── load_sleep_data.py
│   │   └── load_resting_hr_data.py
│   └── trainingpeaks/
│       ├── calculate_1wk_4wk_ratio_training_stress.py
│       ├── calculate_1wk_training_stress.py
│       └── calculate_48hr_training_stress.py
```

## Import Pattern

### For Standalone Scripts
Use path manipulation to import from project root, with `noqa: E402` to suppress linting errors:

```python
import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import requests
import pandas as pd

# Add the project root to the path so we can import config
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../../../"))

from config import get_timezone_offset_hours  # noqa: E402
```

**Note**: The `noqa: E402` comment suppresses the "module level import not at top of file" linting error, which is necessary when importing after path manipulation in standalone scripts.

**Important**: When Black formats imports with parentheses, place the `noqa: E402` comment on the first line of the import statement:

```python
from training_readiness.etl.transform_data.hevy.hevy_pipeline import (  # noqa: E402
    transform,
)
```

### For Module Imports
Use absolute imports when importing from other modules:

```python
from training_readiness.etl.transform_data.hevy.processors.time import add_time_columns
```

## User Notifications

### Required Notifications
All ETL scripts must provide the following notifications:

1. **File Reading**: Notify when reading input files
   ```python
   print(f"Reading {data_source} data from: {input_file}")
   ```

2. **Data Extraction**: Report number of records extracted
   ```python
   print(f"Extracted {len(data)} records from {data_source}")
   ```

3. **Processing Start**: Notify when processing begins
   ```python
   print("Processing {data_source} data...")
   ```

4. **Processing Results**: Report processing outcomes
   ```python
   print(f"Processed {len(processed_data)} records")
   ```

5. **File Saving**: Notify when saving output files
   ```python
   print(f"Saving {data_source} analysis to: {output_file}")
   ```

6. **Success Confirmation**: Confirm successful completion
   ```python
   print(f"{data_source} data processing completed successfully!")
   ```

7. **Error Handling**: Provide clear error messages
   ```python
   print(f"Error processing {data_source} data: {str(e)}")
   ```

### Notification Examples

#### Apple Health Pattern
```python
def main():
    print(f"Reading Apple Health export from: {xml_file}")
    data = extract_data(xml_file)
    print(f"Extracted {len(data)} records from XML")

    print("Processing sleep data...")
    processed_data = process_data(data)
    print(f"Processed {len(processed_data)} sleep sessions")

    print(f"Saving sleep analysis to: {output_file}")
    save_data(processed_data, output_file)
    print(f"Successfully saved {len(processed_data)} sleep sessions to {output_file}")

    print("Sleep data processing completed successfully!")
```

#### Hevy Pattern
```python
def main():
    print(f"Reading Hevy workout data from: {workout_file}")
    raw_df = pd.read_csv(workout_file)
    print(f"Extracted {len(raw_df)} workout records")

    print("Processing Hevy data...")
    final_df = transform(raw_df, exercises_path, date_map, rollup_map)
    print(f"Processed {len(final_df)} workout records")

    print(f"Saving processed Hevy data to: {output_file}")
    final_df.to_csv(output_file, index=False)
    print(f"Successfully saved {len(final_df)} workout records to {output_file}")

    print("Hevy data processing completed successfully!")
```

## Error Handling

### Required Error Handling
1. **File Not Found**: Check if input files exist
2. **Data Validation**: Validate data structure and content
3. **Processing Errors**: Catch and report processing failures
4. **Output Errors**: Handle file writing failures

### Error Handling Pattern
```python
try:
    # Processing logic
    pass
except FileNotFoundError as e:
    print(f"Error: Input file not found: {e}")
    raise
except Exception as e:
    print(f"Error processing {data_source} data: {str(e)}")
    raise
```

### Graceful Degradation Pattern
For optional features, implement graceful degradation:

```python
def process_with_optional_feature(data, optional_file=None):
    """Process data with optional feature"""
    if optional_file and optional_file.exists():
        print(f"Using optional feature: {optional_file}")
        # Process with feature
        return enhanced_data
    else:
        print("Optional feature not available - processing without it")
        # Process without feature
        return basic_data

# Usage
result = process_with_optional_feature(
    data,
    optional_file=Path("optional/mapping.csv")
)
```

**Benefits:**
- Script continues to work even when optional files are missing
- Clear user feedback about what's happening
- No hard failures for optional features

## File Paths

### Input Files
- Use relative paths from project root
- Standard locations:
  - `data/raw/{source}/` for raw data files
  - `maps/{source}/` for mapping files

### Output Files
- Use timestamped filenames to prevent overwrites
- Standard format: `{source}_{timestamp}.csv`
- Output to: `data/processed/{source}/`

### Path Construction Pattern
```python
from datetime import datetime
from pathlib import Path

# Input paths
input_file = Path("data/raw/hevy/hevy_workouts.csv")
mapping_file = Path("maps/hevy/workout_date_location.csv")

# Output paths
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = Path(f"data/processed/hevy/hevy_workouts_processed_{timestamp}.csv")
```

## Data Processing Patterns

### Pipeline Pattern (Complex Processing)
For multi-step processing, use a pipeline pattern:

```python
def transform(df, **kwargs):
    """Orchestrate data transformation pipeline"""
    df = step1_process(df)
    df = step2_process(df, **kwargs)
    df = step3_process(df, **kwargs)
    return df
```

### Direct Processing Pattern (Simple Processing)
For single-step processing:

```python
def process_data(input_data):
    """Process data in a single step"""
    # Processing logic
    return processed_data
```

## Testing Requirements

### Unit Tests
- Test each processing function in isolation
- Use mocked data and files
- Test error conditions and edge cases

### Integration Tests
- Test complete workflows with real data files
- Test file I/O operations
- Test end-to-end processing

### Real Integration Tests (Critical!)
**Always create tests that use actual data files, not just synthetic test data.**

```python
def test_with_real_data_files(self):
    """Test with actual data files to catch real-world issues"""
    # Use actual file paths, not temporary test files
    workout_file = Path("data/raw/hevy/hevy_workouts.csv")
    exercises_file = Path("data/raw/hevy/hevy_exercises.json")

    # Skip if real files don't exist
    if not workout_file.exists():
        pytest.skip("Real data files not found")

    # Process with real data
    result = transform(real_workouts, exercises_path=exercises_file)

    # Validate real-world scenarios
    assert len(result) > 0
    assert "location" in result.columns  # Catches path mismatches!
```

**Why this matters:**
- Catches file path mismatches between script expectations and actual file structure
- Validates real data formats and edge cases
- Ensures the script works with actual user data
- Prevents "works in tests, fails in production" issues

### Test File Structure
```
tests/
├── unit/
│   └── datasources/
│       ├── apple_health/
│       ├── hevy/
│       └── trainingpeaks/
└── integrations/
    └── etl/
```

## Documentation

### Required Documentation
1. **Module Docstring**: Describe the module's purpose
2. **Function Docstrings**: Document all public functions
3. **Inline Comments**: Explain complex logic
4. **README Updates**: Update relevant README files

### Documentation Pattern
```python
"""
Module Name

Brief description of what this module does.
Examples of usage and expected inputs/outputs.
"""

def process_function(data, **kwargs):
    """
    Process the given data.

    Args:
        data: Input data to process
        **kwargs: Additional processing parameters

    Returns:
        Processed data

    Raises:
        ValueError: If data is invalid
        FileNotFoundError: If required files are missing
    """
```

## Performance Considerations

### Large Files
- Use chunked processing for large datasets
- Implement progress reporting for long operations
- Consider memory usage for large dataframes

### Performance Monitoring
```python
import time

start_time = time.time()
# Processing logic
end_time = time.time()
print(f"Processing completed in {end_time - start_time:.2f} seconds")
```

## Version Control

### Commit Messages
Use descriptive commit messages:
- `feat: add Hevy data processing pipeline`
- `fix: correct timezone handling in Apple Health processing`
- `test: add comprehensive tests for Hevy processors`

### File Changes
- Update tests when changing processing logic
- Update documentation when changing interfaces
- Maintain backward compatibility when possible
