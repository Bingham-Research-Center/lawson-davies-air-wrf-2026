# Provenance — recovering the WRF run config for the Methods section

Read-only CHPC probes used to recover the exact configuration of the 2013 WRF runs
(forcing dataset, PBL / land-surface / microphysics schemes, vertical levels, d03 `dx`,
analysis-nudging settings, run window) so the manuscript Methods can disclose them
accurately. No model runs here — just digging the group archive for the namelist and
config that produced the runs.

## Files
- `chpc_pathcheck.sh` — first-pass probe: locate Trang's `WRF_TRANG_frozone` / `WRF_anlnudge`
  baseline run dir and its namelist on the group archive / scratch (read-only: `ls`/`stat`/`find`/
  `grep`, `rclone ls`, `ncdump -h`).
- `chpc_wrf_provenance.sh` — targeted dig of the archive subtrees that hold the run config,
  extracting the Methods-relevant settings. Read-only except an optional, size-capped,
  auto-deleted single-`wrfout` fallback download used only when no `namelist.input` is found.
- `namelist_candidates.txt` — the `namelist.input` candidates surfaced from the archive
  (raw config to reconcile against the runs before it enters Methods).

## Running (on CHPC)
```sh
module load rclone netcdf-c          # or: module load nco
bash chpc_pathcheck.sh      2>&1 | tee chpc_pathcheck_$(date +%F).log
bash chpc_wrf_provenance.sh 2>&1 | tee chpc_wrf_provenance_$(date +%F).log
```
Run logs (`*.log`, `*.log.txt`) are gitignored — large raw dumps, not tracked. The original
2026-07-01 dumps are preserved on the `jrl/first-edits` branch if ever needed.

## Status
Candidate namelists are recovered but **not yet reconciled** against the actual runs — verify
forcing / scheme / level / `dx` / nudging / window against the run output before citing in
Methods (flagged in `main.tex`).
