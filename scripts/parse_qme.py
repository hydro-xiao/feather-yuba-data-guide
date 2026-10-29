"""
Load an observed QME / datacard fixed-width daily file (`*.qme`).

See docs/file-formats.md section 4 for the full format writeup — in
particular the month/year code quirk this parser has to handle (the month is
NOT zero-padded, so the code is 3 digits in January–September and 4 digits
in October–December), and the fact that the embedded station field can be a
raw USGS site number rather than the CNRFC code.
"""
from __future__ import annotations

import re
import warnings

import pandas as pd

_ROW_RE = re.compile(r"^(\S+)\s+(\d{3,4})\s+(\d{1,2})\s+(-?\d+\.\d+)")
_PERIOD_RE = re.compile(
    r"PERIOD OF RECORD\s*=\s*(\d{1,2})/(\d{2,4})\s*THRU\s*(\d{1,2})/(\d{2,4})", re.I
)
_FORMAT_LINE_RE = re.compile(r"^\s*(\d{1,2})\s+(\d{4})\s+(\d{1,2})\s+(\d{4})\s")
_MISSING_VALUES = {-999.0, -998.0}


def _read_period_of_record(path: str) -> tuple[int, int] | None:
    """
    Reads the file's own declared start/end year from its header, so a
    2-digit year embedded in a data row can be assigned to the right
    century. Checks the `PERIOD OF RECORD=` comment first, then falls back
    to the raw `MM YYYY MM YYYY` format-spec line that appears instead in
    some files.
    """
    with open(path, errors="ignore") as f:
        for _ in range(15):
            line = f.readline()
            if not line:
                break
            m = _PERIOD_RE.search(line)
            if m:
                return _expand_year(m.group(2)), _expand_year(m.group(4))
            m = _FORMAT_LINE_RE.match(line)
            if m:
                return int(m.group(2)), int(m.group(4))
    return None


def _expand_year(year_str: str) -> int:
    """`PERIOD OF RECORD=` years can be 2-digit ("10/04") or 4-digit
    ("09/2019") — expand a 2-digit one with the same pivot used elsewhere."""
    if len(year_str) == 4:
        return int(year_str)
    year2 = int(year_str)
    return 2000 + year2 if year2 <= 30 else 1900 + year2


def _resolve_year(year2: int, period: tuple[int, int] | None, anchor: int | None) -> int:
    """
    A 2-digit year is ambiguous between 19xx and 20xx. Narrow it down using,
    in order:
      1. the file's declared period of record (if only one century fits), then
      2. `anchor` — the previously resolved year, since rows are written in
         chronological order, so the right candidate is whichever one is
         closest to wherever we already are (this is what correctly
         resolves century-spanning files like a 1900-2024 record, where
         BOTH 1900 and 2000 fall inside the declared range for year2=00),
      3. a last-resort pivot (<=30 -> 2000s) if neither of the above apply
         (e.g. the very first row, with no declared period either).
    """
    candidates = (1900 + year2, 2000 + year2)
    if period is not None:
        lo, hi = period
        in_range = [y for y in candidates if lo <= y <= hi]
        if len(in_range) == 1:
            return in_range[0]
    if anchor is not None:
        return min(candidates, key=lambda y: abs(y - anchor))
    return 2000 + year2 if year2 <= 30 else 1900 + year2


def load_qme(path: str, station: str | None = None) -> pd.DataFrame:
    """
    Returns a DataFrame with columns:
        station (str — see below)
        date    (pandas Timestamp, daily)
        value   (float, CFS — -999/-998 sentinels become NaN)

    GOTCHA: the station field embedded in each data row is NOT reliable. In
    the original streamflow_obs/*.qme files it's usually the CNRFC code
    (sometimes with a trailing "F", which this loader strips). But in the
    newer datacard/*.qme files it's often the raw USGS site number instead
    (e.g. "11413000" for GYRC1) — the CNRFC code only appears in the
    filename there. Pass `station=` explicitly (e.g. derived from the
    filename, with any trailing "F" stripped) whenever the embedded value
    shouldn't be trusted.
    """
    period = _read_period_of_record(path)
    anchor = period[0] if period is not None else None

    rows = []
    skipped = 0
    with open(path, errors="ignore") as f:
        for line in f:
            if line.startswith("$"):
                continue
            m = _ROW_RE.match(line)
            if not m:
                continue
            embedded_station, code, day, value = m.groups()
            if len(code) == 4:
                month, year2 = int(code[:2]), int(code[2:])
            else:  # 3-digit code: single-digit month, no leading zero
                month, year2 = int(code[0]), int(code[1:])
            year = _resolve_year(year2, period, anchor)
            anchor = year
            try:
                date = pd.Timestamp(year=year, month=month, day=int(day))
            except ValueError:
                # A handful of files contain a calendar-impossible date
                # (e.g. a Feb 29 under a resolved non-leap year) — a real
                # anomaly in the source data, not a parsing error. Skip the
                # row rather than guessing a replacement date.
                skipped += 1
                continue
            value = float(value)
            rows.append(
                {
                    "station": station or embedded_station.rstrip("F"),
                    "date": date,
                    "value": pd.NA if value in _MISSING_VALUES else value,
                }
            )
    if skipped:
        warnings.warn(f"{path}: skipped {skipped} row(s) with an invalid calendar date")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    import sys
    from pathlib import Path

    filename_station = Path(sys.argv[1]).stem.split("_")[0].split(".")[0].upper().rstrip("F")
    df = load_qme(sys.argv[1], station=filename_station)
    print(df.head(10))
    print(f"\n{len(df):,} rows · {df['date'].min().date()} → "
          f"{df['date'].max().date()} · {df['value'].isna().sum()} missing")
