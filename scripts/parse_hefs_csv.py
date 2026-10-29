"""
Load a basin HEFS ensemble CSV (`*_FeatherYuba_hefs_csv_hourly.csv`) or the
deterministic export (`*_FeatherYuba_csv_export`) — both share the same
three-header-row shape, this loader handles either.

See docs/file-formats.md sections 1 and 3 for the full format writeup.
"""
from __future__ import annotations

import pandas as pd


def load_hefs_csv(path: str) -> pd.DataFrame:
    """
    Returns a long-format DataFrame with columns:
        time       (pandas Timestamp, GMT)
        station    (str, e.g. "ORDC1")
        parameter  (str, "QINE" or "SQIN")
        member     (int, 1-based position of this column among repeats for
                    that station — NOT a calendar year. The CSV format does
                    not label ensemble members individually; for that, use
                    the per-station XML files instead (parse_pi_xml.py).
                    For the deterministic export, member is always 1.)
        value      (float, missing values -999 become NaN)
    """
    # Read the two header rows as plain text — pandas' own CSV header
    # parsing silently de-duplicates repeated names (e.g. "IIFC1" ->
    # "IIFC1.1", "IIFC1.2", ...), which would make every ensemble member
    # look like a different station.
    with open(path) as f:
        station_row = f.readline().strip().split(",")
        param_row = f.readline().strip().split(",")

    stations = station_row[1:]
    params = param_row[1:]

    df = pd.read_csv(path, skiprows=2, header=None)
    df[0] = pd.to_datetime(df[0])

    # member = running count of how many times we've seen this station so far
    seen = {}
    member_idx = []
    for s in stations:
        seen[s] = seen.get(s, 0) + 1
        member_idx.append(seen[s])

    # build long-format rows positionally — a plain melt() would collapse
    # the repeated station-name columns and lose member/parameter identity
    frames = []
    for i, (station, param, member) in enumerate(zip(stations, params, member_idx)):
        col = df[i + 1]
        frames.append(
            pd.DataFrame(
                {
                    "time": df[0],
                    "station": station,
                    "parameter": param,
                    "member": member,
                    "value": col.replace(-999, pd.NA),
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    import sys

    df = load_hefs_csv(sys.argv[1])
    print(df.head(10))
    print(f"\n{len(df):,} rows · {df['station'].nunique()} stations · "
          f"{df['member'].max()} members · "
          f"{df['time'].min()} → {df['time'].max()}")
