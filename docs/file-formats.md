# File formats

Five distinct file shapes show up in this dataset. This doc covers each one:
what it looks like raw, what every field means, and the gotchas that aren't
obvious from a quick glance.

---

## 1. Basin HEFS hourly CSV

**Filename pattern:** `YYYYMMDDHH_FeatherYuba_hefs_csv_hourly.csv`
The filename *is* the forecast issuance date/hour — always `12` (12Z UTC).

**Shape:** three header-ish rows, then one row per timestep.

```
GMT,IIFC1,IIFC1,...,SCBC1,...
,QINE,QINE,...,QINE,...
2001-03-19 12:00:00,0.04362,0.04362,...
2001-03-19 13:00:00,0.04405,0.04474,...
```

- **Row 1** — station code, repeated once per ensemble member (62 repeats per station)
- **Row 2** — parameter code for that column (`QINE` or `SQIN`)
- **Row 3+** — one row per hourly timestep, first column is the GMT timestamp

| Fact | Value |
|---|---|
| Ensemble members | 62 (one per historical analog year) |
| Timesteps | 337 (14-day lead, hourly) |
| Stations | 12 — 7 `QINE` (IIFC1, SCBC1, MFTC1, MRMC1, NFEC1, WBGC1, ORDC1), 5 `SQIN` (PLLC1, ANTC1, DVSC1, FHDC1, PLGC1L) |
| Issuance years | 2001 (Jan–Sep), 2005 (Jan–Sep), 2009 (full year) — daily, 12Z only |

**Gotcha:** `QINE` and `SQIN` are *different quantities at the same kind of
node* — don't assume a station's `QINE` value and its `SQIN` value (if it
appears in another file) are comparable. `QINE` generally reads like a local
inflow/accretion term; `SQIN` reads like a larger, more routed quantity. We
never got an authoritative definition from the files themselves — this is
inferred from relative magnitudes, not documented anywhere in the headers.

---

## 2. Per-station ESP/MEFP XML

**Filename pattern:** `YYYYMMDDHH.STATIONCODE.SQIN.xml`, one file per station
per issuance, inside a folder named for the station (e.g. `NBBC1/`) or inside
an event folder (`1986/`, `1997/`).

