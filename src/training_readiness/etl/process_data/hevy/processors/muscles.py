import pandas as pd
from importlib.resources import files

DATA_DIR = files("training_readiness.resources.hevy")  # see §3


def add_muscle_groups(df: pd.DataFrame) -> pd.DataFrame:
    rollup = pd.read_csv(DATA_DIR / "primary_muscle_rollup.csv")

    # lookup from exercise title → primary / secondary muscles
    templates = pd.read_json(DATA_DIR / "hevy_exercises.json")
    lookup = templates.set_index("title")[
        ["primary_muscle_group", "secondary_muscle_groups"]
    ]

    df = df.join(lookup, on="exercise_title")

    # explode list → comma-separated string
    df["Secondary Muscles"] = df["secondary_muscle_groups"].apply(
        lambda x: ",".join(x or [])
    )
    df = df.drop(columns="secondary_muscle_groups")

    # map roll-ups
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
