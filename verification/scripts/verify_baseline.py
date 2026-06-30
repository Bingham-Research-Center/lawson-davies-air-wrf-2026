#!/usr/bin/env python3
"""Score Trang's 2013 baseline WRF against Basin obs (Jan 15-21 2013).

Loads the per-station WRF series (reduce_wrf_to_stations.py) and the Synoptic obs
(case_study_2013_obs.py), aligns them on (waypoint, valid_time), and prints
deterministic skill per station, per variable via brc_tools.verify.paired_scores.

The obs frame is keyed by ``stid`` while paired_scores joins on ``waypoint``; the WRF
reduction already labels its waypoints by station id, so we set obs.waypoint = obs.stid.
``harmonize=True`` converts the WRF side to obs units (temp_2m K->C; pressure already Pa
both sides; wind needs none).
"""
from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl

from brc_tools.verify.deterministic import paired_scores

VARIABLES = ["temp_2m", "wind_speed_10m", "wind_dir_10m", "pressure_surface"]


def _read(path: str) -> pl.DataFrame:
    p = Path(path)
    df = pl.read_csv(p, try_parse_dates=True) if p.suffix == ".csv" else pl.read_parquet(p)
    if df["valid_time"].dtype == pl.Utf8:
        df = df.with_columns(pl.col("valid_time").str.to_datetime(strict=False))
    return df.with_columns(pl.col("valid_time").cast(pl.Datetime("us")))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wrf", default="/scratch/general/vast/u6060939/wrf_trang_2013/wrf_trang_2013_per_station.csv",
                    help="per-station WRF csv/parquet from reduce_wrf_to_stations.py")
    ap.add_argument("--obs", required=True,
                    help="obs csv/parquet from case_study_2013_obs.py (Jan 15-21 2013)")
    ap.add_argument("--out", default=None, help="write the scores table to this csv")
    args = ap.parse_args()

    nwp = _read(args.wrf)
    obs = _read(args.obs)
    if "waypoint" not in obs.columns and "stid" in obs.columns:
        obs = obs.with_columns(pl.col("stid").alias("waypoint"))

    present = [v for v in VARIABLES if v in nwp.columns and v in obs.columns]
    print(f"WRF: {nwp.height} rows, {nwp['waypoint'].n_unique()} stations, {nwp['valid_time'].min()} .. {nwp['valid_time'].max()}")
    print(f"obs: {obs.height} rows, {obs['waypoint'].n_unique()} stations, {obs['valid_time'].min()} .. {obs['valid_time'].max()}")
    print(f"verifying: {present}")

    scores = paired_scores(nwp, obs, variables=present, tolerance_minutes=30, harmonize=True)
    with pl.Config(tbl_rows=200, tbl_width_chars=200):
        print(scores.sort(["variable", "waypoint"]))

    if args.out:
        scores.write_csv(args.out)
        print(f"wrote scores -> {args.out}")


if __name__ == "__main__":
    main()
