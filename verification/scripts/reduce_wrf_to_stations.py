#!/usr/bin/env python3
"""Reduce a 2013-case WRF run (innermost domain) to per-station hourly series.

Reads staged ``wrfout`` files, finds the nearest grid cell to each Basin obs station
(via XLAT/XLONG), extracts surface met, **rotates 10 m winds to earth-relative**
(COSALPHA/SINALPHA — wrfout U10/V10 are grid-relative), derives wind speed/direction, and
writes a tidy per-station hourly frame keyed ``(waypoint, valid_time)`` — the ``nwp_df``
that ``brc_tools.verify.paired_scores()`` expects.

Stations come from ``verification/data/stations_2013_selection.csv`` (rows with
``in_case_window=true``; pass ``--stations`` if the CSV lives elsewhere). ``--run-label``
names the run (e.g. gfs_2way / nam_2way / nam_1way); it becomes a ``run`` column and the
default output filename, so the three touchstone runs reduce with the same command.

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

DEFAULT_STATIONS_CSV = Path(__file__).resolve().parents[1] / "data" / "stations_2013_selection.csv"


def load_stations(csv_path: Path) -> dict[str, tuple[float, float]]:
    """stid -> (lat, lon) for stations reporting in the case window."""
    meta = pd.read_csv(csv_path)
    meta = meta[meta["in_case_window"]]
    return {r.stid: (float(r.latitude), float(r.longitude)) for r in meta.itertuples()}


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
    ap.add_argument("--wrf-dir", required=True, help="directory holding the run's wrfout files")
    ap.add_argument("--run-label", required=True,
                    help="run name for the output (e.g. gfs_2way, nam_2way, nam_1way, trang)")
    ap.add_argument("--glob", default="wrfout_d03_2013-0[12]-*",
                    help="wrfout pattern; d03 = innermost of the triple nest (override per run layout)")
    ap.add_argument("--stations", type=Path, default=DEFAULT_STATIONS_CSV,
                    help="stations_2013_selection.csv (copied next to this script on CHPC is fine)")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    stations = load_stations(args.stations)
    print(f"{len(stations)} stations from {args.stations}")

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
    print("station -> nearest grid cell:")
    for stid, (lat0, lon0) in stations.items():
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
                    "run": args.run_label,
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
    out = args.out or str(Path(args.wrf_dir) / f"wrf_{args.run_label}_per_station.csv")
    df.to_csv(out, index=False)
    n_sta = df["waypoint"].nunique()
    print(f"\nwrote {len(df)} rows ({n_sta} stations) -> {out}")
    print(df.groupby("waypoint")["valid_time"].agg(["min", "max", "count"]))


if __name__ == "__main__":
    main()
