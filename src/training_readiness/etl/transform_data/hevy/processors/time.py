import pandas as pd


def add_time_columns(df: pd.DataFrame) -> pd.DataFrame:
    dt = pd.to_datetime(df["start_time"], utc=True)
    # workout_date in m/d/yy without leading zeros
    df["workout_date"] = dt.dt.strftime("%-m/%-d/%y")
    df["day_of_week"] = dt.dt.day_name()
    return df
