# Verification — 2013 baseline (Trang frozone WRF vs Basin obs)

Baseline evaluation for the MDPI *Air* WRF paper: Trang's existing `WRF_TRANG_frozone/WRF_anlnudge` run scored against 6 Uinta Basin stations for the Jan 15-21 2013 wintertime ozone event. Headline result: a systematic **+4 to +6 °C 2 m warm bias** (the model over-mixes and cannot hold the cold pool) with correct surface pressure — the number the improved run must beat.

## Contents
- `baseline-eval-2013.md` — full writeup: setup, pipeline, figure guide, scores, interpretation.
- `scripts/` — the verification pipeline (`reduce_wrf_to_stations.py` -> `case_study_2013_obs.py` -> `verify_baseline.py` -> `plot_baseline_eval.py`).
- `data/baseline_scores_jan1521.csv` — per-station scores.
- `data/figures/` — the 7 diagnostic figures.

## Running the code
Scripts are copied here from the canonical source, brc-tools branch `mjdavies/synoptic-2013-verify`, for a self-contained record. They import `brc_tools` (e.g. `brc_tools.verify.paired_scores`), so run with that on the path:

```bash
PYTHONPATH=~/brc-tools python verification/scripts/verify_baseline.py ...
```

See `baseline-eval-2013.md` section 6 for the full reproduce commands (WRF output staged on CHPC scratch).

## Feb 1-2 2013 case study (independent runs)

Separate from the Jan 15-21 baseline above: an independent evaluation for the **Feb 1-2 2013** high-ozone episode (the case in Tran et al. 2018), obs vs John's WRF runs.

- `scripts/select_stations_2013.py` — matches the 7 Tran (2018) eval sites to Synoptic STIDs (USU01-USU07), pulls authoritative metadata, and gates on real case-window data. Writes `data/stations_2013_selection.csv`.
- `scripts/verify_pull.py` — QC gate on a pulled obs parquet (station coverage + unit sanity).
- Station list = the 7 eval sites + basin context (USU08/UUT01/KVEL/QV4/QRS) = `BASIN_2013` in `case_study_2013_obs.py`. USU06 (Sand Wash) is offline over Feb 1-2, so 6 of 7 eval sites are usable.

**Obs data stays local.** `*.parquet` is gitignored — bulk obs never enter the repo; only the small selection/score CSVs and figures are tracked. The pull writes to a local cache (`~/brc-tools/data/`):

```bash
# 1. station selection + availability table (small CSV, tracked)
PYTHONPATH=~/brc-tools python verification/scripts/select_stations_2013.py

# 2. obs pull -> LOCAL parquet (NOT the repo)
PYTHONPATH=~/brc-tools python verification/scripts/case_study_2013_obs.py \
    --start "2013-01-31 00Z" --end "2013-02-04 00Z" \
    --out ~/brc-tools/data/obs_basin_2013_feb0102.parquet

# 3. verification gate on the local parquet
python verification/scripts/verify_pull.py \
    ~/brc-tools/data/obs_basin_2013_feb0102.parquet \
    --expected USU01 USU02 USU03 USU04 USU05 USU06 USU07 USU08 UUT01 KVEL QV4 QRS
```
