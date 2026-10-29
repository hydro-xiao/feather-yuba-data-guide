"""
Load an observed daily CSV (`<STATION>_daily.csv` / `<STATION>_fnf_daily.csv`)
from the newer `streamflow_obs/.../csv/` folder.

See docs/file-formats.md section 5 for the full format writeup.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_daily_csv(path: str, station: str | None = None) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
        station   (str — defaults to the filename's leading token, upper-cased)
        date      (pandas Timestamp, daily)
        value_cfs (float — the file stores KCFS; this is already x1000'd to CFS)
    """
    if station is None:
        station = Path(path).stem.split("_")[0].upper()

    df = pd.read_csv(path)
    df.columns = ["date", "value_kcfs"]
    df["date"] = pd.to_datetime(df["date"])
    df["value_cfs"] = df["value_kcfs"] * 1000.0
    df["station"] = station
    return df[["station", "date", "value_cfs"]]


if __name__ == "__main__":
    import sys

    df = load_daily_csv(sys.argv[1])
    print(df.head(10))
    print(f"\n{len(df):,} rows · {df['date'].min().date()} → "
          f"{df['date'].max().date()}")
