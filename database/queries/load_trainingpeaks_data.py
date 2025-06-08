#!/usr/bin/env python3
import sys
import argparse
import duckdb
from pathlib import Path
import jinja2

def parse_args():
    parser = argparse.ArgumentParser(description='Load TrainingPeaks data into DuckDB')
    parser.add_argument('file_path', help='Path to the CSV or Excel file to load')
    parser.add_argument('-r', '--replace', action='store_true',
                      help='Replace existing data instead of appending')
    return parser.parse_args()

def get_file_type(file_path):
    """Determine if the file is CSV or Excel based on extension."""
    path = Path(file_path)
    if path.suffix.lower() == '.csv':
        return 'csv'
    elif path.suffix.lower() in ['.xlsx', '.xls']:
        return 'excel'
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}. Only .csv and .xlsx/.xls files are supported.")

def main():
    args = parse_args()
    file_path = args.file_path
    db_path = Path(__file__).parent.parent / "training_readiness.duckdb"
    sql_template_path = Path(__file__).parent / "load_trainingpeaks_data.sql"

    try:
        file_type = get_file_type(file_path)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Read the template SQL
    template = jinja2.Template(sql_template_path.read_text())
    
    # Render the template with our parameters
    sql_text = template.render(
        FILE_PATH=file_path,
        FILE_TYPE=file_type,
        REPLACE_MODE=args.replace
    )

    con = duckdb.connect(str(db_path))

    # Connect to the database and execute the SQL
    try:
        # Install & load the extension if needed
        if file_type == 'excel':
            con.execute("INSTALL excel;")
            con.execute("LOAD excel;")
        # Execute the filled‐in SQL
        con.execute(sql_text)
        mode = "replaced" if args.replace else "appended to"
        print(f"✔ {mode} data from {file_path} in {db_path}")
    except duckdb.Error as e:
        print("DuckDB error:", e)
        sys.exit(1)
    finally:
        con.close()

if __name__ == "__main__":
    main()