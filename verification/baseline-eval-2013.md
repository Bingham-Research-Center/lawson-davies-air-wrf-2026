# Baseline evaluation — Trang 2013 frozone WRF vs Basin obs

**Jan 15–21 2013 wintertime ozone event · domain d03 · branch `mjdavies/synoptic-2013-verify`**
Owner: Michael · scored 2026-06-22 · for the MDPI *Air* meteorology/methods paper (John leads; Michael owns diagnostics + figures).

## Headline
Trang's existing run is the **baseline we have to beat**. Scored against 6 Basin stations it shows a **systematic +4 to +6 °C warm bias in 2 m temperature at every station**, paired with a mild **over-windiness** at 10 m. Surface pressure is essentially correct. Read together: the synoptic mass field is right, but the model's **PBL over-mixes and cannot hold the surface cold pool / inversion** — which is precisely the error a wintertime-ozone run must fix. **Shrinking the surface warm bias = holding the cold pool = beating the baseline.**

---

## 1. What was run (model setup)
- **Run:** Trang's `WRF_TRANG_frozone/WRF_anlnudge` — the **analysis-nudged** configuration — pulled from `archive:trang/WRFOUT/...` via rclone (Loknath's world-readable `archive:` remote) and staged to CHPC scratch (`/scratch/general/vast/u6060939/wrf_trang_2013`).
- **Domain / cadence:** innermost **d03**, **hourly** output.
- **Period:** **2013-01-15 12Z → 2013-01-21 00Z** = **133 hourly frames**. The obs window was realigned to match (the run is January, not the February window we first assumed).
- **Not this run:** `WRF_HUY*_Janfeb15` is a *2015* case — ignore it.

## 2. How it was evaluated (verification pipeline)
Fully reproducible, standalone scripts on the branch above (`scripts/`):

