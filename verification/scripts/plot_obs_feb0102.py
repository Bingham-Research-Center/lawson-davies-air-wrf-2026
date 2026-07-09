#!/usr/bin/env python3
"""Observed-case figures for the Feb 1-2 2013 Uinta Basin cold-air-pool episode.

Three obs-only figures (WRF overlays come later, when the Feb runs land), following
the CAP-literature conventions -- esp. Neemann et al. 2015 (ACP 15:135-151; the SAME
31 Jan-6 Feb 2013 case), Lyman & Tran 2015 (Atmos. Environ. 123, Figs. 5/7/8), and
Whiteman & Hoch 2014 (JAMC 53, pseudo-vertical profiles):

1. obs_theta_profiles_feb0102.png -- pseudo-vertical potential-temperature profiles:
   theta vs station elevation at snapshot times across the episode. theta (not raw T)
   so a well-mixed layer reads vertical and inversion strength reads directly.
   Caveat (Whiteman & Hoch): surface stations run colder than free air at night and
   warmer by day; midday panels are the most representative.
2. obs_temp_timeseries_feb0102.png -- 2 m temperature at 4 stations spanning the
   basin floor -> bench (1465 -> 2228 m), colored by a sequential elevation ramp
   (cividis clamped to [0, 0.6]; CVD- and print-safe, all lines >= 3:1 on white)
   with distinct line styles as secondary encoding. Midnight (MST) ticks.
3. obs_inversion_index_feb0102.png -- CAP bulk metrics: bench-minus-floor
   delta-theta (PCAPS 8 K threshold marked) and the valley heat deficit
   H = sum rho*cp*(theta_top - theta)*dz integrated over the station pseudo-profile.

Data stays LOCAL: reads the obs parquet from the local cache (never committed; the
repo gitignores *.parquet). Figures are small tracked PNGs like the baseline set.

Run:
    PYTHONPATH=~/brc-tools python verification/scripts/plot_obs_feb0102.py
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import polars as pl

# Journal style: captions live in the manuscript, so figures carry no titles;
# panels get letters. PDF (vector) is the LaTeX deliverable, PNG the quick look.
# Helvetica with per-glyph fallback; fonttype 42 = TrueType so PDF text stays
# editable/searchable (journals reject Type-3).
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica", "Helvetica Neue", "Arial", "DejaVu Sans"],
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "mathtext.fontset": "stixsans",
    "font.size": 9,
    "axes.labelsize": 9.5,
    "axes.linewidth": 0.8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "legend.frameon": True,
    "legend.framealpha": 0.9,
    "legend.edgecolor": "0.85",
    "xtick.direction": "out",
    "ytick.direction": "out",
})

# Figures are drawn at TRUE print size (MDPI full text width ~16 cm = 6.3 in) so the
# point sizes above are what the reader sees; PNGs export at MDPI's 600 dpi minimum.
FULL_W = 6.3

REPO = Path(__file__).resolve().parents[1]
DEFAULT_OBS = Path.home() / "brc-tools/data/obs_basin_2013_feb0102.parquet"
META_CSV = REPO / "data" / "stations_2013_selection.csv"
OUT = REPO / "data" / "figures"

KAPPA = 0.2854
CP = 1004.0  # J kg-1 K-1
RD = 287.05  # J kg-1 K-1
UTC_TO_MST = -7  # hours; plot axes in local standard time

# Representative floor->bench set for the timeseries (evenly spaced in elevation).
TS_STATIONS = ["USU07", "USU05", "USU04", "USU03"]
TS_STYLES = ["-", "--", "-.", ":"]
# cividis sampled at [0, 0.6] over 1465-2228 m; validated (CVD >= 16, contrast >= 3:1).
ELEV_CMAP = matplotlib.colormaps["cividis"]
ELEV_RANGE = (1465.0, 2228.0)
ELEV_CLAMP = 0.60

# Pseudo-profile snapshot times (MST) across the episode lifecycle: night/day pairs
# while the CAP deepens, then late-episode midday.
SNAPSHOTS_MST = [
    "2013-01-31 13:00",
    "2013-02-01 05:00",
    "2013-02-01 13:00",
    "2013-02-02 05:00",
    "2013-02-02 13:00",
    "2013-02-03 13:00",
]


def elev_color(elev_m: float) -> tuple:
    lo, hi = ELEV_RANGE
    frac = (float(elev_m) - lo) / (hi - lo)
    return ELEV_CMAP(ELEV_CLAMP * min(max(frac, 0.0), 1.0))


def load(obs_path: Path) -> tuple[pl.DataFrame, dict[str, dict]]:
    meta = pl.read_csv(META_CSV)
    names = {
        r["stid"]: {"name": (r["paper_site"] or r["name"]).split(" (")[0], "elev_m": r["elev_m"]}
        for r in meta.iter_rows(named=True)
    }
    # Short labels so annotations fit print-width panels.
    for stid, short in {"USU08": "USU Trailer", "UUT01": "UB Trailer"}.items():
        if stid in names:
            names[stid]["name"] = short
    obs = (
        pl.read_parquet(obs_path)
        .with_columns(pl.col("valid_time").dt.offset_by(f"{UTC_TO_MST}h").alias("time_mst"))
        .with_columns(pl.col("time_mst").dt.truncate("1h").alias("hour_mst"))
    )
    hourly = (
        obs.group_by("stid", "hour_mst")
        .agg(
            pl.col("temp_2m").mean(),
            pl.col("pressure_surface").mean(),
            # Synoptic elevation is in FEET; convert once here.
            (pl.col("elevation").first() * 0.3048).alias("elev_m"),
        )
        # Guard: all-null groups aggregate to 0.0 (not null) in this polars version,
        # which would make theta inf. Physical-range gate instead of a null test.
        .with_columns(
            pl.when(pl.col("pressure_surface").is_between(5.0e4, 1.1e5))
            .then(pl.col("pressure_surface"))
            .otherwise(None)
            .alias("pressure_surface")
        )
        .with_columns(
            (
                (pl.col("temp_2m") + 273.15)
                * (1000.0 / (pl.col("pressure_surface") / 100.0)) ** KAPPA
            ).alias("theta")
        )
        .sort("stid", "hour_mst")
    )
    return hourly, names


def style_axes(ax) -> None:
    ax.grid(alpha=0.25, linewidth=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def save(fig, stem: str) -> None:
    """600 dpi PNG (MDPI submission minimum); vector PDF for the LaTeX draft."""
    for ext, dpi in (("png", 600), ("pdf", None)):
        fig.savefig(OUT / f"{stem}.{ext}", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {stem}.png + .pdf")


def panel_letter(ax, letter: str, extra: str = "") -> None:
    """Bold lowercase (a) top-left (AMS/ACP convention), optional regular text after."""
    t = ax.text(0.03, 0.97, f"({letter})", transform=ax.transAxes,
                va="top", ha="left", fontsize=9, fontweight="bold", color="0.15")
    if extra:
        ax.annotate(extra, xycoords=t, xy=(1, 0), xytext=(3, 0),
                    textcoords="offset points", va="bottom", fontsize=8, color="0.25")


def shade_nights(ax, t_min, t_max) -> None:
    """Light bands over local night (approx. 18:00-07:30 MST for early Feb, 40 N)."""
    import datetime as dt

    day = dt.datetime(t_min.year, t_min.month, t_min.day) - dt.timedelta(days=1)
    while day < t_max:
        dusk, dawn = day.replace(hour=18), (day + dt.timedelta(days=1)).replace(hour=7, minute=30)
        ax.axvspan(max(dusk, t_min), min(dawn, t_max), color="0.92", zorder=0, lw=0)
        day += dt.timedelta(days=1)


def fig_theta_profiles(hourly: pl.DataFrame, names: dict) -> None:
    fig, axes = plt.subplots(2, 3, figsize=(FULL_W, 4.5), sharex=True, sharey=True,
                             layout="constrained")
    for ax, snap, letter in zip(axes.flat, SNAPSHOTS_MST, "abcdef"):
        t = pl.Series([snap]).str.to_datetime("%Y-%m-%d %H:%M")[0]
        prof = (
            hourly.filter(
                (pl.col("hour_mst") == t)
                & pl.col("theta").is_not_null()
                & pl.col("theta").is_finite()
            )
            .sort("elev_m")
        )
        if prof.height < 3:
            ax.set_visible(False)
            continue
        elev = [names[s]["elev_m"] for s in prof["stid"]]
        ax.plot(prof["theta"], elev, color="0.45", lw=1.2, zorder=1)
        for i, (th, ev, st) in enumerate(zip(prof["theta"], elev, prof["stid"])):
            ax.scatter(th, ev, s=26, color=elev_color(ev), zorder=2, edgecolor="white", lw=0.5)
            if snap == SNAPSHOTS_MST[0]:
                # Stations cluster near 1550-1620 m; alternate label side and add a small
                # offset so names are less likely to collide.
                side = 1 if i % 2 == 0 else -1
                ax.annotate(
                    names[st]["name"], (th, ev),
                    xytext=(6 * side, 3 * side), textcoords="offset points",
                    fontsize=6.5, color="0.25", va="center",
                    ha="left" if side > 0 else "right",
                )
        hh = t.strftime("%H:%M")
        panel_letter(ax, letter,
                     f"{t.strftime('%d %b')} {hh} MST" + (" (night)" if hh == "05:00" else ""))
        style_axes(ax)
    axes[0, 0].set_ylim(1415, 2300)  # headroom so the bench marker clears the panel label
    for ax in axes[:, 0]:
        ax.set_ylabel("Station elevation (m)")
    for ax in axes[1, :]:
        ax.set_xlabel("Potential temperature θ (K)")
    save(fig, "obs_theta_profiles_feb0102")


def fig_temp_timeseries(hourly: pl.DataFrame, names: dict) -> None:
    fig, ax = plt.subplots(figsize=(FULL_W, 2.9), layout="constrained")
    t_min, t_max = hourly["hour_mst"].min(), hourly["hour_mst"].max()
    shade_nights(ax, t_min, t_max)
    for st, ls in zip(TS_STATIONS, TS_STYLES):
        d = hourly.filter((pl.col("stid") == st) & pl.col("temp_2m").is_not_null())
        ev = names[st]["elev_m"]
        ax.plot(
            d["hour_mst"], d["temp_2m"], ls, color=elev_color(ev), lw=1.3,
            label=f"{names[st]['name']} ({ev:.0f} m)",
        )
    ax.axhline(0.0, color="0.7", lw=0.8, zorder=1)
    ax.set_xlim(t_min, t_max)
    ax.set_ylabel("2 m temperature (°C)")
    ax.set_xlabel("Local time (MST); shaded = night")
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(byhour=[12]))
    ax.tick_params(axis="x", which="major", length=7)
    ax.legend(loc="upper left", title="Station (elevation)", title_fontsize=8)
    style_axes(ax)
    save(fig, "obs_temp_timeseries_feb0102")


def fig_inversion_index(hourly: pl.DataFrame, names: dict) -> None:
    top, floor = "USU03", "USU07"
    th = hourly.filter(pl.col("theta").is_not_null() & pl.col("theta").is_finite())
    dth = (
        th.filter(pl.col("stid") == top)
        .join(th.filter(pl.col("stid") == floor), on="hour_mst", suffix="_floor")
        .select("hour_mst", (pl.col("theta") - pl.col("theta_floor")).alias("dtheta"))
        .sort("hour_mst")
    )

    # Valley heat deficit from the station pseudo-profile (trapezoid over elevation).
    rows = []
    for key, grp in th.group_by("hour_mst"):
        t = key[0] if isinstance(key, tuple) else key
        grp = grp.sort("elev_m")
        if grp.height < 5 or top not in grp["stid"].to_list():
            continue
        theta = grp["theta"].to_numpy()
        z = grp["elev_m"].to_numpy()
        p = grp["pressure_surface"].to_numpy()
        tk = grp["temp_2m"].to_numpy() + 273.15
        rho = p / (RD * tk)
        theta_top = theta[grp["stid"].to_list().index(top)]
        deficit = rho * CP * np.maximum(theta_top - theta, 0.0)
        trapz = getattr(np, "trapezoid", np.trapz)
        h = float(trapz(deficit, z)) / 1e6  # MJ m-2
        rows.append({"hour_mst": t, "heat_deficit": h})
    hd = pl.DataFrame(
        rows,
        schema={"hour_mst": pl.Datetime, "heat_deficit": pl.Float64},
    ).sort("hour_mst")
    if hd.is_empty():
        raise ValueError("No heat-deficit profiles computed (need >=5 theta stations incl. USU03).")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(FULL_W, 4.2), sharex=True,
                                   layout="constrained")
    t_min, t_max = hourly["hour_mst"].min(), hourly["hour_mst"].max()
    for ax in (ax1, ax2):
        shade_nights(ax, t_min, t_max)

    ax1.plot(dth["hour_mst"], dth["dtheta"], color="#00224e", lw=1.3)
    ax1.axhline(8.0, color="0.4", lw=1.0, ls="--")
    ax1.annotate("8 K CAP threshold", xy=(0.99, 8.0), xycoords=("axes fraction", "data"),
                 xytext=(0, -10), textcoords="offset points", fontsize=8, color="0.35",
                 ha="right")
    ax1.set_ylabel(
        f"Δθ, {names[top]['name']} ({names[top]['elev_m']:.0f} m)\n"
        f"− {names[floor]['name']} ({names[floor]['elev_m']:.0f} m)  (K)"
    )
    panel_letter(ax1, "a")
    style_axes(ax1)

    ax2.plot(hd["hour_mst"], hd["heat_deficit"], color="#5f636f", lw=1.3)
    ax2.set_ylabel("Valley heat deficit (MJ m⁻²)")
    ax2.set_xlabel("Local time (MST); shaded = night")
    ax2.set_xlim(t_min, t_max)
    ax2.xaxis.set_major_locator(mdates.DayLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    panel_letter(ax2, "b")
    style_axes(ax2)

    save(fig, "obs_inversion_index_feb0102")


def main() -> None:
    ap = argparse.ArgumentParser(description="Observed-case figures, Feb 1-2 2013 CAP.")
    ap.add_argument("--obs", default=str(DEFAULT_OBS), help="local obs parquet")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    hourly, names = load(Path(args.obs).expanduser())
    n_theta = hourly.filter(pl.col("theta").is_not_null())["stid"].n_unique()
    print(f"stations: {hourly['stid'].n_unique()} total, {n_theta} with pressure (theta)")
    fig_theta_profiles(hourly, names)
    fig_temp_timeseries(hourly, names)
    fig_inversion_index(hourly, names)


if __name__ == "__main__":
    main()
