#!/usr/bin/env python3
"""Score N WRF runs against the Feb 1-2 2013 Basin obs; per-run skill + inter-run spread.

Multi-run successor to verify_baseline.py. Takes the per-station files that
reduce_wrf_to_stations.py writes (one per run, e.g. the three touchstones gfs_2way /
nam_2way / nam_1way), scores each against the obs with brc_tools paired_scores, and adds
the across-run spread (std + range of each metric per station/variable) — the error-bar
numbers every obs-vs-WRF comparison needs (#24: inter-model spread is IC-driven and large).

Run labels come from the ``run`` column (filename stem as fallback).

Run:
    PYTHONPATH=~/brc-tools python verification/scripts/verify_runs_feb0102.py \\
        --wrf wrf_gfs_2way_per_station.csv wrf_nam_2way_per_station.csv wrf_nam_1way_per_station.csv
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import polars as pl

from brc_tools.verify.deterministic import paired_scores

VARIABLES = ["temp_2m", "wind_speed_10m", "wind_dir_10m", "pressure_surface"]
METRICS = ["bias", "mae", "rmse", "correlation"]
DEFAULT_OBS = Path.home() / "brc-tools/data/obs_basin_2013_feb0102.parquet"
DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data"


def _read(path: Path) -> pl.DataFrame:
    df = pl.read_csv(path, try_parse_dates=True) if path.suffix == ".csv" else pl.read_parquet(path)
    if df["valid_time"].dtype == pl.Utf8:
        df = df.with_columns(pl.col("valid_time").str.to_datetime(strict=False))
    return df.with_columns(pl.col("valid_time").cast(pl.Datetime("us")))


def run_label(df: pl.DataFrame, path: Path) -> str:
    if "run" in df.columns:
        return str(df["run"][0])
    return path.stem.removeprefix("wrf_").removesuffix("_per_station")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wrf", nargs="+", required=True, type=Path,
                    help="per-station csv/parquet files from reduce_wrf_to_stations.py, one per run")
    ap.add_argument("--obs", type=Path, default=DEFAULT_OBS,
                    help="Feb 1-2 2013 obs parquet (local cache)")
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT,
                    help="where the scores + spread csv tables go")
    ap.add_argument("--min-time", default=None,
                    help="drop WRF rows before this valid time (spin-up exclusion), "
                         "e.g. 2013-02-02T14:00")
    ap.add_argument("--out-suffix", default="",
                    help="suffix for the output csv names, e.g. _postspinup")
    args = ap.parse_args()
    min_time = datetime.fromisoformat(args.min_time) if args.min_time else None

    obs = _read(args.obs)
    if "waypoint" not in obs.columns and "stid" in obs.columns:
        obs = obs.with_columns(pl.col("stid").alias("waypoint"))
    print(f"obs: {obs.height} rows, {obs['waypoint'].n_unique()} stations, "
          f"{obs['valid_time'].min()} .. {obs['valid_time'].max()}")

    per_run = []
    for path in args.wrf:
        nwp = _read(path)
        if min_time is not None:
            nwp = nwp.filter(pl.col("valid_time") >= min_time)
        label = run_label(nwp, path)
        present = [v for v in VARIABLES if v in nwp.columns and v in obs.columns]
        scores = paired_scores(nwp.drop("run", strict=False), obs,
                               variables=present, tolerance_minutes=30, harmonize=True)
        per_run.append(scores.with_columns(pl.lit(label).alias("run")))
        print(f"{label}: {nwp.height} nwp rows -> scored {present}")

    scores = pl.concat(per_run).select(["run", "variable", "waypoint", *METRICS, "n_obs"])
    with pl.Config(tbl_rows=400, tbl_width_chars=200):
        print(scores.sort(["variable", "waypoint", "run"]))

    spread = (
        scores.group_by("variable", "waypoint")
        .agg(
            pl.len().alias("n_runs"),
            *[pl.col(m).std().alias(f"{m}_std") for m in METRICS],
            *[(pl.col(m).max() - pl.col(m).min()).alias(f"{m}_range") for m in METRICS],
        )
        .sort("variable", "waypoint")
    )
    if len(args.wrf) > 1:
        with pl.Config(tbl_rows=100, tbl_width_chars=200):
            print("\nAcross-run spread (std / max-min per metric):")
            print(spread)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    scores_out = args.out_dir / f"wrf_runs_scores_feb0102{args.out_suffix}.csv"
    scores.write_csv(scores_out)
    print(f"\nwrote {scores_out}")
    if len(args.wrf) > 1:
        spread_out = args.out_dir / f"wrf_runs_spread_feb0102{args.out_suffix}.csv"
        spread.write_csv(spread_out)
        print(f"wrote {spread_out}")


if __name__ == "__main__":
    main()
