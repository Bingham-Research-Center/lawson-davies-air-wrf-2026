#!/usr/bin/env python3
"""Reduce Trang's 2013 baseline WRF (d03) to per-station hourly series for verification.

Reads the staged ``wrfout_d03`` files, finds the nearest d03 grid cell to each Basin obs
station (via XLAT/XLONG), extracts surface met, **rotates 10 m winds to earth-relative**
(COSALPHA/SINALPHA — wrfout U10/V10 are grid-relative), derives wind speed/direction, and
writes a tidy per-station hourly frame keyed ``(waypoint, valid_time)`` — the ``nwp_df``
that ``brc_tools.verify.paired_scores()`` expects.

Output units match the lookups.toml aliases so ``harmonize=True`` converts correctly:
    temp_2m = K, pressure_surface = Pa, wind_speed_10m = m/s, wind_dir_10m = deg, q2 = kg/kg.
``waypoint`` is set to the station id so it joins the obs frame (add ``waypoint=stid`` there).

Run on a CHPC **compute** node (e.g. ``salloc -A lawson-np -p lawson-np -N 1 -n 4 ...``),
reading from scratch. Standalone — needs only xarray + netCDF4 + numpy + pandas, NOT brc_tools.
"""
from __future__ import annotations

import argparse
import glob
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

# 2013-era Basin stations (lat, lon) — from obs_basin_2013_jan1521.parquet.
STATIONS = {
    "USU01": (39.98130, -109.34540),
    "USU05": (40.06700, -110.15100),
    "USU08": (40.14370, -109.46718),
    "KVEL":  (40.44295, -109.51273),
    "QV4":   (40.46472, -109.56083),
    "QRS":   (40.29430, -110.00900),
}


def _decode_time(row) -> str:
    """WRF ``Times`` row (S1 array or bytes) -> 'YYYY-MM-DD_HH:MM:SS'."""
    b = row if isinstance(row, bytes) else row.tobytes()
    return b.decode("ascii", "ignore").strip("\x00").strip()


def nearest_cell(xlat, xlon, lat0, lon0):
    """(j, i) of the grid cell nearest (lat0, lon0); equirectangular distance."""
    dlat = xlat - lat0
    dlon = (xlon - lon0) * np.cos(np.deg2rad(lat0))
    j, i = np.unravel_index(int(np.argmin(dlat * dlat + dlon * dlon)), xlat.shape)
    return int(j), int(i)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wrf-dir", default="/scratch/general/vast/u6060939/wrf_trang_2013")
    ap.add_argument("--glob", default="wrfout_d03_2013-01-*")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    files = sorted(f for f in glob.glob(str(Path(args.wrf_dir) / args.glob))
                   if not f.endswith(".nc"))
    if not files:
        raise SystemExit(f"no wrfout files matched {args.wrf_dir}/{args.glob}")
    print(f"{len(files)} wrfout files")

    # Grid + static fields from the first file (grid is fixed across the run).
    ds0 = xr.open_dataset(files[0], decode_times=False)
    xlat = np.asarray(ds0["XLAT"].isel(Time=0))
    xlon = np.asarray(ds0["XLONG"].isel(Time=0))
    hgt = np.asarray(ds0["HGT"].isel(Time=0))
    cells = {}
    print("station -> nearest d03 cell:")
    for stid, (lat0, lon0) in STATIONS.items():
        j, i = nearest_cell(xlat, xlon, lat0, lon0)
        cells[stid] = (j, i)
        print(f"  {stid}: (j={j}, i={i})  grid {xlat[j,i]:.4f},{xlon[j,i]:.4f}  "
              f"terrain {hgt[j,i]:.0f} m")
    ds0.close()

    rows = []
    for f in files:
        ds = xr.open_dataset(f, decode_times=False)
        valid = pd.to_datetime([_decode_time(t) for t in ds["Times"].values],
                               format="%Y-%m-%d_%H:%M:%S")
        for stid, (j, i) in cells.items():
            sel = dict(south_north=j, west_east=i)
            t2 = np.asarray(ds["T2"].isel(**sel))
            u10 = np.asarray(ds["U10"].isel(**sel))
            v10 = np.asarray(ds["V10"].isel(**sel))
            psfc = np.asarray(ds["PSFC"].isel(**sel))
            q2 = np.asarray(ds["Q2"].isel(**sel))
            cosa = np.asarray(ds["COSALPHA"].isel(**sel))
            sina = np.asarray(ds["SINALPHA"].isel(**sel))
            # grid-relative -> earth-relative (wrf-python uvmet convention)
            ue = u10 * cosa - v10 * sina
            ve = v10 * cosa + u10 * sina
            speed = np.hypot(ue, ve)
            wdir = (270.0 - np.rad2deg(np.arctan2(ve, ue))) % 360.0
            for k in range(len(valid)):
                rows.append({
                    "waypoint": stid,
                    "valid_time": valid[k],
                    "temp_2m": float(t2[k]),
                    "wind_speed_10m": float(speed[k]),
                    "wind_dir_10m": float(wdir[k]),
                    "pressure_surface": float(psfc[k]),
                    "q2": float(q2[k]),
                })
        ds.close()
        print(f"  read {Path(f).name}: {len(valid)} frames")

    df = (pd.DataFrame(rows)
            .sort_values(["waypoint", "valid_time"])
            .reset_index(drop=True))
    out = args.out or str(Path(args.wrf_dir) / "wrf_trang_2013_per_station.csv")
    df.to_csv(out, index=False)
    n_sta = df["waypoint"].nunique()
    print(f"\nwrote {len(df)} rows ({n_sta} stations) -> {out}")
    print(df.groupby("waypoint")["valid_time"].agg(["min", "max", "count"]))


if __name__ == "__main__":
    main()
