#!/usr/bin/env python3
import sys
import argparse
import duckdb
from pathlib import Path
import jinja2

def parse_args():
    parser = argparse.ArgumentParser(description='Load TrainingPeaks data into DuckDB')
    parser.add_argument('excel_path', help='Path to the Excel file to load')
    parser.add_argument('-r', '--replace', action='store_true',
                      help='Replace existing data instead of appending')
    return parser.parse_args()

def main():
    args = parse_args()
    excel_path = args.excel_path
    db_path = Path(__file__).parent.parent / "training_readiness.duckdb"
    sql_template_path = Path(__file__).parent / "load_trainingpeaks_data.sql"

    # Read the template SQL
    template = jinja2.Template(sql_template_path.read_text())
    
    # Render the template with our parameters
    sql_text = template.render(
        EXCEL_PATH=excel_path,
        REPLACE_MODE=args.replace
    )

    con = duckdb.connect(str(db_path))

    # Connect to the database and execute the SQL
    try:
        # Install & load the extension if not already in this DB
        con.execute("INSTALL excel;")
        con.execute("LOAD excel;")
        # Execute the filled‐in SQL
        con.execute(sql_text)
        mode = "replaced" if args.replace else "appended to"
        print(f"✔ {mode} data from {excel_path} in {db_path}")
    except duckdb.Error as e:
        print("DuckDB error:", e)
        sys.exit(1)
    finally:
        con.close()

if __name__ == "__main__":
    main()