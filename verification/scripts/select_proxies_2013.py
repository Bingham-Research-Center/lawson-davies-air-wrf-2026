#!/usr/bin/env python3
"""Find usable 2013 Uinta Basin proxy observations for the WRF eval (#39, John's ask).

Direct obs are sparse for 2013 (snow_depth is empty from the USU/UDOT sites; ozone/PM
are unavailable). This sweeps candidate proxy variables across the Basin bbox and
CONFIRMS which actually return case-window data via a real pull -- metadata alone lies
(ozone lists period-of-record-covering stations but returns nothing).

Candidates and what they proxy:
    snow_water_equiv   SWE -- snowpack / albedo (cold-pool forcing); Uinta mountain SNOTEL
    snow_depth         snow depth
    solar_radiation    downward shortwave -> cloud-cover proxy
    visibility         fog / inversion-strength proxy
    ozone_concentration, PM_25_concentration  -- AQ target (unavailable for 2013)

Output: verification/data/proxies_2013_availability.csv (per-variable summary + the
usable station list). Bulk proxy obs are NOT written here -- pull those to a local cache.

Env: base conda env (polars + synopticpy) with SYNOPTIC_TOKEN (long-term archive).
The token is never printed: failed Synoptic requests (which echo the token in their URL)
are caught and not logged.
"""
from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

import polars as pl
from synoptic.services import Metadata, TimeSeries

# regions.uinta_basin from brc-tools lookups.toml (lon_min, lat_min, lon_max, lat_max)
BBOX = [-110.9, 39.4, -108.5, 41.1]
DEFAULT_START = "2013-02-01 00:00"
DEFAULT_END = "2013-02-04 00:00"

PROXIES = {
    "snow_water_equiv": "snowpack / albedo (cold-pool forcing)",
    "snow_depth": "snow depth",
    "solar_radiation": "downward shortwave -> cloud cover",
    "visibility": "fog / inversion strength",
    "ozone_concentration": "AQ target",
    "PM_25_concentration": "AQ target",
}


def por_covering(var: str, start_d: dt.date, end_d: dt.date):
    """Basin stations that sense `var` and whose period-of-record covers the case."""
    md = Metadata(bbox=BBOX, vars=var).df()
    if not md.height or not {"period_of_record_start", "period_of_record_end"} <= set(md.columns):
        return md, []
    stids = md.filter(
        (pl.col("period_of_record_start").dt.date() <= end_d)
        & (pl.col("period_of_record_end").dt.date() >= start_d)
    ).get_column("stid").to_list()
    return md, stids


def real_data(stids: list[str], var: str, start: str, end: str):
    """Stations that actually return non-null `var` in the window, and total obs."""
    if not stids:
        return [], 0
    try:
        ts = TimeSeries(stid=stids, start=start, end=end, vars=[var]).df()
    except Exception:
        # No data / no account access. Do NOT log the raw error -- Synoptic echoes the
        # token in the failed request URL. Treat as unusable.
        print(f"  {var}: no 2013 data returned (no data or no account access)")
        return [], 0
    if not ts.height:
        return [], 0
    if {"variable", "value"} <= set(ts.columns):
        got = ts.filter((pl.col("variable") == var) & pl.col("value").is_not_null())
    elif var in ts.columns:
        got = ts.filter(pl.col(var).is_not_null())
    else:
        got = ts
    real = sorted(got.get_column("stid").unique().to_list()) if got.height else []
    return real, got.height


def main() -> None:
    ap = argparse.ArgumentParser(description="Find usable 2013 Basin proxy obs (#39).")
    ap.add_argument("--start", default=DEFAULT_START)
    ap.add_argument("--end", default=DEFAULT_END)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    start_d = dt.datetime.strptime(args.start, "%Y-%m-%d %H:%M").date()
    end_d = dt.datetime.strptime(args.end, "%Y-%m-%d %H:%M").date()

    rows = []
    for var, use in PROXIES.items():
        md, por = por_covering(var, start_d, end_d)
        real, n_obs = real_data(por, var, args.start, args.end)
        rows.append({
            "variable": var,
            "proxies_for": use,
            "n_sense": md.height,
            "n_por_covers_2013": len(por),
            "n_real_data": len(real),
            "n_obs": n_obs,
            "usable": len(real) > 0,
            "stations": ",".join(real),
        })
        print(f"{var:22s} usable={str(len(real) > 0):5s}  real={len(real):2d}/{len(por):2d} POR  obs={n_obs}")

    tbl = pl.DataFrame(rows).sort("usable", descending=True)
    with pl.Config(tbl_rows=20, tbl_cols=10, fmt_str_lengths=40):
        print(tbl.drop("stations"))

    out = (
        Path(args.out)
        if args.out
        else Path(__file__).resolve().parents[1] / "data" / "proxies_2013_availability.csv"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    tbl.write_csv(out)
    print(f"\nwrote proxy availability -> {out}")


if __name__ == "__main__":
    main()