This is [Delft-FEWS PI-XML](https://oss.deltares.nl/web/fews/pi-xml). Each
file contains 62 `<series>` blocks — one per ensemble member:

```xml
<series>
  <header>
    <type>instantaneous</type>
    <locationId>NBBC1</locationId>
    <parameterId>SQIN</parameterId>
    <ensembleId>MEFP</ensembleId>
    <ensembleMemberIndex>1949</ensembleMemberIndex>
    <timeStep unit="second" multiplier="3600"/>
    <startDate date="1996-12-27" time="12:00:00"/>
    <endDate date="1997-01-11" time="12:00:00"/>
    <units>CMS</units>
    <stationName>NF YUBA - NEW BULLARDS BAR</stationName>
  </header>
  <event date="1996-12-27" time="12:00:00" value="969.901" flag="0"/>
  ...
</series>
```

**Key field:** `ensembleMemberIndex` is not a member number 1–62 — it's the
**historical year** whose meteorological forcing drove that trace (e.g. `1949`
through roughly `2010`). This is the ESP/MEFP method: run the current
hydrologic state forward using every past year's weather, and treat the
spread as the forecast uncertainty.

| Fact | Value |
|---|---|
| Stations with full history | `DCWC1`, `CFWC1`, `MRYC1L`, `NBBC1`, `ORDC1`, `YUBC1L` (~8,988 files each, ~1985–2010, daily 12Z) |
| Stations only in event windows | `HLEC1L` — appears only in `1986/` (Feb 10–26) and `1997/` (Dec 20, 1996 – Jan 9, 1997) |
| Units | CMS (not CFS — convert before comparing to anything in the QME files) |

**Gotcha:** this is the only format with an explicit `<units>` tag. Trust it
over assumptions carried from the CSV formats.

---

## 3. Deterministic historical export

**Filename pattern:** a single file, e.g. `2010093012_FeatherYuba_csv_export`
(no `.csv` extension, but it's plain CSV text).

Same three-header-row shape as the basin HEFS CSV, but **no ensemble** — one
value per station per timestep, continuous from `1984-10-01` to `2010-09-30`
(26 water years in one file), across all **39** station/parameter columns
used anywhere else in the project.

```
GMT,IIFC1,SCBC1,...,YUBC1L
,QINE,QINE,...,SQIN
1984-10-01 12:00:00,-999,0.03979,...
```

**Gotcha:** `-999` is a missing-data sentinel, same convention as the QME
files — filter it out before any statistics.

**Gotcha:** several station codes here (`HLEC1`, `MRYC1`, `JNSC1`, `DCSC1`,
`LOCC1`, `OURC1`, `SUAC1`) appear **twice** — once bare, once with an `L`
suffix (and `HLEC1`/`MRYC1` even have an `LT` variant). These are the same
physical site reporting two or three different series (e.g. local vs. total),
not duplicate columns. 39 columns reduce to 30 *physical* sites once you
collapse these suffix groups.

---

## 4. Observed QME / datacard (fixed-width legacy)

**Filename pattern:** varies a lot — `<station>_fnf_2019.qme`,
`<station>.qme`, `<station>_total_fnf.qme`, etc. Same underlying format in
both `streamflow_obs/*.qme` (inside the original three zips) and
`.../datacard/*.qme` (the deeper multi-decade pull).

```
$  IDENTIFIER=NBBC1F   DESCRIPTION=full natural flow
$  PERIOD OF RECORD=10/1988 THRU 09/2019
$  SYMBOL FOR MISSING DATA=-999.00   SYMBOL FOR ACCUMULATED DATA=-998.00
$  TYPE=QME   UNITS=CFSD   DIMENSIONS=L3     DATA TIME INTERVAL=24 HOURS
$  OUTPUT FORMAT=(3A4,2I2,I4,1F10.2)
NBBC1F      1296  01  01173.80
NBBC1F      1296  02  00828.93
```

Header lines start with `$`. The `OUTPUT FORMAT` line (or, when the `PERIOD
OF RECORD` comment is missing, the raw `MM  YYYY MM  YYYY` line right above
the data) tells you the record's date range.

**Data row layout:** `STATIONCODE` + a **month/year code** + **day** + **value**.
The month/year code is `month` (1 or 2 digits, no leading zero) immediately
followed by a 2-digit year — so:

- `1296` = month `12`, year `96` → December 1996
- `197`  = month `1`, year `97`  → January 1997 (note: only 3 digits, because the month isn't zero-padded)

This trips people up — **don't assume it's always 4 digits.** Always split
from the right: last 2 digits are the year, everything before that is the
month.

| Fact | Value |
|---|---|
| Units | `CFSD` = CFS, daily |
| Missing value | `-999.00` |
| Accumulated-data flag | `-998.00` |
| Century rule for 2-digit years | `<= 30` → 2000s, `> 30` → 1900s (not fully reliable — a few files spell out 4-digit years in `PERIOD OF RECORD`, which should always be preferred when present) |

**Gotcha:** the station code in the data rows often has a trailing `F`
(`NBBC1F`) that isn't on the "clean" station code elsewhere in the project —
strip it when matching against the forecast-point list.

**Gotcha — bigger one:** in the newer `datacard/*.qme` files, the embedded
station field in each data row is frequently the raw **USGS site number**
instead of the CNRFC code (e.g. `11413000` for `GYRC1`, `11402000` for
`SCBC1`). The CNRFC code only appears in the **filename** in those cases.
Don't trust the embedded field — derive the station from the filename
instead. `scripts/parse_qme.py` takes an explicit `station=` override for
exactly this reason.

---

## 5. Observed daily CSV (the newer, simpler format)

**Filename pattern:** `<STATION>_daily.csv` or `<STATION>_fnf_daily.csv`,
inside `streamflow_obs/.../csv/`.

```
Date (ending 12 UTC),Flow (KCFS)
1960-10-01,0.591
1960-10-02,0.671
```

That's it — two columns, one header row, daily. **Flow is in KCFS (thousands
of CFS)**, not CFS — multiply by 1000 before comparing to any QME file, which
is already in plain CFS.

**Gotcha:** this is the only format in the whole project where the unit is
KCFS instead of CFS or CMS. Easy to miss since nothing in the filename flags
it — only the header row says so.
