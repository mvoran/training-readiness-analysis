from pathlib import Path
import pandas as pd

from .processors import time, muscles, location


def transform(
    df: pd.DataFrame,
    *,
    date_map: Path | None = None,
    rollup_map: Path | None = None,
) -> pd.DataFrame:
    df = time.add_time_columns(df)  # required
    df = muscles.add_muscle_groups(df)  # required
    df = location.add_location_columns(  # optional
        df,
        date_map=date_map,
        rollup_map=rollup_map,
    )
    return df
