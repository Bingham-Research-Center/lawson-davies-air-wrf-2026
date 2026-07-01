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
        print("absent (expected):", [s for s in args.expected if s not in present])

    aggs = [pl.len().alias("n")]
    for v in ("temp_2m", "pressure_surface", "wind_speed_10m"):
        if v in df.columns:
            aggs += [
                pl.col(v).min().round(1).alias(f"{v}_min"),
                pl.col(v).max().round(1).alias(f"{v}_max"),
            ]
    summ = df.group_by("stid").agg(aggs).sort("stid")
    with pl.Config(tbl_rows=30, tbl_cols=12):
        print(summ)


if __name__ == "__main__":
    main()
