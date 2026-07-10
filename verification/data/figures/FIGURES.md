# Figure catalog — verification figures

Every figure in this directory: which script makes it, the exact command, and
what it shows. PNGs also carry the generating script in their metadata
(`Software` field; visible via Preview > Tools > Show Inspector, or `exiftool`).
All figures are 2026-07-09 journal style: no titles on local sets, panel
letters, Okabe-Ito colors, PNG + PDF pairs. Draft captions with the full
quantitative descriptions: `CAPTIONS_draft.md`.

Regenerate-all: local figures from the commands below; wrfout-based figures need
a CHPC session (`docs/chpc-feb-touchstones.md`; one-command runner
`scripts/regen_wrfout_figures.sh`).

## Jan 15–21 2013 baseline (Tran anlnudge d03 vs 6 stations)

Script: `plot_baseline_eval.py` (no args; reads `~/brc-tools/data`, writes here).
Inputs: `obs_basin_2013_jan1521.parquet` + `wrf_trang_2013_per_station.csv`.

| File | What it shows |
|---|---|
| `baseline_temp_timeseries_jan1521.png` | 6-panel 2 m T, obs vs WRF |
| `baseline_temp_scatter_jan1521.png` | WRF vs obs 2 m T against 1:1, bias annotated |
| `baseline_temp_diurnal_bias_jan1521.png` | mean WRF−obs by hour (UTC), per station + all-station |
| `baseline_inversion_night_zoom_jan1521.png` | 2 m T, ±18 h around the coldest observation |
| `baseline_windspeed_timeseries_jan1521.png` | 6-panel 10 m wind, obs hourly-mean vs WRF |
| `baseline_pressure_timeseries_jan1521.png` | 4-panel surface pressure (stations with obs pressure) |
| `baseline_skill_bars_jan1521.png` | bias + RMSE bars per station (T / wind / pressure); wind_dir excluded (circular + calm-filtered in the score tables instead) |

## Feb 1–2 2013 observed case (obs only)

Script: `plot_obs_feb0102.py` (no args; obs parquet from local cache
`obs_basin_2013_feb0102.parquet`).

| File | What it shows |
|---|---|
| `obs_theta_profiles_feb0102.png` | pseudo-vertical θ profiles, 6 snapshot times (Whiteman & Hoch style) |
| `obs_temp_timeseries_feb0102.png` | 2 m T at 4 floor→bench stations, elevation-keyed colors |
| `obs_inversion_index_feb0102.png` | Δθ bench−floor + valley heat deficit; 8 °C CAP threshold marked |

## Feb 1–2 2013 WRF vs obs (three touchstone runs, d02)

Script: `plot_wrf_vs_obs_feb0102.py --wrf <three d02 per-station CSVs>`;
add `--window 2013-02-02T04:00 2013-02-02T12:00 --spinup-until 2013-02-02T07:00`
for the `_zoom` versions. Paper set = the two `_zoom` figures; the full-window
versions are working/supplementary (episode context is carried by the obs-only
figures above).

| File | What it shows |
|---|---|
| `wrf_temp_timeseries_feb0102.png` | WORKING/SUPP: 2 m T, obs + 3 runs + spread band, 4 stations, full episode |
| `wrf_temp_timeseries_feb0102_zoom.png` | PAPER: same, forecast window ±1 h, hourly ticks, spin-up marker |
| `wrf_inversion_index_feb0102.png` | WORKING/SUPP: (a) Δθ bench−floor (b) valley heat deficit, obs + runs, full episode |
| `wrf_inversion_index_feb0102_zoom.png` | PAPER: same, zoomed; dotted line = end of spin-up |

## wrfout diagnostics (CHPC-generated, 2026-07-09 shared-scale set)

Scripts: `plot_wrf_cross_sections.py` / `plot_wrf_upper_air.py`, run per run dir
on a compute node. Exact commands (including the fixed `--vrange` per figure
family, `--adv-cap 10`, `--mark-stations`): `scripts/regen_wrfout_figures.sh`,
documented in `docs/chpc-feb-touchstones.md`. Feb θ sections/time-heights share
266–306 K; 700 hPa maps 294–303 K; 500 hPa maps 307–312 K; diff maps ±5 / ±2.5 °C;
advection ±10 °C h⁻¹ (Uinta wave couplets saturate by design).

| File (per run: gfs_2way_d02 / nam_2way_d02 / nam_1way_d02) | What it shows |
|---|---|
| `wrf_xsect_theta_<run>.png` | θ slice USU07→USU03, 16 UTC post-spin-up |
| `wrf_timeheight_theta_<run>.png` | θ time-height at QRS, 12–18 UTC |
| `wrf_upper_700hPa_<run>.png` | θ + winds at 700 hPa, 14 + 16 UTC |
| `wrf_upper_500hPa_<run>.png` | θ + winds at 500 hPa, 14 + 16 UTC |
| `wrf_upper_{700,500}hPa_gfs_minus_nam2way_d02.png` | GFS−NAM Δθ maps |
| `wrf_adv_{700,500}hPa_<run>.png` | horizontal θ advection (°C/h), mechanism check on the 700 hPa GFS warm layer |
| `wrf_xsect_theta_trang_ref.png`, `wrf_timeheight_theta_trang_ref.png` | Tran REF (obs-nudged, WRF 4.2, 1.33 km), same case; provenance in chpc-feb-touchstones.md 2026-07-09 notes |
| `wrf_xsect_theta_trang_anlnudge_jan17.png`, `wrf_timeheight_theta_trang_anlnudge_jan17.png` | Tran anlnudge, Jan 17 (xsect 11 UTC = 04 MST pre-dawn; file covers 00–11 UTC) |

No nudged-variant figures: Tran's nudged coefficient variants all end Feb 2
09 UTC, before the forecast window (chpc-feb-touchstones.md 07-09 notes).
