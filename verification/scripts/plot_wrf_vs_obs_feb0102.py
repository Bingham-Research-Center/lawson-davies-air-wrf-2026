#!/usr/bin/env python3
"""WRF-vs-obs overlay figures for the Feb 1-2 2013 cold-air-pool episode.

Companion to plot_obs_feb0102.py (whose styling/helpers it reuses): same conventions,
now with N WRF runs (the gfs_2way / nam_2way / nam_1way touchstones) overlaid on the
observed episode. Two figures:

1. wrf_temp_timeseries_feb0102 -- 2 m temperature at the 4 floor->bench stations
   (one panel each): obs in black, one line per run, min-max across runs shaded.
   The shaded band IS the IC-driven inter-run spread (#24) at each station.
2. wrf_inversion_index_feb0102 -- bench-minus-floor delta-theta (USU03 - USU07):
   does each run HOLD the cold pool (stay above the 8 K CAP threshold) or mix it
   out like the Jan baseline's +4-6 C warm bias implies?

Inputs are the per-station files from reduce_wrf_to_stations.py (WRF units: temp K,
pressure Pa; converted here). Obs stays local, figures are tracked like the obs set.

Run:
    PYTHONPATH=~/brc-tools python verification/scripts/plot_wrf_vs_obs_feb0102.py \\
        --wrf wrf_gfs_2way_per_station.csv wrf_nam_2way_per_station.csv ...
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import polars as pl

from plot_obs_feb0102 import (
    DEFAULT_OBS, KAPPA, TS_STATIONS, UTC_TO_MST,
    elev_color, load, panel_letter, save, shade_nights, style_axes,
)
from verify_runs_feb0102 import _read, run_label

# Okabe-Ito, CVD-safe; obs stays black.
RUN_COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00"]
BENCH, FLOOR = "USU03", "USU07"  # Mountain Home (2228 m) minus Pariette Draw (1465 m)


def load_runs(paths: list[Path]) -> pl.DataFrame:
    """Per-station WRF files -> one hourly-MST frame with run, theta, temp in C."""
    frames = []
    for p in paths:
        df = _read(p)
        frames.append(df.with_columns(pl.lit(run_label(df, p)).alias("run")))
    return (
        pl.concat(frames, how="diagonal")
        .with_columns(
            pl.col("valid_time").dt.offset_by(f"{UTC_TO_MST}h").dt.truncate("1h").alias("hour_mst"),
            (pl.col("temp_2m") - 273.15).alias("temp_c"),
            ((pl.col("temp_2m")) * (1000.0 / (pl.col("pressure_surface") / 100.0)) ** KAPPA)
            .alias("theta"),
        )
        .sort("run", "waypoint", "hour_mst")
    )


def x_axis_days(ax) -> None:
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[12]))
    ax.tick_params(axis="x", which="major", length=7)


def fig_temp_timeseries(wrf: pl.DataFrame, hourly: pl.DataFrame, names: dict,
                        runs: list[str]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(9.5, 6.2), sharex=True, sharey=True)
    t_min = min(hourly["hour_mst"].min(), wrf["hour_mst"].min())
    t_max = max(hourly["hour_mst"].max(), wrf["hour_mst"].max())
    for ax, st, letter in zip(axes.flat, TS_STATIONS, "abcd"):
        shade_nights(ax, t_min, t_max)
        w = wrf.filter(pl.col("waypoint") == st)
        band = (w.group_by("hour_mst")
                 .agg(pl.col("temp_c").min().alias("lo"), pl.col("temp_c").max().alias("hi"))
                 .sort("hour_mst"))
        if band.height and len(runs) > 1:
            ax.fill_between(band["hour_mst"], band["lo"], band["hi"],
                            color="0.55", alpha=0.25, lw=0, zorder=1,
                            label="run spread (min-max)")
        for run, color in zip(runs, RUN_COLORS):
            d = w.filter(pl.col("run") == run)
            ax.plot(d["hour_mst"], d["temp_c"], color=color, lw=1.1, zorder=2, label=run)
        o = hourly.filter((pl.col("stid") == st) & pl.col("temp_2m").is_not_null())
        ax.plot(o["hour_mst"], o["temp_2m"], color="black", lw=1.5, zorder=3, label="obs")
        ax.axhline(0.0, color="0.7", lw=0.8, zorder=1)
        ev = names[st]["elev_m"]
        panel_letter(ax, letter, f"{names[st]['name']} ({ev:.0f} m)")
        ax.set_xlim(t_min, t_max)
        x_axis_days(ax)
        style_axes(ax)
    for ax in axes[:, 0]:
        ax.set_ylabel("2 m temperature (°C)")
    for ax in axes[1, :]:
        ax.set_xlabel("Local time (MST); shaded = night")
    axes.flat[0].legend(loc="lower right", ncols=1)
    fig.tight_layout()
    save(fig, "wrf_temp_timeseries_feb0102")


def _dtheta(df: pl.DataFrame, key: str, group: list[str]) -> pl.DataFrame:
    both = (
        df.filter(pl.col(key).is_in([BENCH, FLOOR]) & pl.col("theta").is_finite())
        .pivot(on=key, index=group, values="theta")
    )
    if BENCH not in both.columns or FLOOR not in both.columns:
        return pl.DataFrame()
    return (both.drop_nulls([BENCH, FLOOR])
                .with_columns((pl.col(BENCH) - pl.col(FLOOR)).alias("dtheta"))
                .sort(group))


def fig_inversion_index(wrf: pl.DataFrame, hourly: pl.DataFrame, runs: list[str]) -> None:
    obs_d = _dtheta(hourly, "stid", ["hour_mst"])
    fig, ax = plt.subplots(figsize=(9, 3.8))
    t_min, t_max = obs_d["hour_mst"].min(), obs_d["hour_mst"].max()
    shade_nights(ax, t_min, t_max)
    for run, color in zip(runs, RUN_COLORS):
        d = _dtheta(wrf.filter(pl.col("run") == run), "waypoint", ["hour_mst"])
        if d.height:
            ax.plot(d["hour_mst"], d["dtheta"], color=color, lw=1.1, zorder=2, label=run)
    ax.plot(obs_d["hour_mst"], obs_d["dtheta"], color="black", lw=1.5, zorder=3, label="obs")
    ax.axhline(8.0, color="0.4", lw=1.0, ls="--")
    ax.annotate("8 K CAP threshold", xy=(0.99, 8.0), xycoords=("axes fraction", "data"),
                xytext=(0, -10), textcoords="offset points", fontsize=8, color="0.35",
                ha="right", va="top")
    ax.set_ylabel("Δθ bench − floor (K)")
    ax.set_xlabel("Local time (MST); shaded = night")
    ax.set_xlim(t_min, t_max)
    x_axis_days(ax)
    ax.legend(loc="upper left")
    style_axes(ax)
    fig.tight_layout()
    save(fig, "wrf_inversion_index_feb0102")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--wrf", nargs="+", required=True, type=Path,
                    help="per-station csv/parquet files from reduce_wrf_to_stations.py, one per run")
    ap.add_argument("--obs", type=Path, default=DEFAULT_OBS)
    args = ap.parse_args()

    hourly, names = load(args.obs)
    wrf = load_runs(args.wrf)
    runs = wrf["run"].unique(maintain_order=True).to_list()
    print(f"runs: {runs}; WRF stations: {sorted(wrf['waypoint'].unique().to_list())}")

    fig_temp_timeseries(wrf, hourly, names, runs)
    fig_inversion_index(wrf, hourly, runs)


if __name__ == "__main__":
    main()
