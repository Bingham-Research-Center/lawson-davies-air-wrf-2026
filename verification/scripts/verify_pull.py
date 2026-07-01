#!/usr/bin/env python3
"""Verification gate on a pulled obs parquet (see verification/README.md).

Confirms station coverage and that temp/pressure/wind units are physical, before the
obs are trusted for scoring. Obs data stays LOCAL -- pass the parquet path; this
script only reads, it never writes to the repo.

Example:
    python verification/scripts/verify_pull.py \\
        ~/brc-tools/data/obs_basin_2013_feb0102.parquet \\
        --expected USU01 USU02 USU03 USU04 USU05 USU06 USU07 USU08 UUT01 KVEL QV4 QRS
"""
from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl


def main() -> None:
    ap = argparse.ArgumentParser(description="QC a pulled obs parquet (local, not in-repo).")
    ap.add_argument("parquet", help="path to the local obs parquet")
    ap.add_argument("--expected", nargs="*", default=None,
                    help="expected STIDs; report any that are absent")
    args = ap.parse_args()

    df = pl.read_parquet(Path(args.parquet).expanduser())
    print(f"rows={df.height}")
    present = sorted(df.get_column("stid").unique().to_list())
    print("present:", present)
    if args.expected:
        absent = [s for s in args.expected if s not in present]
        print("absent (expected):", absent)
        if absent:
            raise SystemExit(2)

    aggs = [pl.len().alias("n")]
    for v in ("temp_2m", "pressure_surface", "wind_speed_10m"):
        if v in df.columns:
            aggs += [
                pl.col(v).min().round(1).alias(f"{v}_min"),
                pl.col(v).max().round(1).alias(f"{v}_max"),
            ]
    # Unit sanity: fail fast if values look like the wrong units (e.g., K vs °C, hPa vs Pa).
    ranges = {
        "temp_2m": (-80.0, 60.0),              # °C
        "pressure_surface": (7.5e4, 1.1e5),    # Pa
        "wind_speed_10m": (0.0, 60.0),         # m/s
    }
    bad = []
    for col, (lo, hi) in ranges.items():
        if col in df.columns:
            mn, mx = df.select(pl.col(col).min(), pl.col(col).max()).row(0)
            if (mn is not None and mn < lo) or (mx is not None and mx > hi):
                bad.append(f"{col} min={mn} max={mx} (expected {lo}..{hi})")
    if bad:
        raise SystemExit("unit sanity check failed: " + "; ".join(bad))

    summ = df.group_by("stid").agg(aggs).sort("stid")
    with pl.Config(tbl_rows=30, tbl_cols=12):
        print(summ)


if __name__ == "__main__":
    main()