1. **`reduce_wrf_to_stations.py`** — reads the staged `wrfout_d03`, finds the nearest d03 grid cell to each station (XLAT/XLONG), extracts `T2 / U10 / V10 / PSFC / Q2`, **rotates the 10 m winds grid→earth-relative** (COSALPHA/SINALPHA — wrfout winds are grid-relative), derives speed/direction, and writes a tidy per-station hourly CSV. Runs on a CHPC compute node; needs only xarray + netCDF4 + numpy + pandas.
2. **`case_study_2013_obs.py`** — Synoptic obs pull for the 6 stations using the *correct 2013-era STIDs* → `data/obs_basin_2013_jan1521.parquet`.
3. **`verify_baseline.py`** — aligns WRF↔obs on `(station, valid_time)` within a 30-min tolerance and scores each variable per station via `brc_tools.verify.paired_scores` (`harmonize=True` handles K→°C). Wind direction uses a **circular-aware metric** (wrap-corrected bias/MAE/RMSE + Jammalamadaka circular correlation — fixed #32, the old metric had wraparound artifacts). → `data/baseline_scores_jan1521.csv`.
4. **`plot_baseline_eval.py`** — writes the 7 figures below to `data/figures/`.

**Stations (6):** USU01, USU05, USU08 (USU network), KVEL (NWS/RAWS), QV4, QRS (UDOT — *no pressure reported*). Obs are resampled to hourly means to match WRF's native hourly output; WRF is shown as-is.

## 3. The figures (`data/figures/`, what each shows)
| File | What it is |
|------|------------|
| `baseline_temp_timeseries_jan1521.png` | 6-panel 2 m T, obs (black, hourly mean) vs WRF (red), per station — the warm bias is visible everywhere |
| `baseline_windspeed_timeseries_jan1521.png` | 6-panel 10 m wind speed, obs hourly-mean vs WRF — WRF generally too windy |
| `baseline_pressure_timeseries_jan1521.png` | 6-panel surface pressure (only USU01/05/08 + KVEL report) — near-perfect tracking |
| `baseline_skill_bars_jan1521.png` | per-station **bias + RMSE bars** for temp / wind-speed / pressure (wind_dir omitted — needs the circular metric) |
| `baseline_temp_scatter_jan1521.png` | WRF-vs-obs 2 m T scatter against the 1:1 line; overall bias annotated — points sit consistently above 1:1 (warm) |
| `baseline_temp_diurnal_bias_jan1521.png` | mean (WRF−obs) by hour, per station + all-station mean — **diagnostic: is the warm bias worst overnight, as a cold-pool failure would be?** |
| `baseline_inversion_night_zoom_jan1521.png` | 2 m T zoomed to ±18 h around the **coldest observed temperature** (deepest-inversion night) — where the model loses the inversion most |

## 4. Findings (scores vs obs)

**2 m temperature — the headline. Systematic +4 to +6 °C warm bias, every station.** MAE ≈ bias ⇒ the error is almost entirely systematic, not noise. Correlation stays high (0.84–0.92), so the *shape* is right — it's offset warm.

| Station | bias (°C) | MAE | RMSE | corr |
|---------|-----------|-----|------|------|
| KVEL  | **+6.12** | 6.12 | 6.37 | 0.87 |
| QRS   | +5.75 | 5.75 | 5.94 | 0.89 |
| USU01 | +5.76 | 5.76 | 5.93 | 0.92 |
| USU05 | +5.74 | 5.74 | 5.97 | 0.88 |
| USU08 | +5.43 | 5.45 | 5.81 | 0.85 |
| QV4   | +4.26 | 4.40 | 4.85 | 0.84 |

**Surface pressure — good.** Bias ≲1 hPa where reported (KVEL −0.86, USU01 −0.44, USU05 +0.36, USU08 −1.17 hPa), corr 0.93–0.95. The large-scale mass field is well captured — this is *not* a synoptic problem.

**10 m wind speed — slightly too windy.** Positive bias at 5 of 6 stations (worst **USU05 +2.4 m/s**; KVEL +1.1; others +0.5–0.7; QRS the lone slightly-calm one at −0.8). Correlation near zero (0.07–0.22) — the model doesn't capture the *timing* of the calms/gusts. Consistent with over-ventilation in a regime that is genuinely near-calm and hard to verify.

**10 m wind direction — near-random, and that's expected.** Circular bias −21°…+13°, MAE ~43–103°. In a genuinely calm basin, direction is ill-defined — this is a property of the regime, **not** a flagged model failure (hence omitted from the skill bars).

## 5. Interpretation & where to go next
Warm **and** over-windy **and** correct pressure ⇒ a boundary layer that **mixes out the inversion**: too much vertical mixing ventilates the cold pool, warming 2 m T and raising 10 m winds, while the synoptic field stays right. The diurnal-bias figure tests the signature directly (expect the warm bias to peak overnight when the real cold pool is strongest).

**Levers to propose for the improved run** (the d03 config to beat this baseline):
- **PBL scheme** (less aggressive mixing in stable conditions),
- **near-surface vertical resolution** (more levels in the lowest ~100–200 m),
- **land-surface / snow** (albedo + insulation drive the surface energy balance that sets the inversion).

Procedure is set: rerun the **same pipeline** on an improved config and compare against `baseline_scores_jan1521.csv` — beating the baseline means a smaller surface warm bias.

## 6. Reproduce
```bash
# on a CHPC compute node (data on scratch); from ~/brc-tools with PYTHONPATH=.
python scripts/reduce_wrf_to_stations.py \
  --wrf-dir /scratch/general/vast/u6060939/wrf_trang_2013 \
  --glob 'wrfout_d03_2013-01-*' --out data/wrf_trang_2013_per_station.csv
# [ISSUE #3: BROKEN as written -- no-arg case_study_2013_obs.py uses stale Feb defaults
#  and writes obs_basin_2013_stids2013.parquet, NOT the jan1521 file below. Needs the
#  explicit Jan 15-21 window + --out (Michael to finalize):]
python scripts/case_study_2013_obs.py \
  --start "[JAN-2013-START -- see #3]" --end "[JAN-2013-END -- see #3]" \
  --out data/obs_basin_2013_jan1521.parquet
python scripts/verify_baseline.py \
  --wrf data/wrf_trang_2013_per_station.csv \
  --obs data/obs_basin_2013_jan1521.parquet \
  --out data/baseline_scores_jan1521.csv
python scripts/plot_baseline_eval.py             # -> data/figures/*.png
```

## 7. Open for John
- **Confirm the baseline:** is `WRF_TRANG_frozone/WRF_anlnudge` the run you mean? Everything keys off it.
- The ~10-run **predictability spread** (#24) is yours — separate from this deterministic baseline.
