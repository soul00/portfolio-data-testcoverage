"""Download the IMDB dataset and store a snapshot as parquet."""

import argparse
from pathlib import Path

import pandas as pd
from datasets import load_dataset


def fetch_imdb(split: str = "train") -> pd.DataFrame:
    return load_dataset("stanfordnlp/imdb", split=split).to_pandas()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="train")
    parser.add_argument("--out", default="data/imdb.parquet")
    args = parser.parse_args()

    df = fetch_imdb(args.split)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"{len(df)} rows -> {out}")


if __name__ == "__main__":
    main()
