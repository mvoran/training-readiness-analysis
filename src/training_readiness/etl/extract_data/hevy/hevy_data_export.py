"""
hevy_data_export.py

Exports Hevy workout and exercise data using the Hevy API.
- Loads API key from project root .env (HEVY_API_KEY)
- Exports exercises to hevy_exercises.json
- Exports workouts to hevy_workouts.csv
- No downstream processing, just raw export
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import requests
import pandas as pd
from config import get_timezone_offset_hours

# Load .env from project root
project_root = Path(__file__).resolve().parents[4]
load_dotenv(project_root / ".env")


def load_api_key() -> str:
    """Load Hevy API key from environment variable HEVY_API_KEY."""
    api_key = os.getenv("HEVY_API_KEY")
    if not api_key:
        raise ValueError("HEVY_API_KEY not found in environment variables")
    return api_key


def fetch_hevy_exercises() -> List[Dict[str, Any]]:
    """Fetch exercise templates from Hevy API."""
    api_key = load_api_key()
    base_url = "https://api.hevyapp.com/v1/exercise_templates"
    headers = {"Accept": "application/json", "api-key": api_key}
    all_exercises = []
    page = 1
    per_page = 10
    while True:
        params = {"page": page, "pageSize": per_page}
        response = requests.get(base_url, headers=headers, params=params)

        # Handle 404nd of data (common for paginated APIs)
        if response.status_code == 404:
            print(f"Reached end of data at page {page}")
            break

        response.raise_for_status()
        data = response.json()
        exercises = data.get("exercise_templates", [])
        if not exercises:
            break
        all_exercises.extend(exercises)
        if len(exercises) < per_page:
            break
        page += 1
    return all_exercises


def fetch_hevy_workouts() -> Optional[pd.DataFrame]:
    """Fetch workout data from Hevy API and return as DataFrame."""
    api_key = load_api_key()
    base_url = "https://api.hevyapp.com/v1/workouts"
    headers = {"Accept": "application/json", "api-key": api_key}
    all_workouts = []
    page = 1
    per_page = 10
    while True:
        params = {"page": page, "pageSize": per_page}
        response = requests.get(base_url, headers=headers, params=params)

        # Handle 404 error for end of data (common for paginated APIs)
        if response.status_code == 404:
            print(f"Reached end of data at page {page}")
            break

        response.raise_for_status()
        data = response.json()
        workouts = data.get("workouts", [])
        if not workouts:
            break
        for workout in workouts:
            workout_id = workout["id"]
            workout_title = workout["title"]
            workout_description = workout["description"]
            start_time_utc = pd.to_datetime(workout["start_time"])
            end_time_utc = pd.to_datetime(workout["end_time"])
            offset_hours = get_timezone_offset_hours()
            start_time_local = start_time_utc - pd.Timedelta(hours=offset_hours)
            end_time_local = end_time_utc - pd.Timedelta(hours=offset_hours)
            for exercise in workout["exercises"]:
                exercise_data = {
                    "workout_id": workout_id,
                    "title": workout_title,
                    "description": workout_description,
                    "start_time": start_time_local.strftime("%Y-%m-%dT%H:%M:%S"),
                    "end_time": end_time_local.strftime("%Y-%m-%dT%H:%M:%S"),
                    "exercise_title": exercise["title"],
                    "exercise_notes": exercise["notes"],
                    "exercise_template_id": exercise["exercise_template_id"],
                    "superset_id": exercise.get("supersets_id", 0),
                    "set_index": exercise["index"],
                }
                for set_data in exercise["sets"]:
                    set_row = exercise_data.copy()
                    set_row.update(
                        {
                            "set_index": set_data["index"],
                            "set_type": set_data["type"],
                            "weight_lbs": (
                                set_data["weight_kg"] * 2.20462
                                if set_data["weight_kg"]
                                else None
                            ),
                            "reps": set_data["reps"],
                            "distance_miles": (
                                set_data["distance_meters"] * 0.000621371
                                if set_data["distance_meters"]
                                else None
                            ),
                            "duration_seconds": set_data["duration_seconds"],
                            "rpe": set_data["rpe"],
                        }
                    )
                    all_workouts.append(set_row)
        if len(workouts) < per_page:
            break
        page += 1
    if not all_workouts:
        return None
    return pd.DataFrame(all_workouts)


def main():
    """Export Hevy exercises and workouts to data/raw/hevy/"""
    output_dir = Path("data/raw/hevy")
    output_dir.mkdir(parents=True, exist_ok=True)
    # Export exercises
    print("Fetching Hevy exercises...")
    exercises = fetch_hevy_exercises()
    exercises_file = output_dir / "hevy_exercises.json"
    with open(exercises_file, "w", encoding="utf-8") as f:
        json.dump(exercises, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(exercises)} exercises to {exercises_file}")
    # Export workouts
    print("Fetching Hevy workouts...")
    workouts_df = fetch_hevy_workouts()
    if workouts_df is not None:
        workouts_file = output_dir / "hevy_workouts.csv"
        workouts_df.to_csv(workouts_file, index=False)
        print(f"Saved {len(workouts_df)} workout records to {workouts_file}")
    else:
        print("No workout data found.")


if __name__ == "__main__":
    main()
