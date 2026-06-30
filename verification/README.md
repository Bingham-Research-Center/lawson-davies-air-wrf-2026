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
