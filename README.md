# Feather-Yuba Data Guide

A map and toolkit for the CNRFC Feather-Yuba basin streamflow dataset: ESP/HEFS
ensemble forecast hindcasts, one deterministic historical simulation, and
observed gauge records. This repo does **not** contain the data itself (it's
~88GB) — it explains what each file is, how to read it, and which stations
actually have forecast-vs-observed coverage, plus small parser scripts to get
any file into a tidy table quickly.

If someone handed you a folder of `.csv`, `.xml`, and `.qme` files from this
project and you don't know where to start, start here.

## The five file types

| Type | Where | What it is |
|---|---|---|
| Basin HEFS hourly CSV | `*_FeatherYuba_hefs_csv_hourly.csv` | 14-day, 62-member ensemble forecast for 12 points, 3 selected years |
| Per-station ESP/MEFP XML | `<STATION>/`, `1986/`, `1997/` | Same kind of ensemble forecast, one station at a time, full multi-decade history |
| Deterministic export | `*_FeatherYuba_csv_export` | One continuous simulated trace, no ensemble, 26 water years |
| Observed QME / datacard | `streamflow_obs/*.qme`, `datacard/*.qme` | Daily observed/naturalized flow, fixed-width legacy format |
| Observed daily CSV | `streamflow_obs/.../csv/*.csv` | Same kind of observed record, plain `Date,Flow` format |

Full detail on every field, header, and gotcha: **[docs/file-formats.md](docs/file-formats.md)**

## Station coverage — the short version

This dataset covers **30 named forecast points**, but:

- Only **12** have the basin-wide HEFS ensemble CSV
- Only **7** have the full per-station ESP XML archive
- Only **22 of the 30** have *any* matching observed record, across both observed downloads combined
- **8 forecast points have no observed data anywhere in this project**: `CFWC1`, `DCSC1`, `DCWC1`, `DMCC1`, `MRYC1`, `ROLC1`, `SOVC1`, `YUBC1L`

Full station-by-station tables, including which observed stations sit entirely
outside this forecast network: **[docs/station-inventory.md](docs/station-inventory.md)**

## Quickstart

```bash
pip install -r scripts/requirements.txt
```

```python
from scripts.parse_hefs_csv import load_hefs_csv
from scripts.parse_pi_xml import load_pi_xml
from scripts.parse_qme import load_qme
from scripts.parse_daily_csv import load_daily_csv

# A basin-wide ensemble hindcast (or the deterministic export — same shape)
df = load_hefs_csv("2009040112_FeatherYuba_hefs_csv_hourly.csv")

# A single-station ensemble issuance (62 members, one per analog year)
df = load_pi_xml("1996122712.NBBC1.SQIN.xml")

# Observed data, either format
df = load_qme("nbbc1f_fnf_2019.qme")
df = load_daily_csv("ORDC1_fnf_daily.csv")
```

Each loader returns a long-format `pandas.DataFrame` with consistent columns
(`station`, `time`/`date`, `value`, plus `member`/`parameter`/`units` where
relevant) — see each script's docstring for the exact schema.

## What's *not* here

The raw data files themselves. Point teammates at wherever your team actually
stores the 88GB (shared drive, bucket, etc.) — this repo is the map, not the
territory.
