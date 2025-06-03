#!/usr/bin/env python3
import sys
import duckdb
from pathlib import Path

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} PATH_TO_EXCEL_FILE.xlsx")
    sys.exit(1)

excel_path = sys.argv[1]
db_path = Path(__file__).parent.parent / "training_readiness.duckdb"
sql_template_path = Path(__file__).parent / "load_trainingpeaks_data.sql"

# Read the template SQL and substitute the placeholder
sql_text = sql_template_path.read_text().replace("{{EXCEL_PATH}}", excel_path)

con = duckdb.connect(str(db_path))

# Connect to the database and execute the SQL
try:
    # Install & load the extension if not already in this DB
    con.execute("INSTALL excel;")
    con.execute("LOAD excel;")
    # Execute the filled‐in SQL
    con.execute(sql_text)
    print(f"✔ Loaded {excel_path} into {db_path}")
except duckdb.Error as e:
    print("DuckDB error:", e)
finally:
    con.close()