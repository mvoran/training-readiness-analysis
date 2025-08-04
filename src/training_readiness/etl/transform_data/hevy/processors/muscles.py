# src/training_readiness/etl/transform_data/hevy/processors/muscles.py
from pathlib import Path
import json
import pandas as pd


def add_muscle_groups(
    df: pd.DataFrame,
    exercises_path: Path = Path("data/raw/hevy/hevy_exercises.json"),
    rollup_path: Path = Path(
        "src/training_readiness/resources/hevy/primary_muscle_rollup.csv"
    ),
) -> pd.DataFrame:
    templates = json.loads(exercises_path.read_text(encoding="utf-8"))

    primary_lookup = {t["title"]: t["primary_muscle_group"] for t in templates}
    secondary_lookup = {
        t["title"]: ",".join(t["secondary_muscle_groups"] or []) for t in templates
    }

    df["Primary Muscle"] = df["exercise_title"].map(primary_lookup).fillna("")
    df["Secondary Muscles"] = df["exercise_title"].map(secondary_lookup).fillna("")

    rollup = pd.read_csv(rollup_path)
    df = df.merge(
        rollup.rename(
            columns={
                "primary_muscle": "Primary Muscle",
                "primary_muscle_rollup": "primary_muscle_group",
            }
        ),
        on="Primary Muscle",
        how="left",
    )
    return df
