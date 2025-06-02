# Runbook to Install DuckDB and Load Initial Data #

Note: The runbook assumes that the project is run in Cursor on MacOS and the data structure looks like this:

```
.
├── database
│   ├── queries
│   │   └── create_duckdb.sql
│   └── training_readiness.duckbb
├── project_docs
│   ├── install_duckdb_workflow.md
├── README.md
└── source_data
    └── TrainingPeaksExport_2023_2025.xlsx
```

*To build the tree, run `brew install tree` from the Cursor Terminal. Once installed, you can run `tree` to build the tree in the Cursor Terminal.*

## Runbook Steps ##
*All steps are run from the Cursor Terminal in the project root unless otherwise specified*

1. Create Python virtual environment: `python3 -m venv .venv`.
2. Activate the virtual environment: `source .venv/bin/activate`.
3. Install pandas: `pip install pandas`.
4. Install DuckDB: `pip install duckdb`.
5. Install the DuckDB extensions for Excel and other file types: `pip install duckdb-extensions`.
6. Install the DuckDB CLI (simplifies the process for running .sql files against DuckDB): `brew install duckdb`.
7. Run duckdb to install the Excel extension: `duckdb` to open the DuckDB CLI, then `INSTALL excel;`.
8. Load the Excel extension: `LOAD excel;`.
9. Create the DuckDB database and load the sample data: From the `./database/queries` folder run `duckdb ../training_readiness.duckdb -f create_duckdb.sql`.

Documentation on the DuckDB Excel extension is here: https://duckdb.org/docs/stable/core_extensions/excel.
