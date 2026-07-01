#!/usr/bin/env python3
"""Select 2013 Uinta Basin verification stations by matching the Tran et al. (2018)
evaluation sites to Synoptic STIDs, then confirm real data in the case window.

Tran et al. (2018, Atmos. Environ. 177:75-92) evaluated WRF against 7 "representative"
BRC-USU surface sites. Those sites are the temporary BRC study-period stations in
Synoptic (USU01-USU07), live only ~Jan-Mar 2013 -- exactly this case. Their names,
coords and elevations are authoritative in Synoptic metadata, so we do NOT need the
coordinates from Lyman & Tran (2015).

Two gotchas this guards against:
- Name drift: the paper labels USU04 "Sego Ridge" and USU06 "Dry Wash"; Synoptic
  reports "Seep Ridge" and "Sand Wash" (same sites, paper typos).
- Metadata != data: a station's period-of-record can span the case while the actual
  timeseries has a gap. USU06 (Sand Wash) is live proof -- metadata says 2013, but the
  pull is empty Jan 28-Feb 4 2013 (first data Feb 5), so it drops for the Feb 1-2 episode.

Output: a selection/availability table -> verification/data/stations_2013_selection.csv
plus a printed recommended station list (those with data in the case window).

Env: needs synopticpy + brc_tools importable and SYNOPTIC_TOKEN with the long-term
archive (2013). The base conda env carries both; run with PYTHONPATH=~/brc-tools.

Examples:
    PYTHONPATH=~/brc-tools python scripts/select_stations_2013.py
    PYTHONPATH=~/brc-tools python scripts/select_stations_2013.py --start "2013-02-05 00Z" --end "2013-02-08 00Z"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import polars as pl
from synoptic.services import Metadata

from brc_tools.obs import ObsSource

# Tran (2018) eval site -> Synoptic STID. Names as Synoptic reports them (paper typos
# noted). USU01-USU07 are the paper's 7 "representative" BRC sites.
PAPER_EVAL_SITES = {
    "USU01": "Seven Sisters",
    "USU02": "Gusher",
    "USU03": "Mountain Home",
    "USU04": "Seep Ridge",      # paper: "Sego Ridge"
    "USU05": "Wells Draw",
    "USU06": "Sand Wash",       # paper: "Dry Wash"
    "USU07": "Pariette Draw",
}
# Basin-floor context stations (not among the paper's 7 but useful coverage;
# KVEL carries surface pressure). Superset of the prior BASIN_2013.
CONTEXT_SITES = ["USU08", "UUT01", "KVEL", "QV4", "QRS"]

M_PER_FT = 0.3048
DEFAULT_START = "2013-02-01 00Z"
DEFAULT_END = "2013-02-03 00Z"   # brackets the Feb 1-2 high-ozone episode
PROBE_VARS = ["temp_2m", "wind_speed_10m", "pressure_surface"]


def main() -> None:
    ap = argparse.ArgumentParser(description="Select/verify 2013 Basin stations.")
    ap.add_argument("--start", default=DEFAULT_START, help="case-window start")
    ap.add_argument("--end", default=DEFAULT_END, help="case-window end")
    ap.add_argument("--out", default=None, help="output CSV path")
    args = ap.parse_args()

    stids = list(PAPER_EVAL_SITES) + CONTEXT_SITES

    # 1) Authoritative metadata: name, coords, elevation (ft -> m), period of record.
    meta = Metadata(stid=stids).df().select(
        "stid",
        "name",
        "latitude",
        "longitude",
        (pl.col("elevation") * M_PER_FT).round(0).alias("elev_m"),
        pl.col("period_of_record_start").alias("por_start"),
        pl.col("period_of_record_end").alias("por_end"),
    )

    # 2) Case-window availability -- an actual pull, not just metadata (the gate).
    obs = ObsSource()
    got = obs.timeseries(stids=stids, start=args.start, end=args.end, variables=PROBE_VARS)
    avail = got.group_by("stid").agg(pl.len().alias("n_case"))

    paper = pl.DataFrame(
        {"stid": list(PAPER_EVAL_SITES), "paper_site": list(PAPER_EVAL_SITES.values())}
    )

    tbl = (
        meta.join(avail, on="stid", how="left")
        .join(paper, on="stid", how="left")
        .with_columns(pl.col("n_case").fill_null(0))
        .with_columns((pl.col("n_case") > 0).alias("in_case_window"))
        .sort("elev_m")
    )

    with pl.Config(tbl_rows=30, tbl_cols=12, fmt_str_lengths=32):
        print(tbl)

    kept = tbl.filter("in_case_window").get_column("stid").to_list()
    dropped = tbl.filter(~pl.col("in_case_window")).get_column("stid").to_list()
    print(f"\nrecommended for {args.start} .. {args.end} (by elevation): {kept}")
    if dropped:
        print(f"dropped -- no data in window (sensor gap): {dropped}")

    out = (
        Path(args.out)
        if args.out
        else Path(__file__).resolve().parents[1] / "data" / "stations_2013_selection.csv"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    tbl.write_csv(out)
    print(f"wrote selection table -> {out}")


if __name__ == "__main__":
    main()
