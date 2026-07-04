# CHPC session: reduce the three touchstone runs (Feb 1-2 2013)

Command sheet for a Michael-driven CHPC session. Goal: locate John's three "333m"
touchstone runs, stage them to scratch, reduce each to a per-station CSV, and pull
the CSVs back local. Everything downstream (scoring, overlays, spread) then runs
locally via `verify_runs_feb0102.py` / `plot_wrf_vs_obs_feb0102.py`.

Runs (John, 2026-07-02): GFS-driven two-way ON; NAM-driven two-way ON; NAM-driven
two-way OFF (Neemann/Tran-like). Directory names contain `333m`.

## 1. Locate the runs (login node OK — trivial)

```sh
ssh u6060939@notchpeak1.chpc.utah.edu
ls -d ~jrlawson/wrf_archive/*333m* 2>/dev/null || find ~jrlawson/wrf_archive -maxdepth 2 -type d -name '*333m*'
du -sh <each dir>          # sanity: how much are we staging?
ls <dir> | head            # confirm wrfout naming + which domain is the 333 m nest
```

Note which domain number the 333 m nest is (d03 expected; adjust `--glob` if not)
and whether wrfouts sit in the dir root or a subdir.

## 2. Stage to scratch (login node, rsync; dtn/globus if >100 GiB total)

```sh
mkdir -p /scratch/general/vast/u6060939/wrf_touchstones_2013
rsync -a --info=progress2 <gfs_2way_dir>/wrfout_d03_2013-0[12]* /scratch/general/vast/u6060939/wrf_touchstones_2013/gfs_2way/
rsync -a --info=progress2 <nam_2way_dir>/wrfout_d03_2013-0[12]* /scratch/general/vast/u6060939/wrf_touchstones_2013/nam_2way/
rsync -a --info=progress2 <nam_1way_dir>/wrfout_d03_2013-0[12]* /scratch/general/vast/u6060939/wrf_touchstones_2013/nam_1way/
```

Scratch purges at 60 days — this is a working copy, the archive stays put.

## 3. Reduce (compute node — NOT the login node)

Get the two scripts + station CSV up (from the local repo clone):

```sh
# local machine
scp verification/scripts/reduce_wrf_to_stations.py verification/scripts/plot_wrf_cross_sections.py \
    verification/data/stations_2013_selection.csv u6060939@notchpeak1.chpc.utah.edu:
```

Then on CHPC:

```sh
salloc -A lawson-np -p lawson-np -N 1 -n 4 --mem=16G -t 2:00:00
# python env needs xarray+netCDF4+numpy+pandas (miniforge3 env in $HOME/envs)
cd /scratch/general/vast/u6060939/wrf_touchstones_2013
for run in gfs_2way nam_2way nam_1way; do
  python ~/reduce_wrf_to_stations.py --wrf-dir $run --run-label $run --stations ~/stations_2013_selection.csv
done
```

Each writes `wrf_<run>_per_station.csv` (~1 MB). Check the printed station->cell
mapping: terrain heights should be plausible (1400-2300 m) and no two stations in
the same cell.

Optional while the allocation is live — cross-sections (matplotlib needed too):

```sh
for run in gfs_2way nam_2way nam_1way; do
  python ~/plot_wrf_cross_sections.py --wrf-dir $run --run-label $run --stations ~/stations_2013_selection.csv
done
```

Watch for the "outside the domain" warning: if USU03 (Mountain Home) falls outside
the 333 m nest, rerun with `--transect USU07 USU05` (or slice the 1 km domain via
`--glob 'wrfout_d02*'`).

## 4. Pull back + finish locally

```sh
# local machine
scp 'u6060939@notchpeak1.chpc.utah.edu:/scratch/general/vast/u6060939/wrf_touchstones_2013/wrf_*_per_station.csv' ~/brc-tools/data/
scp -r 'u6060939@notchpeak1.chpc.utah.edu:/scratch/general/vast/u6060939/wrf_touchstones_2013/*/figures' ./xsect-figs/

cd ~/lawson-davies-air-wrf-2026
PYTHONPATH=~/brc-tools python verification/scripts/verify_runs_feb0102.py \
    --wrf ~/brc-tools/data/wrf_{gfs_2way,nam_2way,nam_1way}_per_station.csv
PYTHONPATH=~/brc-tools python verification/scripts/plot_wrf_vs_obs_feb0102.py \
    --wrf ~/brc-tools/data/wrf_{gfs_2way,nam_2way,nam_1way}_per_station.csv
```

