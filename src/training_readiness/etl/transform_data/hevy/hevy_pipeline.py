# src/training_readiness/etl/transform_data/hevy/pipeline.py
from pathlib import Path
import pandas as pd
from .processors import time, muscles, location


def transform(
    df: pd.DataFrame,
    *,
    exercises_path: Path = Path("data/raw_data/hevy/hevy_exercises.json"),
    date_map: Path | None = None,
    rollup_map: Path | None = None,
) -> pd.DataFrame:
    df = time.add_time_columns(df)
    df = muscles.add_muscle_groups(df, exercises_path=exercises_path)
    df = location.add_location_columns(df, date_map=date_map, rollup_map=rollup_map)
    return df
