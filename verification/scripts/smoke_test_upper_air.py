#!/usr/bin/env python3
"""Smoke test for plot_wrf_upper_air.py against tiny synthetic wrfouts.

Two fake runs on the same grid (one uniformly warmer aloft), so both the plain
theta+wind maps and the --diff-dir difference panel are exercised end-to-end.

Run:
    python verification/scripts/smoke_test_upper_air.py
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
NZ, NY, NX = 12, 30, 30
P0, H_SCALE = 101325.0, 8434.0


def fake_wrfout(path: Path, stamp: str, warm_offset: float) -> None:
    lat = np.linspace(39.7, 40.6, NY)
    lon = np.linspace(-110.5, -109.2, NX)
    xlon, xlat = np.meshgrid(lon, lat)
    hgt = 1450.0 + 800.0 * ((xlat - 39.7) / 0.9) ** 2

    z_mass = hgt[None, :, :] + np.linspace(150.0, 4200.0, NZ)[:, None, None]
    p_full = P0 * np.exp(-z_mass / H_SCALE)
    theta_pert = warm_offset + 4.0 * (z_mass - 1500.0) / 3000.0  # stable profile
    u = np.full((NZ, NY, NX + 1), 3.0)
    v = np.full((NZ, NY + 1, NX), -1.0)

    times = np.array([list(stamp.ljust(19))], dtype="S1")
    e = lambda a: a[None]  # add Time dim
    ds = xr.Dataset(
        {
            "Times": (("Time", "DateStrLen"), times),
            "XLAT": (("Time", "south_north", "west_east"), e(xlat)),
            "XLONG": (("Time", "south_north", "west_east"), e(xlon)),
            "HGT": (("Time", "south_north", "west_east"), e(hgt)),
            "T": (("Time", "bottom_top", "south_north", "west_east"), e(theta_pert)),
            "P": (("Time", "bottom_top", "south_north", "west_east"), e(np.zeros_like(p_full))),
            "PB": (("Time", "bottom_top", "south_north", "west_east"), e(p_full)),
            "U": (("Time", "bottom_top", "south_north", "west_east_stag"), e(u)),
            "V": (("Time", "bottom_top", "south_north_stag", "west_east"), e(v)),
        }
    )
    ds.to_netcdf(path, format="NETCDF4")


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="wrf_upper_smoke_"))
    (tmp / "runA").mkdir(), (tmp / "runB").mkdir()
    fake_wrfout(tmp / "runA" / "wrfout_d03_2013-02-02_16:00:00", "2013-02-02_16:00:00", 2.0)
    fake_wrfout(tmp / "runB" / "wrfout_d03_2013-02-02_16:00:00", "2013-02-02_16:00:00", 0.0)

    base = [sys.executable, str(SCRIPTS / "plot_wrf_upper_air.py"),
            "--times", "2013-02-02_16:00:00", "--levels", "700"]
    for extra in (["--wrf-dir", str(tmp / "runA"), "--run-label", "fake"],
                  ["--wrf-dir", str(tmp / "runA"), "--run-label", "fake_diff",
                   "--diff-dir", str(tmp / "runB")]):
        cmd = base + extra
        print(f"$ {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

    diff_expected = 2.0
    for stem in ("wrf_upper_700hPa_fake", "wrf_upper_700hPa_fake_diff"):
        f = tmp / "runA" / "figures" / f"{stem}.png"
        assert f.exists() and f.stat().st_size > 10_000, f"missing/empty {f}"
    print(f"\nOK: theta map + difference panel rendered (expected uniform Δθ ≈ "
          f"{diff_expected} K) -> {tmp}/runA/figures")


if __name__ == "__main__":
    main()