Outputs: `wrf_runs_scores_feb0102.csv` + `wrf_runs_spread_feb0102.csv` (verification/data/),
overlay figures (verification/data/figures/). Both pipelines are smoke-tested green
(`smoke_test_runs_feb0102.py`, `smoke_test_cross_sections.py`) — synthetic fixtures,
so the first real-data run should still be eyeballed against the QC list in
`docs/how-to-obs-verify.md` (actual-T-not-potential, 1-h offset, units/sign/axis).

## Session notes (2026-07-03, first real pass)

- Archive actually lives at `/uufs/chpc.utah.edu/common/home/lawson-group6/jrlawson/wrf_archive`
  (not `~jrlawson`). Four `*333m*` dirs; `pelican2013_rap_...` has 0 wrfouts (skip). Wrfouts sit
  under `full6h/run_<stamp>/`, NOT the dir root; the nam dir also has a `smoke6h` test run (skip).
- Runs are 6-h forecasts: wrfout_d0{2,3} hourly, 2013-02-02 12:00-18:00 UTC only. First ~2 h are
  spin-up (visible as blocky IC noise in the GFS t=0 fields) — score with
  `--min-time 2013-02-02T14:00 --out-suffix _postspinup`, and pass the cross-section script
  `--times 2013-02-02_16:00:00` rather than the frame-zero default.
- **The 333 m nest (d03, ~50x48 km) excludes the bench stations** — 7 of 11 stations clamp to its
  boundary. d02 (1 km) covers all 11 (USU03 terrain 2222 m vs real 2228 m) → d02 is the comparison
  domain; d03 is interior-only (USU07/USU02/USU08/KVEL) resolution sensitivity.
- Python env: `~/.conda/envs/wrfpost/bin/python` has the full stack (xarray/netCDF4/pandas/
  matplotlib). `conda activate` fails on compute nodes without the shell hook — call the env's
  python directly. Scripts pull cleanly via `git clone -b wrf-run-pipeline-feb2013 <repo> ~/wrfpaper`
  (works on notch nodes; no scp needed).
- Staged copies: `/scratch/general/vast/u6060939/wrf_touchstones_2013/{gfs_2way,nam_2way,nam_1way}`
  (60-day purge); durable bundle of reduced CSVs + figures:
  `lawson-group6/u6060939/wrf_touchstones_2013_reduced/touchstones_reduced.tgz`.

## Session notes (2026-07-04, Tran-runs comparison)

- Tran's archived WRF runs live in the group's rclone `archive:` remote (S3; ask John/Loknath
  for access) — `trang/WRFOUT/WRF_TRANG_frozone/WRF_anlnudge` (Jan 15-21 2013, the previously
  scored baseline window) and `trang_G5/WRF_SIP/` (the FDDA-study suite for the Jan 29-Feb 12
  episode: `REF_long` reference run + nudging-coefficient / land-use / vertical-level variants,
  plus a `namelists` dir). Her config (kept out of this public repo; see local copies):
  12 / 4 / 1.33 km one-way nests, 37 levels, MYJ PBL + Noah LSM + Thompson mp + RRTMG,
  continuous multi-week episode runs — a setup built to drive AQ modeling, with FDDA as the
  designed correction, vs our 75-level 3 / 1 / 0.333 km short-forecast touchstones.
- `REF_long` d03 (1.33 km) covers our Feb 1-2 case → direct same-case comparison
  (`wrf_trang_ref_per_station.csv`, `*_withtrang` score tables). On 14-18 UTC Feb 2 the
  un-nudged reference shows a -4.4 C 2 m T bias (cold, strongest midday) with a deeper/colder
  CAP than observed — consistent with the motivation for FDDA documented in Tran (2018), and a
  different error direction than the Jan 15-21 anlnudge baseline (+4-6 C warm). Together: the
  un-nudged errors are episode- and config-dependent in both sign and size, which is the gap
  the short-forecast approach targets.
- Fair-comparison caveat: one 6-h window vs multi-week continuous runs; her best *nudged*
  variant (e.g. `REF_long_0.00008forT`) is the appropriate skill anchor — reduce it with this
  same sheet if wanted (~20 min).
- Cross-section snapshots regenerated at 2013-02-02_16:00 UTC (post-spin-up) for the three
  touchstones (`*_d02_16z`) — use these, not the frame-zero originals.
