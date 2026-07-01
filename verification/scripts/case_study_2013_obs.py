#!/usr/bin/env python3
"""Pull Uinta Basin station obs for the 2013 wintertime-ozone case study.

Exercises the ObsSource path (previously untested in brc-tools, PR #16) and
produces a tidy obs frame for WRF verification against the validated Feb-2013
Basin run.

IMPORTANT — station-ID drift: the lookups.toml waypoint_groups are built for the
*modern* network, and most of those STIDs (UB7ST, UBHSP, A3822, ...) have NO 2013
data. In Feb 2013 the BRC research network reported under USU01-USU08 / UUT01, so
this script defaults to a curated 2013-era station list (BASIN_2013) instead of a
group. Verified to return data for Feb 2013:
    USU01 Seven Sisters · USU05 Wells Draw · USU08 Research Trailer · UUT01 Basin
    Research Trailer · KVEL Vernal Airport (full met incl. pressure)
    QV4 Vernal · QRS Roosevelt (UDOT: temp/wind, NO surface pressure)

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

# Curated 2013-era basin-floor stations (verified to return Feb-2013 data).
BASIN_2013 = ["USU01", "USU05", "USU08", "UUT01", "KVEL", "QV4", "QRS"]

DEFAULT_START = "2013-02-01 00Z"
DEFAULT_END = "2013-02-15 00Z"
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
