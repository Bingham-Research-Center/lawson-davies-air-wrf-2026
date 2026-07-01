#!/usr/bin/env python3
"""Pull Uinta Basin station obs for the 2013 wintertime-ozone case study.

[KNOWN ISSUE #3 -- STALE MONTH: the DEFAULT_START/END below and the "Feb 2013"
wording in this docstring are stale; the baseline case was realigned to Jan 15-21
2013 (see baseline-eval-2013.md sec. 2). Do NOT run no-arg -- the defaults are
placeholdered pending Michael's fix.]

Exercises the ObsSource path (previously untested in brc-tools, PR #16) and
produces a tidy obs frame for WRF verification against the validated Feb-2013
Basin run.

IMPORTANT — station-ID drift: the lookups.toml waypoint_groups are built for the
*modern* network, and most of those STIDs (UB7ST, UBHSP, A3822, ...) have NO 2013
data. In Feb 2013 the BRC research network reported under USU01-USU08 / UUT01, so
this script defaults to a curated 2013-era station list (BASIN_2013) instead of a
group. BASIN_2013 covers the 7 Tran et al. (2018) eval sites (USU01-USU07) plus
context (USU08/UUT01 research trailers, KVEL/QV4/QRS; KVEL carries surface pressure,
UDOT QV4/QRS do not). See select_stations_2013.py for the site->STID mapping and a
per-window availability check (e.g. USU06 Sand Wash is offline over Feb 1-2 2013).

Examples:
    python scripts/case_study_2013_obs.py
    python scripts/case_study_2013_obs.py --start "2013-01-25 00Z" --end "2013-02-15 00Z"
    python scripts/case_study_2013_obs.py --group basin_full   # modern preset (sparse for 2013)

Caveats:
- Obs return in SYNOPTIC native units (temp_2m in C, snow_depth in mm), NOT the
  alias's canonical units. For verification, convert obs or use brc_tools.verify
  (paired_scores(..., harmonize=True) converts the MODEL side to obs units).
- 2013 needs a Synoptic token with the long-term archive (env SYNOPTIC_TOKEN).
- Ozone: `ozone_concentration` returned no stations here — chase var name / network
  access with support@synopticdata.com before relying on 2013 AQ obs.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from brc_tools.obs import ObsSource

# Curated 2013-era basin stations: the 7 Tran et al. (2018) eval sites (USU01-USU07,
# temporary BRC study-period stations) + context (USU08/UUT01 trailers, KVEL/QV4/QRS).
# See select_stations_2013.py for the mapping + case-window availability. USU06 has a
# Feb 1-2 data gap (offline Jan 28-Feb 4) but is kept here for other 2013 windows.
BASIN_2013 = [
    "USU01", "USU02", "USU03", "USU04", "USU05", "USU06", "USU07",  # Tran 2018 eval sites
    "USU08", "UUT01", "KVEL", "QV4", "QRS",                          # context (KVEL = pressure)
]

# [ISSUE #3: stale Feb window -- the baseline case is Jan 15-21 2013, not February.
#  Placeholdered so a no-arg run fails loudly instead of silently producing February
#  obs. Pass explicit --start/--end, or set the Jan window here (Michael).
#  Prior values: START="2013-02-01 00Z", END="2013-02-15 00Z".]
DEFAULT_START = "[SET-JAN-2013-START -- see #3]"
DEFAULT_END = "[SET-JAN-2013-END -- see #3]"
MET_VARS = [
    "temp_2m", "dewpoint_2m", "rh_2m", "wind_speed_10m",
    "wind_dir_10m", "pressure_surface", "snow_depth",
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Pull Basin obs for the 2013 case study.")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--stids", nargs="*", default=None, help="explicit STIDs (default: BASIN_2013)")
    ap.add_argument("--group", default=None, help="use a lookups.toml waypoint_group instead of STIDs")
    ap.add_argument("--vars", nargs="*", default=MET_VARS)
    ap.add_argument("--out", default=None, help="output parquet path")
    args = ap.parse_args()

    obs = ObsSource()
    if args.group:
        print(f"ObsSource: group={args.group}  {args.start} -> {args.end}")
        df = obs.timeseries(waypoint_group=args.group, start=args.start, end=args.end, variables=args.vars)
        tag = args.group
    else:
        stids = args.stids or BASIN_2013
        print(f"ObsSource: stids={stids}  {args.start} -> {args.end}")
        df = obs.timeseries(stids=stids, start=args.start, end=args.end, variables=args.vars)
        tag = "stids2013"
    print(f"variables={args.vars}")

    print(f"\nrows={df.height}  cols={df.columns}")

    keys = ["waypoint", "stid"] if "waypoint" in df.columns else ["stid"]
    present = [v for v in args.vars if v in df.columns]
    coverage = (
        df.group_by(keys)
        .agg(
            pl.len().alias("n"),
            *[pl.col(v).is_not_null().sum().alias(v) for v in present],
            pl.col("valid_time").min().alias("first"),
            pl.col("valid_time").max().alias("last"),
        )
        .sort("stid")
    )
    with pl.Config(tbl_rows=40, tbl_cols=15):
        print("\nper-station coverage (non-null counts per var):")
        print(coverage)

    missing = [v for v in args.vars if v not in df.columns]
    if missing:
        print("variables not returned at all:", missing)

    out = (
        Path(args.out)
        if args.out
        else Path(__file__).resolve().parents[1] / "data" / f"obs_basin_2013_{tag}.parquet"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(out)
    print(f"\nwrote {df.height} rows -> {out}")


if __name__ == "__main__":
    main()
