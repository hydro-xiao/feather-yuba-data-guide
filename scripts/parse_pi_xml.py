"""
Load a per-station ESP/MEFP Delft-FEWS PI-XML file
(`YYYYMMDDHH.STATIONCODE.SQIN.xml`).

See docs/file-formats.md section 2 for the full format writeup.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

import pandas as pd

_NS = {"pi": "http://www.wldelft.nl/fews/PI"}


def load_pi_xml(path: str) -> pd.DataFrame:
    """
    Returns a long-format DataFrame with columns:
        time    (pandas Timestamp)
        station (str, from <locationId>)
        member  (int, the historical analog year from <ensembleMemberIndex> —
                 this is a calendar year like 1949, not a 1..62 index)
        units   (str, from <units>, e.g. "CMS")
        value   (float)
    """
    tree = ET.parse(path)
    root = tree.getroot()

    frames = []
    for series in root.findall("pi:series", _NS):
        header = series.find("pi:header", _NS)
        station = header.find("pi:locationId", _NS).text
        member = int(header.find("pi:ensembleMemberIndex", _NS).text)
        units = header.find("pi:units", _NS).text

        times, values = [], []
        for event in series.findall("pi:event", _NS):
            times.append(f"{event.get('date')} {event.get('time')}")
            values.append(float(event.get("value")))

        frames.append(
            pd.DataFrame(
                {
                    "time": pd.to_datetime(times),
                    "station": station,
                    "member": member,
                    "units": units,
                    "value": values,
                }
            )
        )
    return pd.concat(frames, ignore_index=True)


if __name__ == "__main__":
    import sys

    df = load_pi_xml(sys.argv[1])
    print(df.head(10))
    print(f"\n{len(df):,} rows · {df['member'].nunique()} members "
          f"(analog years {df['member'].min()}–{df['member'].max()}) · "
          f"{df['time'].min()} → {df['time'].max()} · units={df['units'].iloc[0]}")
