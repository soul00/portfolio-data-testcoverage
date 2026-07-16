"""Corrupt the dataset snapshot on purpose, to prove the dataset tests catch real issues."""

import argparse
from pathlib import Path

import pandas as pd


def corrupt(df: pd.DataFrame) -> pd.DataFrame:
    df = df.iloc[:20000].copy()  # drop rows below the minimum, skews label balance too
    duplicates = df.sample(1000, random_state=1)
    df = pd.concat([df, duplicates], ignore_index=True)  # inject duplicate rows
    df.loc[df.sample(500, random_state=2).index, "text"] = None  # inject nulls
    df["label"] = df["label"].astype("float64")  # schema drift
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", default="data/imdb.parquet")
    args = parser.parse_args()

    path = Path(args.path)
    df = corrupt(pd.read_parquet(path))
    df.to_parquet(path, index=False)
    print(f"corrupted {len(df)} rows -> {path}")


if __name__ == "__main__":
    main()
