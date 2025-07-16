import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import csv
import os
import argparse


def format_datetime(dt):
    """Format datetime as MM/DD/YYYY HH:MM:SS"""
    return dt.strftime("%m/%d/%Y %H:%M:%S")


def extract_sleep_data_from_xml(xml_file_path):
    """Extract sleep data from Apple Health XML export"""
    print(f"Reading Apple Health export from: {xml_file_path}")

    if not os.path.exists(xml_file_path):
        raise FileNotFoundError(f"XML file not found: {xml_file_path}")

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    sleep_data = []

    for record in root.iter("Record"):
        if record.attrib.get("type") == "HKCategoryTypeIdentifierSleepAnalysis":
            start_date = record.attrib.get("startDate")
            end_date = record.attrib.get("endDate")
            sleep_type = record.attrib.get("value")
            sleep_data.append(
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "sleep_type": sleep_type,
                }
            )

    print(f"Extracted {len(sleep_data)} sleep records from XML")
    return sleep_data


def write_debug_log(df, debug_file):
    """Write debug information to file for troubleshooting session grouping"""
    debug_file.write("Debug: Session Grouping Details\n")
    debug_file.write("==============================\n")

    current_session = 0
    session_groups = []
    last_end = None

    for idx, row in df.iterrows():
        debug_file.write(f"\nRecord {idx}:\n")
        debug_file.write(f"Start: {row['start_date']}\n")
        debug_file.write(f"End: {row['end_date']}\n")
        debug_file.write(f"Type: {row['sleep_type']}\n")
        if last_end is not None:
            debug_file.write(f"Last End: {last_end}\n")
            debug_file.write(
                f"Time diff: {(row['start_date'] - last_end).total_seconds() / 60:.2f} minutes\n"
            )

        # Start a new session if:
        # 1. This is the first record
        # 2. There's a gap between the end of the last record and start of this one
        if last_end is None or row["start_date"] > last_end:
            current_session += 1
            debug_file.write(f"Creating new session: {current_session}\n")
        else:
            debug_file.write(f"Continuing session: {current_session}\n")

        session_groups.append(current_session)
        last_end = row["end_date"]

    return session_groups


def process_sleep_data(sleep_data, debug=False):
    """Process raw sleep data into structured analysis format"""
    print("Processing sleep data...")

    # Convert to DataFrame
    df = pd.DataFrame(sleep_data)

    if df.empty:
        print("No sleep data found in XML export")
        return []

    # Filter out InBed records
    df = df[~df["sleep_type"].str.endswith("InBed")]

    # Convert date strings to datetime objects
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # Sort by start date
    df = df.sort_values("start_date")

    # Group records into sleep sessions
    if debug:
        # Open debug file for troubleshooting
        with open("sleep_debug.txt", "w") as debug_file:
            session_groups = write_debug_log(df, debug_file)
    else:
        # Simple session grouping without debug output
        current_session = 0
        session_groups = []
        last_end = None

        for _, row in df.iterrows():
            # Start a new session if:
            # 1. This is the first record
            # 2. There's a gap between the end of the last record and start of this one
            if last_end is None or row["start_date"] > last_end:
                current_session += 1

            session_groups.append(current_session)
            last_end = row["end_date"]

    df["session"] = session_groups

    # Identify sessions to exclude (those containing Unspecified sleep type)
    sessions_to_exclude = df[df["sleep_type"].str.contains("Unspecified")][
        "session"
    ].unique()

    # Process each sleep session
    output_data = []
    for session in df["session"].unique():
        # Skip sessions that contain Unspecified sleep type
        if session in sessions_to_exclude:
            continue

        session_df = df[df["session"] == session]

        # Get the earliest start and latest end time for this session
        sleep_start = session_df["start_date"].min()
        sleep_end = session_df["end_date"].max()

        # Determine sleep date (date of the earliest record)
        sleep_date = sleep_start.date()

        # Initialize sleep type totals
        total_asleep = 0
        total_deep = 0
        total_core = 0
        total_rem = 0
        total_awake = 0

        # Calculate totals for each sleep type
        for _, row in session_df.iterrows():
            duration = (
                row["end_date"] - row["start_date"]
            ).total_seconds() / 3600  # in hours

            if "Asleep" in row["sleep_type"]:
                total_asleep += duration
                if "Deep" in row["sleep_type"]:
                    total_deep += duration
                elif "Core" in row["sleep_type"]:
                    total_core += duration
                elif "REM" in row["sleep_type"]:
                    total_rem += duration
            elif "Awake" in row["sleep_type"]:
                total_awake += duration

        output_data.append(
            {
                "Sleep_Date": sleep_date.strftime("%m/%d/%Y"),
                "Total_Time_Asleep": round(total_asleep, 2),
                "Total_Deep_Sleep": round(total_deep, 2),
                "Total_Core_Sleep": round(total_core, 2),
                "Total_REM_Sleep": round(total_rem, 2),
                "Total_Awake_Time": round(total_awake, 2),
                "Sleep_Start": format_datetime(sleep_start),
                "Sleep_End": format_datetime(sleep_end),
            }
        )

    print(f"Processed {len(output_data)} sleep sessions")
    return output_data


def save_sleep_analysis(output_data, output_file="sleep_analysis.csv"):
    """Save processed sleep data to CSV file"""
    print(f"Saving sleep analysis to: {output_file}")

    fieldnames = [
        "Sleep_Date",
        "Total_Time_Asleep",
        "Total_Deep_Sleep",
        "Total_Core_Sleep",
        "Total_REM_Sleep",
        "Total_Awake_Time",
        "Sleep_Start",
        "Sleep_End",
    ]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

    print(f"Successfully saved {len(output_data)} sleep sessions to {output_file}")


def main(debug=False):
    """Main function to process Apple Health sleep data"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    xml_file = os.path.join(script_dir, "raw/apple_health_export/export.xml")

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        script_dir, f"cleaned/apple_sleep_analysis_{timestamp}.csv"
    )

    try:
        # Extract sleep data from XML
        sleep_data = extract_sleep_data_from_xml(xml_file)

        if not sleep_data:
            print("No sleep data found in the XML export")
            return

        # Process the sleep data
        output_data = process_sleep_data(sleep_data, debug=debug)

        if not output_data:
            print("No valid sleep sessions found after processing")
            return

        # Save the analysis
        save_sleep_analysis(output_data, output_file)

        print("Sleep data processing completed successfully!")

    except Exception as e:
        print(f"Error processing sleep data: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Apple Health sleep data from XML export"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to generate detailed logging",
    )
    args = parser.parse_args()

    main(debug=args.debug)
