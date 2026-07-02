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
