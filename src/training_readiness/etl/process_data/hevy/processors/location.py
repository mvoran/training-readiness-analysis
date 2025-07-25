"""
Add location-related columns to the DataFrame based on optional mapping files.

Args:
    df (pd.DataFrame): Input DataFrame containing at least 'workout_date' and 'workout_name' columns.
    date_map (Path | None): Optional path to CSV mapping 'workout_date' to 'location'.
    rollup_map (Path | None): Optional path to CSV with location roll-up information.

Returns:
    pd.DataFrame: DataFrame enriched with location and roll-up columns.

Behavior:
    - If neither date_map nor rollup_map exists, returns df unchanged.
    - If date_map exists, merges location info on 'workout_date'.
    - If rollup_map exists:
        - Loads rollup data and extracts canonical locations.
        - For rows missing 'location' or with null 'location', attempts to infer location by searching
            'workout_name' for any canonical location string (case-insensitive), preferring longer matches.
        - Merges rollup info on 'location' to add roll-up columns.
"""

from pathlib import Path
import pandas as pd


def add_location_columns(
    df: pd.DataFrame,
    date_map: Path | None = None,
    rollup_map: Path | None = None,
) -> pd.DataFrame:

    if not (date_map and date_map.exists()) and not (
        rollup_map and rollup_map.exists()
    ):
        return df

    if date_map and date_map.exists():
        df = df.merge(
            pd.read_csv(date_map)[["workout_date", "location"]],
            on="workout_date",
            how="left",
        )

    if rollup_map and rollup_map.exists():
        rollup_df = pd.read_csv(rollup_map)
        canonical_locations = rollup_df["location"].dropna().unique()
        canonical_locations_list: list[str] = [str(x) for x in canonical_locations]
        # Sort locations by length descending to prefer most specific matches
        canonical_locations_list = sorted(
            canonical_locations_list, key=len, reverse=True
        )

        if "location" not in df.columns:
            df["location"] = pd.NA

        missing_loc_mask = df["location"].isna()

        def infer_location(workout_name: str) -> str | None:
            if not isinstance(workout_name, str):
                return None
            workout_name_lower = workout_name.lower()
            for loc_str in canonical_locations_list:
                if loc_str.lower() in workout_name_lower:
                    return loc_str
            return None

        df.loc[missing_loc_mask, "location"] = df.loc[
            missing_loc_mask, "workout_name"
        ].apply(infer_location)

        df = df.merge(rollup_df, on="location", how="left")

    return df
