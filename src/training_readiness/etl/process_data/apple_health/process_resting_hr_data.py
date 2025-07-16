import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
import csv
import os
import argparse


def format_datetime(dt):
    """Format datetime as MM/DD/YYYY HH:MM:SS"""
    return dt.strftime("%m/%d/%Y %H:%M:%S")


def extract_resting_hr_data_from_xml(xml_file_path):
    """Extract resting heart rate data from Apple Health XML export"""
    print(f"Reading Apple Health export from: {xml_file_path}")

    if not os.path.exists(xml_file_path):
        raise FileNotFoundError(f"XML file not found: {xml_file_path}")

    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    resting_hr_data = []

    for record in root.iter("Record"):
        if record.attrib.get("type") == "HKQuantityTypeIdentifierRestingHeartRate":
            start_date = record.attrib.get("startDate")
            end_date = record.attrib.get("endDate")
            value = record.attrib.get("value")
            unit = record.attrib.get("unit")

            # Only process if we have a valid value
            if value and unit:
                resting_hr_data.append(
                    {
                        "start_date": start_date,
                        "end_date": end_date,
                        "value": float(value),
                        "unit": unit,
                    }
                )

    print(f"Extracted {len(resting_hr_data)} resting heart rate records from XML")
    return resting_hr_data


def write_debug_log(df, debug_file):
    """Write debug information to file for troubleshooting data processing"""
    debug_file.write("Debug: Resting Heart Rate Processing Details\n")
    debug_file.write("===========================================\n")

    for idx, row in df.iterrows():
        debug_file.write(f"\nRecord {idx}:\n")
        debug_file.write(f"Date: {row['date']}\n")
        debug_file.write(f"Value: {row['value']} {row['unit']}\n")
        debug_file.write(f"Time: {row['start_date']}\n")

    return df


def process_resting_hr_data(resting_hr_data, debug=False):
    """Process raw resting heart rate data into structured analysis format"""
    print("Processing resting heart rate data...")

    # Convert to DataFrame
    df = pd.DataFrame(resting_hr_data)

    if df.empty:
        print("No resting heart rate data found in XML export")
        return []

    # Convert date strings to datetime objects
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    # Extract date (without time) for grouping
    df["date"] = df["start_date"].dt.date

    # Sort by start date (most recent first within each date)
    df = df.sort_values("start_date", ascending=False)

    if debug:
        # Open debug file for troubleshooting
        with open("resting_hr_debug.txt", "w") as debug_file:
            df = write_debug_log(df, debug_file)

    # Group by date and take the last entry of each day (which will be first due to descending sort)
    daily_hr_data = df.groupby("date").first().reset_index()

    # Sort by date for final output
    daily_hr_data = daily_hr_data.sort_values("date")

    # Convert to output format
    output_data = []
    for _, row in daily_hr_data.iterrows():
        output_data.append(
            {
                "Resting_HR_Date": row["date"].strftime("%m/%d/%Y"),
                "Resting_HR_Value": round(row["value"], 1),
            }
        )

    print(f"Processed {len(output_data)} daily resting heart rate records")
    return output_data


def save_resting_hr_analysis(output_data, output_file="resting_hr_analysis.csv"):
    """Save processed resting heart rate data to CSV file"""
    print(f"Saving resting heart rate analysis to: {output_file}")

    fieldnames = ["Resting_HR_Date", "Resting_HR_Value"]

    with open(output_file, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

    print(
        f"Successfully saved {len(output_data)} resting heart rate records to {output_file}"
    )


def main(debug=False):
    """Main function to process Apple Health resting heart rate data"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    xml_file = os.path.join(script_dir, "raw/apple_health_export/export.xml")

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(
        script_dir, f"cleaned/apple_resting_hr_analysis_{timestamp}.csv"
    )

    try:
        # Extract resting heart rate data from XML
        resting_hr_data = extract_resting_hr_data_from_xml(xml_file)

        if not resting_hr_data:
            print("No resting heart rate data found in the XML export")
            return

        # Process the resting heart rate data
        output_data = process_resting_hr_data(resting_hr_data, debug=debug)

        if not output_data:
            print("No valid resting heart rate records found after processing")
            return

        # Save the analysis
        save_resting_hr_analysis(output_data, output_file)

        print("Resting heart rate data processing completed successfully!")

    except Exception as e:
        print(f"Error processing resting heart rate data: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process Apple Health resting heart rate data from XML export"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode to generate detailed logging",
    )
    args = parser.parse_args()

    main(debug=args.debug)
