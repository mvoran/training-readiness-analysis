from pathlib import Path
import pandas as pd


def add_location_columns(
    df: pd.DataFrame,
    date_map: Path | None = None,
    rollup_map: Path | None = None,
) -> pd.DataFrame:
    if not (date_map and date_map.exists()) or not (rollup_map and rollup_map.exists()):
        # user didn’t provide both maps – skip
        return df

    df = df.merge(
        pd.read_csv(date_map)[["workout_date", "location"]],
        on="workout_date",
        how="left",
    )

    df = df.merge(pd.read_csv(rollup_map), on="location", how="left")
    return df
