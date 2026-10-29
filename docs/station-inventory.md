# Station inventory

Everything we know about which stations exist where, and which ones actually
let you compare a forecast against what really happened.

## The forecast network: 30 named points

Pulled from the deterministic export's 39 columns, collapsed to physical
sites (a handful of codes carry an `L`/`LT` suffix variant of the same site
— see [file-formats.md](file-formats.md#3-deterministic-historical-export)).

```
ANTC1  BWKC1  CFWC1  DCSC1  DCWC1  DMCC1  DVSC1  FHDC1  FOCC1  GYRC1
HLEC1  IIFC1  JKRC1  JNSC1  LOCC1  MFTC1  MRMC1  MRYC1  NBBC1  NFEC1
ORDC1  OURC1  PLGC1L PLLC1  ROLC1  SCBC1  SOVC1  SUAC1  WBGC1  YUBC1L
```

### Coverage per archive

| Archive | Stations covered | Count |
|---|---|---|
| Basin HEFS ensemble CSV | IIFC1, SCBC1, MFTC1, MRMC1, NFEC1, WBGC1, ORDC1, PLLC1, ANTC1, DVSC1, FHDC1, PLGC1L | 12 |
| Per-station ESP XML (full history) | CFWC1, DCWC1, MRYC1(L), NBBC1, ORDC1, YUBC1L | 6 |
| Per-station ESP XML (flood events only) | adds HLEC1(L) | +1 |
| Deterministic export | all 30 | 30 |

### Coverage by observed data (both downloads combined)

**22 of the 30 forecast points have a matching observed record:**

```
ANTC1  BWKC1  DVSC1  FHDC1  FOCC1  GYRC1  HLEC1  IIFC1  JKRC1  JNSC1
LOCC1  MFTC1  MRMC1  NBBC1  NFEC1  ORDC1  OURC1  PLGC1L PLLC1  SCBC1
SUAC1  WBGC1
```

**8 forecast points have NO observed record anywhere in this project:**

```
CFWC1  DCSC1  DCWC1  DMCC1  MRYC1  ROLC1  SOVC1  YUBC1L
```

Of the 22 covered points, only **5** have observed data in *both* the
original and the newer download (meaning: a deeper, longer record is
available): `GYRC1`, `HLEC1`, `NBBC1`, `ORDC1`, `SCBC1`. The other 17 only
have the original (shorter) record.

**If you need to verify a forecast against reality, start with these 5
stations** — they have the longest observed baseline *and* a forecast/
simulation archive to check it against.

---

## The observed-data downloads

Two separate pulls exist, with almost no overlap, plus a non-Feather-Yuba
basin mixed in.

### Original download (`streamflow_obs/*.zip`)

40 stations, Oct 1944 → ~2021, split by basin:

| Basin | Stations |
|---|---|
| Feather (12) | ANTC1, DVSC1, FHDC1, IIFC1, MFTC1, MRMC1, NFEC1, ORDC1, PLGC1L, PLLC1, SCBC1, WBGC1 |
| Yuba (12) | BWKC1, CAMPTON, FOCC1, GYRC1, HLEC1, JKRC1, JNSC1, LOCC1, LOHMAN, NBBC1, OURC1, SUAC1 |
| American (16) | AKYC1, BCTC1, CBAC1, FMDC1, FOLC1, HLLC1, ICHC1, LNLC1, MFPC1, NFDC1, NMFC1, RBBC1, RRGC1, SPYC1, SVCC1, UNVC1 |

The American River basin is a separate watershed, included here for
comparison — not part of the Feather-Yuba forecast network at all.

### Newer download (`streamflow_obs/new.oct.19.second.download/`)

40 stations, Oct 1900 → Jan 2025, split by file format:

- `csv/` — 22 stations, plain `Date,Flow` daily files
- `datacard/` — 19 stations, fixed-width QME
- `BDBC1` appears in both formats (1 overlap between the two subfolders)

14 of these 40 reach back to 1900–1941 — far deeper than anything in the
original download: `WOOC1`, `BDBC1`, `SESC1`, `UKAC1`, `HPIC1`, `POHC1`,
`GYRC1`, `CREC1`, `SCBC1`, `BTEC1`, `WWBC1`, `PRBC1`, `FTJC1`, `NFDC1`.

Several of these site IDs sit well outside the Feather-Yuba-American network
— e.g. `BDBC1` is explicitly labeled "SACRAMENTO R AB BEND BRIDGE" in its own
file header. This pull looks like a broader CNRFC pull than just this basin;
we did not try to verify the geography of every code beyond what each file's
header states.

### Overlap between the two downloads

Only **7 stations** appear in both downloads: `FOLC1`, `GYRC1`, `HLEC1`,
`NBBC1`, `NFDC1`, `ORDC1`, `SCBC1`. For these, the newer download mostly just
extends the record further back — e.g. `GYRC1` goes from 1944–2020 (original)
to 1930–2024 (newer); `SCBC1` goes from 1948–2020 to 1933–2024.

The other 33 stations in the newer download are new to the project — no
forecast/simulation archive, and no prior observed record, exists for them
here.

---

## Quick reference: "I have station X, what do I have for it?"

1. Is it one of the 30 forecast points above? If not, it's observation-only.
2. Is it in the 12-station basin CSV list? → you have a 3-year ensemble hindcast sample.
3. Is it in the 7-station XML list? → you have the full multi-decade ensemble archive (or just the flood windows, for `HLEC1`).
4. Is it in the 22-station "has observed data" list? → check both downloads; only 5 stations have both.
5. Otherwise: observation-only, no way to check a forecast against it here.
