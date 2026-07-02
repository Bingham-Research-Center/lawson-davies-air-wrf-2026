#!/usr/bin/env python3
"""Smoke test for plot_wrf_cross_sections.py against a tiny synthetic wrfout.

Builds two fake wrfout files (Basin-covering lat/lon grid, 12 mass levels, an idealized
surface-based inversion that weakens between time steps) and runs the cross-section
script on them, so the real invocation on CHPC is known-good syntax-to-figure.

Run:
    python verification/scripts/smoke_test_cross_sections.py
Everything goes to a temp dir; nothing in the repo is touched.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import xarray as xr

SCRIPTS = Path(__file__).resolve().parent
G, NZ, NY, NX = 9.81, 12, 30, 30


def fake_wrfout(path: Path, stamps: list[str], inv_strength: float) -> None:
    nt = len(stamps)
    lat = np.linspace(39.7, 40.6, NY)
    lon = np.linspace(-110.5, -109.2, NX)
    xlon, xlat = np.meshgrid(lon, lat)
    hgt = 1450.0 + 800.0 * ((xlat - 39.7) / 0.9) ** 2  # floor rising to a NW bench

    z_stag = hgt[None, :, :] + np.linspace(0.0, 4000.0, NZ + 1)[:, None, None]
    ph_stag = np.broadcast_to(z_stag * G, (nt, NZ + 1, NY, NX)).copy()
    z_mass = 0.5 * (z_stag[:-1] + z_stag[1:])
    agl = z_mass - hgt[None, :, :]
    # theta: 300 K aloft, colder near the surface (the inversion), decaying with AGL height
    theta_pert = -inv_strength * np.exp(-agl / 500.0)
    t = np.stack([theta_pert * (1.0 - 0.3 * k) for k in range(nt)])  # weakens in time

    times = np.array([list(s.ljust(19)) for s in stamps], dtype="S1")
    ds = xr.Dataset(
        {
            "Times": (("Time", "DateStrLen"), times),
            "XLAT": (("Time", "south_north", "west_east"), np.broadcast_to(xlat, (nt, NY, NX))),
            "XLONG": (("Time", "south_north", "west_east"), np.broadcast_to(xlon, (nt, NY, NX))),
            "HGT": (("Time", "south_north", "west_east"), np.broadcast_to(hgt, (nt, NY, NX))),
            "T": (("Time", "bottom_top", "south_north", "west_east"), t),
            "PH": (("Time", "bottom_top_stag", "south_north", "west_east"), np.zeros_like(ph_stag)),
            "PHB": (("Time", "bottom_top_stag", "south_north", "west_east"), ph_stag),
        }
    )
    ds.to_netcdf(path, format="NETCDF4")


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="wrf_xsect_smoke_"))
    fake_wrfout(tmp / "wrfout_d03_2013-02-01_12:00:00", ["2013-02-01_12:00:00"], 12.0)
    fake_wrfout(tmp / "wrfout_d03_2013-02-02_12:00:00", ["2013-02-02_12:00:00"], 8.0)

    cmd = [sys.executable, str(SCRIPTS / "plot_wrf_cross_sections.py"),
           "--wrf-dir", str(tmp), "--run-label", "fake",
           "--times", "2013-02-01_12:00:00", "2013-02-02_12:00:00"]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

    for stem in ("wrf_xsect_theta_fake", "wrf_timeheight_theta_fake"):
        f = tmp / "figures" / f"{stem}.png"
        assert f.exists() and f.stat().st_size > 10_000, f"missing/empty {f}"
    print(f"\nOK: both cross-section figures rendered -> {tmp}/figures")


if __name__ == "__main__":
    main()
