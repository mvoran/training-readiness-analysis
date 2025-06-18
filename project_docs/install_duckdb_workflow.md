# Runbook to Install DuckDB and Load Initial Data

Note: The runbook assumes that the project is run in Cursor on MacOS and the data structure looks something like this:

```
.
├── database
│   ├── queries
│   │   ├── clean_trainingpeaks_data.py
│   │   ├── load_trainingpeaks_data.py
│   │   └── load_trainingpeaks_data.sql
│   └── training_readiness.duckdb
├── LICENSE
├── project_docs
│   ├── install_duckdb_workflow.md
├── README.md
└── source_data
    ├── cleaned
    └── raw
        └── TrainingPeaksExport_2023_2025.xlsx
```

*To build a directory tree, run `brew install tree` from the Cursor Terminal. Once installed, you can run `tree` to build a tree in the Cursor Terminal.*

## Runbook Steps
*All steps are run from the Cursor Terminal in the project root unless otherwise specified*

1. Create Python virtual environment: `python3 -m venv .venv`.
2. Activate the virtual environment: `source .venv/bin/activate`.
3. Install pandas: `pip install pandas`.
4. Install the Python binding for DuckDB: `pip install duckdb`.
5. Install the DuckDB reader extensions for Excel and other file types: `pip install duckdb-extensions`.
6. Install the DuckDB CLI (simplifies the process for running .sql files against DuckDB): `brew install duckdb`.
7. Open the DuckDB shell and install the Excel extension:
    ```
    duckdb
    INSTALL excel;
    LOAD excel;
    .quit
    
    ```
8. Clean your data if needed before loading it into DuckDB. 
    *Note*: This tool requires standardized tracking of RPE over time to create actionable reports. Use the `clean_trainingpeaks_data.py` file as a guide to standardize your data. 
9. Create the DuckDB database and load initial data: From the `./database/queries` folder run `python3 load_trainingpeaks_data.py <path/to/data/file>`.
    1. 'Append' is the default mode for this script. To use 'Replace' mode add the `-r` flag at the end of the string, *e.g.*, `python3 load_trainingpeaks_data.py <path/to/data/file> -r`.
    2. The script accepts both .xlsx and .csv file formats.

Documentation on the DuckDB Excel extension is here: https://duckdb.org/docs/stable/core_extensions/excel.
