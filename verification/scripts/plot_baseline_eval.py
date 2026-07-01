#!/usr/bin/env python3
"""Diagnostic figures: Trang 2013 baseline WRF vs Basin obs (Jan 15-21 2013, d03).

Reads the per-station WRF series (reduce_wrf_to_stations.py), the Synoptic obs
(case_study_2013_obs.py), and the scores table (verify_baseline.py), and writes a set
of PNGs to ~/brc-tools/data/figures/:

  1. temp / wind-speed / pressure time series (6-panel, obs vs WRF)
  2. skill bars (bias + RMSE per station, temp/wind/pressure)
  3. WRF-vs-obs temperature scatter (1:1)
  4. diurnal temperature bias (mean WRF-obs by hour) -- diagnoses the cold-pool/nighttime error
  5. deepest-inversion-night temperature zoom

Standalone: needs polars + matplotlib + numpy only. WRF temp is Kelvin -> C; pressure Pa -> hPa.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

DATA = Path.home() / "brc-tools/data"
OUT = DATA / "figures"
OUT.mkdir(parents=True, exist_ok=True)

wrf = (pl.read_csv(DATA / "wrf_trang_2013_per_station.csv", try_parse_dates=True)
       .with_columns(pl.col("valid_time").cast(pl.Datetime("us")),
                     (pl.col("temp_2m") - 273.15).alias("temp_C"),
                     (pl.col("pressure_surface") / 100.0).alias("p_hpa")))
obs = (pl.read_parquet(DATA / "obs_basin_2013_jan1521.parquet")
       .with_columns(pl.col("valid_time").cast(pl.Datetime("us")),
                     (pl.col("pressure_surface") / 100.0).alias("p_hpa"))
       .rename({"stid": "waypoint"}))
scores = pl.read_csv(DATA / "baseline_scores_jan1521.csv")
STATIONS = sorted(set(wrf["waypoint"].unique()) & set(obs["waypoint"].unique()))

# Paired (WRF hourly times, nearest obs within 30 min) for scatter + diurnal.
paired = (wrf.select("waypoint", "valid_time", "temp_C").sort(["waypoint", "valid_time"])
          .join_asof(obs.select("waypoint", "valid_time", obs_temp=pl.col("temp_2m"))
                     .sort(["waypoint", "valid_time"]),
                     on="valid_time", by="waypoint", strategy="nearest", tolerance="30m")
          .drop_nulls(["temp_C", "obs_temp"])
          .with_columns((pl.col("temp_C") - pl.col("obs_temp")).alias("dT"),
                        pl.col("valid_time").dt.hour().alias("hour")))


def _grid():
    fig, axes = plt.subplots(2, 3, figsize=(16, 8), sharex=True)
    return fig, axes


def timeseries(wcol, ocol, ylabel, title, fname, xlim=None):
    # obs resampled to hourly mean to MATCH WRF's native hourly output (WRF shown as-is)
    obs_h = (obs.filter(pl.col(ocol).is_not_null())
             .with_columns(pl.col("valid_time").dt.truncate("1h").alias("valid_time"))
             .group_by(["waypoint", "valid_time"]).agg(pl.col(ocol).mean().alias("o")))
    fig, axes = _grid()
    for ax, st in zip(axes.flat, STATIONS):
        w = wrf.filter(pl.col("waypoint") == st).sort("valid_time")
        o = obs_h.filter(pl.col("waypoint") == st).sort("valid_time")
        ax.plot(o["valid_time"].to_list(), o["o"].to_list(), color="black", lw=1.4, label="obs (hourly mean)")
        ax.plot(w["valid_time"].to_list(), w[wcol].to_list(), color="tab:red", lw=1.5, label="WRF")
        ax.set_title(st)
        ax.grid(alpha=0.3)
        ax.set_ylabel(ylabel)
        if xlim:
            ax.set_xlim(xlim)
    axes.flat[0].legend(loc="upper right", fontsize=8)
    for ax in axes[-1]:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(30); lbl.set_ha("right")
    fig.suptitle(title, fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote", fname)


def skill_bars():
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    panels = [("temp_2m", "bias", "temp bias (°C)"), ("wind_speed_10m", "bias", "wind-spd bias (m/s)"),
              ("pressure_surface", "bias", "pressure bias (Pa)"), ("temp_2m", "rmse", "temp RMSE (°C)"),
              ("wind_speed_10m", "rmse", "wind-spd RMSE (m/s)"), ("pressure_surface", "rmse", "pressure RMSE (Pa)")]
    for ax, (var, metric, lab) in zip(axes.flat, panels):
        d = scores.filter(pl.col("variable") == var).sort("waypoint")
        sts = d["waypoint"].to_list()
        vals = [v if v is not None else np.nan for v in d[metric].to_list()]
        ax.bar(sts, vals, color="tab:blue" if metric == "rmse" else "tab:orange")
        ax.axhline(0, color="k", lw=0.8)
        ax.set_ylabel(lab); ax.grid(alpha=0.3, axis="y")
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(30)
    fig.suptitle("Trang 2013 baseline skill vs obs — per station (wind_dir omitted: needs circular metric)", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT / "baseline_skill_bars_jan1521.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote baseline_skill_bars_jan1521.png")


def scatter_temp():
    fig, ax = plt.subplots(figsize=(7, 7))
    for st in STATIONS:
        d = paired.filter(pl.col("waypoint") == st)
        ax.scatter(d["obs_temp"].to_list(), d["temp_C"].to_list(), s=10, alpha=0.5, label=st)
    lo = min(paired["obs_temp"].min(), paired["temp_C"].min()) - 1
    hi = max(paired["obs_temp"].max(), paired["temp_C"].max()) + 1
    ax.plot([lo, hi], [lo, hi], "k--", lw=1, label="1:1")
    ax.set_xlim(lo, hi); ax.set_ylim(lo, hi); ax.set_aspect("equal")
    ax.set_xlabel("obs 2 m T (°C)"); ax.set_ylabel("WRF 2 m T (°C)")
    ax.set_title(f"WRF vs obs 2 m temperature (overall bias {paired['dT'].mean():+.1f} °C)")
    ax.grid(alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "baseline_temp_scatter_jan1521.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote baseline_temp_scatter_jan1521.png")


def diurnal_bias():
    fig, ax = plt.subplots(figsize=(9, 5))
    for st in STATIONS:
        d = (paired.filter(pl.col("waypoint") == st).group_by("hour").agg(pl.col("dT").mean())
             .sort("hour"))
        ax.plot(d["hour"].to_list(), d["dT"].to_list(), marker="o", ms=3, label=st)
    agg = paired.group_by("hour").agg(pl.col("dT").mean()).sort("hour")
    ax.plot(agg["hour"].to_list(), agg["dT"].to_list(), color="k", lw=2.5, label="all stations")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("hour (UTC; MST = UTC−7, so 14–16 UTC ≈ 7–9 am local)")
    ax.set_ylabel("mean WRF−obs 2 m T (°C)")
    ax.set_title("Diurnal temperature bias — is the warm bias worst overnight (cold pool)?")
    ax.grid(alpha=0.3); ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "baseline_temp_diurnal_bias_jan1521.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote baseline_temp_diurnal_bias_jan1521.png")


def windspeed_matched():
    """10 m wind speed: obs resampled to hourly mean to MATCH WRF's native hourly
    output; WRF shown as-is (not smoothed). Hourly-averaging removes the erratic
    sub-hourly spikes/zeros but keeps genuine calm, so WRF over-windiness still shows."""
    obs_h = (obs.filter(pl.col("wind_speed_10m").is_not_null())
             .with_columns(pl.col("valid_time").dt.truncate("1h").alias("valid_time"))
             .group_by(["waypoint", "valid_time"]).agg(pl.col("wind_speed_10m").mean().alias("ws")))
    fig, axes = _grid()
    for ax, st in zip(axes.flat, STATIONS):
        o = obs_h.filter(pl.col("waypoint") == st).sort("valid_time")
        w = wrf.filter(pl.col("waypoint") == st).sort("valid_time")
        ax.plot(o["valid_time"].to_list(), o["ws"].to_list(), color="black", lw=1.4, label="obs (hourly mean)")
        ax.plot(w["valid_time"].to_list(), w["wind_speed_10m"].to_list(), color="tab:red", lw=1.5, label="WRF (hourly)")
        ax.set_title(st)
        ax.grid(alpha=0.3)
        ax.set_ylabel("10 m wind (m/s)")
    axes.flat[0].legend(loc="upper right", fontsize=8)
    for ax in axes[-1]:
        for lbl in ax.get_xticklabels():
            lbl.set_rotation(30)
            lbl.set_ha("right")
    fig.suptitle("Trang 2013 baseline WRF vs obs — 10 m wind speed (obs hourly-mean, matched to WRF's hourly output)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "baseline_windspeed_timeseries_jan1521.png", dpi=130, bbox_inches="tight")
    plt.close(fig)
    print("wrote baseline_windspeed_timeseries_jan1521.png (obs hourly-mean, WRF native)")


if __name__ == "__main__":
    timeseries("temp_C", "temp_2m", "2 m T (°C)",
               "Trang 2013 baseline WRF vs obs — 2 m temperature (Jan 15–21 2013, d03)",
               "baseline_temp_timeseries_jan1521.png")
    windspeed_matched()
    timeseries("p_hpa", "p_hpa", "sfc pressure (hPa)",
               "Trang 2013 baseline WRF vs obs — surface pressure (USU01/05/08 + KVEL report pressure)",
               "baseline_pressure_timeseries_jan1521.png")
    skill_bars()
    scatter_temp()
    diurnal_bias()
    # deepest-inversion-night zoom: ±18 h around the coldest obs temperature
    t0 = obs.filter(pl.col("temp_2m") == obs["temp_2m"].min())["valid_time"][0]
    import datetime as _dt
    win = (t0 - _dt.timedelta(hours=18), t0 + _dt.timedelta(hours=18))
    timeseries("temp_C", "temp_2m", "2 m T (°C)",
               f"Deepest-inversion window — 2 m temperature (around {t0:%Y-%m-%d %HZ})",
               "baseline_inversion_night_zoom_jan1521.png", xlim=win)
    print("\nAll figures ->", OUT)
