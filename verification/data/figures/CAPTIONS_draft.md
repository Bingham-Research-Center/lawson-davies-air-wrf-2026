# Draft figure paragraphs — for John to tweak

One paper-ready paragraph per figure in `data/figures/`. Written from the generating
scripts, `docs/chpc-feb-touchstones.md`, and the figures themselves; numbers quoted
are readable off the figures or from `baseline_scores_jan1521.csv`. Citation
placeholders (Neemann et al. 2015, Whiteman and Hoch 2014, Tran 2018, PCAPS) need
the real bibliography entries. Michael: rewrite in your own voice; the facts are
checked.

## Shared provenance (Methods-style, reuse across captions)

**Observations.** All surface observations are retrieved from the Synoptic Data API
archive and averaged to hourly means. Station selection is recorded in
`data/stations_2013_selection.csv`: the seven Utah State University Uintah Basin
winter-ozone study sites used by Tran (2018) (USU01 Seven Sisters, USU02 Gusher,
USU03 Mountain Home, USU04 Seep Ridge, USU05 Wells Draw, USU06 Sand Wash, USU07
Pariette Draw), the two research trailers (USU08, UUT01), Vernal Airport (KVEL),
and the UDOT stations Roosevelt (QRS) and Vernal (QV4). Elevations span the basin
floor at Pariette Draw (1465 m) to the bench at Mountain Home (2228 m).

**Baseline run (Jan 15–21 2013 figures).** The analysis-nudged (FDDA) configuration
of Tran's 2013 WRF suite (`WRF_anlnudge`), one-way 12 / 4 / 1.33 km nests, 37
levels, MYJ PBL, evaluated on the innermost 1.33 km domain at hourly output.
WRF is matched to stations by nearest grid cell; 10 m winds are rotated from grid-
to earth-relative. Evaluated against six stations reporting through the window
(KVEL, QRS, QV4, USU01, USU05, USU08), roughly 132 hourly pairs per station.

**Touchstone runs (Feb 2 2013 figures).** Three short WRF forecasts (J. Lawson),
each initialized 2013-02-02 12:00 UTC and run 6 h with hourly output, on 3 / 1 /
0.333 km nests with 75 vertical levels: GFS-driven with two-way nesting
(`gfs_2way`), NAM-driven with two-way nesting (`nam_2way`), and NAM-driven with
one-way nesting (`nam_1way`, the Neemann/Tran-like configuration). The first ~2 h
are initialization spin-up; post-spin-up comparison starts 14:00 UTC. All
comparisons use the 1 km d02 domain because the 333 m d03 does not contain the
bench stations. WRF is matched to stations with an elevation-aware nearest-cell
scheme (closest cell within a 7x7 neighborhood whose model terrain is within
200 m of station elevation).

**Tran contrast runs.** `trang_ref` is the reference run (`REF_long`) of Tran's
archived suite: a continuous multi-week episode simulation (Jan 29 – Feb 12
2013), obs-nudged (surface-obs FDDA for wind/T/moisture; WRF v4.2 — provenance
notes in `docs/chpc-feb-touchstones.md`), whose 1.33 km domain covers the Feb 2
case, giving a same-case,
same-snapshot comparison against the touchstones. `trang_anlnudge_jan17` figures
show the analysis-nudged run during the Jan 15–21 baseline window (17 Jan).

---

## Jan 15–21 2013 baseline evaluation (Tran anlnudge d03 vs 6 stations)

### baseline_temp_timeseries_jan1521.png
> Observed and simulated 2 m temperature at the six evaluation stations for the
> 15–21 January 2013 cold-air-pool episode. Observations (black) are hourly means
> of Synoptic Data API records; WRF (red) is the analysis-nudged Tran configuration
> sampled at the nearest 1.33 km grid cell, hourly. The model reproduces the
> diurnal cycle and the slow synoptic warming through the week but sits 4–6 °C
> warm at essentially every station and hour: observed nighttime minima reach −25
> to −27 °C while WRF bottoms out near −15 to −18 °C. The bias never changes sign.
> Vernal (QV4) is the closest station, with simulated and observed daytime maxima
> nearly coincident late in the window.

### baseline_temp_scatter_jan1521.png
> Simulated versus observed 2 m temperature for all six stations pooled over
> 15–21 January 2013, against the 1:1 line; each WRF valid time is paired with the
> nearest observation within 30 min. The overall bias is +5.5 °C and nearly the
> entire point cloud lies above the 1:1 line. The gap is widest through the
> inversion range (observed −25 to −15 °C) and narrows at the cold extreme, where
> the coldest observed hours approach the line: the model can briefly touch the
> right minimum but cannot hold cold through the episode, consistent with
> over-mixing of the pool rather than a uniform offset. QV4 hugs the line at the
> warm end, with a few points below it.

### baseline_temp_diurnal_bias_jan1521.png
> Mean 2 m temperature bias (WRF minus obs) by hour of day (UTC; MST = UTC−7) for
> each station and for the all-station mean over 15–21 January 2013. The
> all-station bias is remarkably flat, between +4.6 and +6.1 °C at every hour of
> the day: the warm bias is not preferentially nocturnal but persists through the
> full diurnal cycle, indicating a standing inability to maintain the cold pool
> rather than a nighttime decoupling failure alone. QV4 is the outlier, dropping
> to about +2 °C in local afternoon; USU08 swings most (+3 to +8 °C).

### baseline_inversion_night_zoom_jan1521.png
> Two-meter temperature at the six stations in a ±18 h window around the coldest
> observation of the evaluation period (15 January 2013 13 UTC, about −27 °C at
> Vernal Airport). WRF's first output hours start near the observations, but after
> one daytime mixing cycle the model overshoots the afternoon warm-up by 4–6 °C
> and never re-cools: overnight 15–16 January the observations return to −20 to
> −23 °C while WRF flattens near −16 to −18 °C. The panel localizes the mechanism
> of the warm bias: the simulated pool is destroyed by daytime mixing and does not
> rebuild.

### baseline_windspeed_timeseries_jan1521.png
> Observed and simulated 10 m wind speed at the six stations, 15–21 January 2013;
> observations are hourly means to match WRF's hourly output while preserving
> genuine calms. Observed speeds are mostly below 2 m s−1, as expected inside a
> persistent cold pool, while WRF is over-ventilated at five of six stations;
> Wells Draw (USU05) is worst at +2.4 m s−1 mean bias with simulated speeds
> oscillating between 2 and 6 m s−1. Roosevelt (QRS) is the one negative-bias
> station, driven by episodic observed spikes the model misses. Correlations are
> near zero throughout: the model has no timing skill for calms or gusts during
> the episode.

### baseline_pressure_timeseries_jan1521.png
> Observed and simulated surface pressure at the stations reporting pressure
> (KVEL, USU01, USU05, USU08), 15–21 January 2013. WRF tracks the observed
> synoptic evolution nearly perfectly, including the mid-window maximum around
> 17–18 January, with biases of −1.2 to +0.4 hPa and correlations above 0.93; the
> model slightly under-amplifies the pressure maxima. Together with the
> temperature panels this separates the error budget: the synoptic mass field is
> essentially correct, and the warm bias must originate in boundary-layer and
> land-surface processes rather than in the large-scale forcing.

### baseline_skill_bars_jan1521.png
> Per-station bias and RMSE for 2 m temperature, 10 m wind speed, and surface
> pressure over 15–21 January 2013. Temperature bias is +4.3 to +6.1 °C at all six
> stations (worst at Vernal Airport, best at Vernal QV4) and RMSE is nearly equal
> to bias everywhere, so the temperature error is almost purely systematic. Wind
> speed bias is +0.5 to +2.4 m s−1 except Roosevelt (−0.8 m s−1); pressure errors
> are below 1.4 hPa at every station. Wind direction is excluded pending a
> circular-statistics treatment, since directions are undefined during the
> predominant calms.

---

## Feb 1–2 2013 observed case (obs only; Synoptic Data API)

### obs_temp_timeseries_feb0102.png
> Observed 2 m temperature during the 31 January – 3 February 2013 cold-air-pool
> episode at four surface stations spanning the depth of the basin atmosphere,
> from the basin floor at Pariette Draw (1465 m) through Wells Draw (1759 m) and
> Seep Ridge (1933 m) to the bench site at Mountain Home (2228 m). Observations
> are hourly means of Synoptic Data API records from the USU Uintah Basin network;
> shading denotes local night. The elevation ordering is persistently inverted:
> Mountain Home, 763 m above the basin floor, is routinely the warmest station
> while Pariette Draw remains the coldest, reaching −17 °C at night, and the
> nocturnal top-to-floor contrast widens from roughly 5 °C on 31 January to 13–15
> °C by 2–3 February. The basin floor retains a 10 °C diurnal cycle throughout,
> indicating shallow daytime mixing beneath a cap that never breaks. No model
> output is shown; these observations are the baseline against which the WRF
> experiments are evaluated.

### obs_theta_profiles_feb0102.png
> Pseudo-vertical profiles of potential temperature θ, constructed by plotting
> hourly-mean station θ against station elevation following Whiteman and Hoch
> (2014), at six snapshot times spanning the episode: 13:00 MST on each of 31
> January and 1–3 February, plus 05:00 MST on 1 and 2 February. θ is computed from
> 2 m temperature and station pressure for the nine stations reporting pressure,
> spanning the basin floor (Pariette Draw, 1465 m) to the bench (Mountain Home,
> 2228 m); the cluster of stations between 1550 and 1620 m samples horizontal
> variability across the basin floor rather than vertical structure. All data are
> surface observations from the Synoptic Data API archive; no radiosonde or model
> data enter these profiles. θ increases monotonically from floor to bench in
> every panel, including midday, showing that the pool never mixes out during the
> episode. The cold anomaly at Seep Ridge (1933 m), which amplifies late in the
> episode, reflects that station sitting within its own drainage airmass on the
> southern rim and illustrates the limit of interpreting a station network as a
> single vertical profile; midday panels are the most representative of free-air
> structure, as surface stations run colder than the free atmosphere at night.

### obs_inversion_index_feb0102.png
> Bulk cold-air-pool metrics computed from the hourly station observations
> (Synoptic Data API archive): (a) the potential-temperature difference Δθ between
> the bench site (Mountain Home, 2228 m) and the basin floor (Pariette Draw,
> 1465 m), with the 8 °C persistent cold-air-pool threshold of the PCAPS literature
> marked, and (b) the valley heat deficit H = ∫ρ c_p (θ_top − θ) dz integrated
> over the station pseudo-profile for hours with at least five reporting stations,
> following Whiteman and Hoch (2014). Δθ drops to the 8 °C threshold only once,
> near midday on 31 January, and otherwise remains between 11 and 22 °C, so the
> pool is continuous throughout the episode by this criterion. Both metrics
> breathe diurnally as daytime surface heating erodes the base of the pool, but
> the nocturnal heat-deficit maxima grow from roughly 9 to 12 MJ m−2 over the
> episode: the pool gains cold-air mass even as the endpoint Δθ plateaus. These
> two series are the observational targets against which the WRF sensitivity runs
> are scored. No model data are shown.

---

## Feb 2 2013 WRF vs obs (three touchstone runs, d02)

### wrf_temp_timeseries_feb0102.png
*(Working/supplementary — not the paper set: its context role is covered by
`obs_temp_timeseries_feb0102`, and the zoom is the comparison figure.)*
> Observed and simulated 2 m temperature at the four floor-to-bench stations
> (Pariette Draw 1465 m, Wells Draw 1759 m, Seep Ridge 1933 m, Mountain Home
> 2228 m) across the full 31 January – 3 February 2013 episode. Observations
> (black) are Synoptic hourly means; the colored traces are the three 6-h
> touchstone forecasts initialized 2013-02-02 12:00 UTC (GFS-driven two-way,
> NAM-driven one-way, NAM-driven two-way; 1 km d02), with the gray band the
> min-max envelope across the three runs. The spread is largest at the basin
> floor, where the error changes sign between drivers within a single episode:
> the NAM runs overshoot the pre-dawn minimum by 4–5 °C cold while GFS runs 4–7 °C
> warm by late morning. The two NAM runs are nearly indistinguishable, so the
> driving analysis, not the nesting mode, controls the spread. Shown at full
> episode scale for context; the zoomed companion figure is the readable version.

### wrf_temp_timeseries_feb0102_zoom.png
> As the previous figure, zoomed to the forecast window (2 February 04:00–12:00
> MST, hourly ticks); the dotted line at 07:00 MST (14:00 UTC) marks the end of
> the ~2 h initialization spin-up, so forecast values left of it should be read
> cautiously. At the basin floor (Pariette Draw) the three runs already
> differ by 4.6 °C at forecast hour zero, so the inter-run spread is seeded by the
> initial conditions rather than developed during the forecast: GFS starts at
> −7.2 °C and the NAM pair at −11.8 °C against an observed −14.3 °C. The NAM runs
> bottom at −18.7 °C (about 4.5 °C too cold) while GFS recovers to 4–7 °C above
> the observations by late morning. At Seep Ridge all three runs warm far too
> quickly (up to +9 °C by 10:00 MST) while the observed bench-edge station stays
> near −11 °C; at Wells Draw all runs track within about 2 °C until the observed
> late-morning warm-up pulls away. The NAM one-way and two-way traces overlap
> almost perfectly at every station.

### wrf_inversion_index_feb0102.png
*(Working/supplementary — not the paper set: its context role is covered by
`obs_inversion_index_feb0102`, and the zoom is the comparison figure.)*
> Cold-air-pool metrics for the touchstone forecasts against observations across
> the full episode: (a) Δθ between Mountain Home and Pariette Draw with the 8 °C
> CAP threshold marked, and (b) the valley heat deficit, both computed identically
> for obs and model (elevation-aware nearest-cell matching on the 1 km d02).
> During the 2 February forecast window both NAM runs ride the observed Δθ within
> 1–2 °C, while the GFS-driven run collapses to 4.4 °C, below the 8 °C threshold:
> the GFS forecast mixes the observed pool out. The heat deficit gives the same
> verdict independently, with the NAM runs reaching roughly half the observed
> deficit and GFS roughly a third. The two metrics agree on the ranking, and the
> two NAM runs are again nearly identical.

### wrf_inversion_index_feb0102_zoom.png
> As the previous figure, zoomed to the forecast window (2 February 04:00–12:00
> MST); the dotted line at 07:00 MST (14:00 UTC) marks the end of the ~2 h
> initialization spin-up. The GFS-driven run starts at Δθ = 6.3 °C, dips to 4.4 °C
> at 06:00 MST (3.6 °C below the CAP threshold), and never gets within 7 °C of the
> observed peak of 20.2 °C, while the two NAM runs rise to 17–18 °C, briefly
> overshooting the observed Δθ pre-dawn (the same floor cold bias seen in the
> temperature figure, inflating Δθ early — an overshoot that falls entirely
> within the spin-up window) before crossing under the observed morning surge.
> Heat deficit (b): observations climb from 4.6 to 11.3 MJ m−2 over the window
> while the NAM runs peak near 6.5 and GFS near 4.9.

---

## Feb 2 2013 wrfout upper-air maps (d02, 14:00 + 16:00 UTC = 07:00 + 09:00 MST)

All maps: θ interpolated linearly in pressure to the stated level from wrfout
fields, shaded (pcolormesh), wind vectors every 12 km, dashed terrain contours at
1700/2000/2300 m, full 1 km d02 extent, station markers at Pariette Draw (USU07),
Mountain Home (USU03), and Roosevelt (QRS). θ maps share a fixed color scale per
level (294–303 K at 700 hPa, 307–312 K at 500 hPa) and difference maps a fixed
symmetric scale (±5 °C at 700, ±2.5 °C at 500), so colors compare directly across
runs. White regions at 700 hPa are terrain above the pressure surface (high
Uintas). Panels at 14:00 UTC are forecast hour 2, the edge of spin-up; 16:00 UTC
(hour 4) is the trusted snapshot.

### wrf_upper_700hPa_gfs_2way_d02.png
> θ and winds at 700 hPa from the GFS-driven two-way touchstone at 14:00 and
> 16:00 UTC 2 February. The basin interior sits at 299–300.5 K with weak, variable
> flow, warming and smoothing between the two times; the coolest air (296–298 K)
> occupies the northeast third. 700 hPa is the layer immediately above the
> cold-air pool, and this run is the warm end member there.

### wrf_upper_700hPa_nam_2way_d02.png
> As above for the NAM-driven two-way run. The basin interior is 297–298.5 K at
> 14:00 UTC, visibly 1.5–2 °C colder than the GFS run at the same instant, with a
> deeper cold lobe in the northeast and short-wavelength mountain-wave banding
> along the Uinta south slope that fades by 16:00 UTC. On the shared 700 hPa
> color scale the contrast against the GFS figure reads directly; the difference
> map quantifies it.

### wrf_upper_700hPa_nam_1way_d02.png
> As above for the NAM-driven one-way run. The field is visually near-identical
> to the two-way NAM run at both times, at both the basin scale and in the wave
> banding: on the 1 km domain at these lead times, the two-way feedback from the
> 333 m nest has essentially no imprint at 700 hPa, and the driving analysis is
> the only first-order axis of spread.

### wrf_upper_700hPa_gfs_minus_nam2way_d02.png
> Difference map, GFS-driven minus NAM-driven (two-way) θ at 700 hPa. At 14:00 UTC
> nearly the whole domain is +1 to +3 °C (GFS warmer), with local maxima of +4 to
> +5 °C along the Uinta flank where the NAM wave banding is in a different phase;
> by 16:00 UTC the coherent basin-wide difference remains at +1 to +2 °C. The GFS
> forecast carries a persistent warm anomaly through the layer that caps the
> cold pool, exactly where a warm bias is most damaging to simulated pool
> strength.

### wrf_upper_500hPa_gfs_2way_d02.png
> θ and winds at 500 hPa from the GFS-driven two-way run, 14:00 and 16:00 UTC 2
> February. The field is synoptically smooth: a southwest-to-northeast gradient
> from about 311 K to 308 K under uniform north-northwesterly flow, with minor
> raggedness near the Uintas at 14:00 UTC that smooths by 16:00 UTC.

### wrf_upper_500hPa_nam_2way_d02.png
> As above for the NAM-driven two-way run: the same smooth gradient and
> north-northwesterly flow, visually near-identical to the GFS run at 500 hPa at
> both times.

### wrf_upper_500hPa_nam_1way_d02.png
> As above for the NAM-driven one-way run; indistinguishable from the two-way NAM
> run at this level. Nesting mode is irrelevant to the mid-troposphere on this
> domain and lead time.

### wrf_upper_500hPa_gfs_minus_nam2way_d02.png
> Difference map, GFS minus NAM (two-way) θ at 500 hPa. At 14:00 UTC the GFS run
> is 0.3–1 °C cooler over most of the domain with a −2 °C streak along the Uinta
> crest, a residual initialization feature that vanishes by 16:00 UTC; at 16:00
> UTC the difference is within about ±0.5–1 °C everywhere. Paired with the 700 hPa
> difference map, this localizes the inter-analysis disagreement vertically: the
> mid-troposphere has converged by hour 4 while the lower troposphere, the layer
> governing the cold pool, has not.

---

## Feb 2 2013 wrfout θ advection maps (d02, 14:00 + 16:00 UTC)

Horizontal θ advection, −(u ∂θ/∂x + v ∂θ/∂y), on the stated pressure surface, in
°C h−1 (diverging scale, red = warm advection), winds overlaid; these figures ask
whether the GFS 700 hPa warm layer is advected in horizontally or inherited /
mixed up vertically. All advection maps share a fixed ±10 °C h−1 scale; the
orographic wave couplets over the Uintas exceed it and saturate by design, so
the weak basin-interior signal stays readable.

### wrf_adv_700hPa_gfs_2way_d02.png
> Horizontal θ advection at 700 hPa from the GFS-driven two-way run at 14:00 and
> 16:00 UTC. Over the basin interior the advection is effectively zero (within a
> few °C h−1); the only strong signal is a train of alternating positive-negative
> couplets along the Uinta south slope, a mountain-wave signature that cancels in
> any area mean and does not represent net heat transport. Resolved horizontal
> advection is not supplying the 700 hPa warm anomaly in this run during the
> forecast window.

### wrf_adv_700hPa_nam_2way_d02.png
> As above for the NAM-driven two-way run. The basin interior is again quiet; the
> orographic wave train is stronger than in the GFS run, saturating the ±10 °C h−1
> scale over a wider area (unsaturated values reached ±75–90 °C h−1 at 14:00 UTC
> in the diagnostic autoscaled set), and fades and shifts east by 16:00 UTC. No
> coherent single-signed advection appears anywhere over the basin.

### wrf_adv_700hPa_nam_1way_d02.png
> As above for the NAM-driven one-way run, and near-identical to the two-way NAM
> figure in wave placement, amplitude, and evolution. Together the three 700 hPa
> panels rule out resolved horizontal warm-air advection as the source of the
> GFS-NAM 700 hPa difference: whatever separates the runs in the cap layer is
> inherited from the driving analyses or generated by vertical mixing, not blown
> in sideways during the forecast.

### wrf_adv_500hPa_gfs_2way_d02.png
> Horizontal θ advection at 500 hPa from the GFS-driven two-way run. Under the
> uniform north-northwesterly flow the field is mottled small-scale noise of
> mixed sign (a few °C h−1, locally saturating the ±10 °C h−1 scale near the
> Uintas at 14:00 UTC, subdued by 16:00 UTC) with no coherent advection over the
> basin, consistent with the
> already-converged 500 hPa θ field.

### wrf_adv_500hPa_nam_2way_d02.png
> As above for the NAM-driven two-way run: weak mixed-sign texture over the basin
> (about ±3 °C h−1), modest wave noise near the Uintas and the domain edges. The
> weakest advection amplitudes of the set.

### wrf_adv_500hPa_nam_1way_d02.png
> As above for the NAM-driven one-way run; a near-duplicate of the two-way NAM
> figure, confirming once more that the nesting mode does not alter the free
> troposphere on this domain and lead time.

---

## Feb 2 / Jan 17 2013 wrfout θ cross-sections and time-heights

Cross-sections: θ shaded on a vertical slice along the 65 km floor-to-bench
transect from Pariette Draw (USU07, 1465 m) to Mountain Home (USU03, 2228 m),
80 columns, terrain filled dark, display top 4500 m ASL. Time-heights: θ at the
grid column matched to Roosevelt (QRS, 1588 m). Touchstone panels are valid
16:00 UTC (09:00 MST) 2 February. All February panels (three touchstones plus
Tran REF) share a fixed 266–306 K color scale, so pool depth and sharpness
compare directly across runs; the Jan 17 anlnudge panels autoscale (different
case, different θ range).

### wrf_xsect_theta_gfs_2way_d02.png
> θ cross-section from the GFS-driven two-way touchstone (1 km d02), 16:00 UTC 2
> February, along the Pariette Draw to Mountain Home transect (a Neemann et al.
> 2015 Fig. 4 analog). The simulated pool is shallow and soft: the coldest air
> (273–275 K) is confined to a thin skin below about 1700 m over the basin
> center, the transition to the free atmosphere is spread over roughly 600 m, and
> warm air reaches the bench slope directly. This is the visibly mixed-out end
> member, consistent with this run breaking the 8 °C CAP criterion at the surface.

### wrf_xsect_theta_nam_2way_d02.png
> As above for the NAM-driven two-way run at the same instant. The floor layer is
> about 4 °C colder than the GFS run (269–273 K), continuous along the basin floor
> to about 1750–1800 m, with a distinctly sharper cap. Same transect, same valid
> time, same domain: the driving analysis alone separates a held pool from a
> mixed-out one.

### wrf_xsect_theta_nam_1way_d02.png
> As above for the NAM-driven one-way run: a near-twin of the two-way NAM
> section, with a marginally thicker cold floor layer. The one-way versus two-way
> choice, the configuration axis distinguishing the Neemann/Tran-style setup, is
> second-order against the GFS-NAM contrast at this snapshot.

### wrf_xsect_theta_trang_ref.png
> θ cross-section from Tran's obs-nudged reference run (REF_long: continuous
> multi-week simulation, one-way 12/4/1.33 km nests) at the same
> instant, 16:00 UTC 2 February, on the same transect. This is the deepest and
> coldest pool of the set: air below 277 K fills the basin to 2100–2300 m, a
> 266–270 K core occupies the lowest 400–500 m, and the inversion top is a sharp
> jump to above 295 K near 2400–2500 m, with cold air running up the bench
> slope. Scored against the same stations this run is 4.7 °C cold at 2 m: the
> obs-nudged continuous run overshoots the pool in the opposite direction from the
> GFS touchstone, bracketing the observations between configurations on the same
> case.

### wrf_xsect_theta_trang_anlnudge_jan17.png
> θ cross-section from Tran's analysis-nudged run during the January baseline
> window, valid 11:00 UTC (04:00 MST, pre-dawn) 17 January 2013, same transect.
> The structure is a smooth, quasi-horizontal stratification with only a thin
> (single-layer) cold skin at the surface and no sharp pool top: the nudged run
> at this hour carries a shallow nocturnal surface inversion rather than a deep
> cold pool, the vertical-structure counterpart of the +5.5 °C surface warm bias
> scored over this window.

### wrf_timeheight_theta_gfs_2way_d02.png
> θ time-height at Roosevelt from the GFS-driven two-way touchstone across its
> full 12:00–18:00 UTC (05:00–11:00 MST) forecast window (a Neemann et al. 2015
> Fig. 9 analog). The near-surface cold layer (below 276 K) stays only 100–200 m
> thick, and structure aloft during the first two hours (a warm blob near 3000 m,
> patchiness in the 2000–2400 m layer) is initialization spin-up rather than
> physical evolution. The pool neither deepens nor sharpens through the morning.

### wrf_timeheight_theta_nam_2way_d02.png
> As above for the NAM-driven two-way run: a steady 200–300 m thick surface cold
> layer (down to about 271 K) persists through the entire window with a smooth,
> quasi-stationary stratification above and no spin-up artifacts aloft. The
> simulated pool survives the morning heating hours intact, in contrast to the
> GFS-driven run at the same station and times.

### wrf_timeheight_theta_nam_1way_d02.png
> As above for the NAM-driven one-way run; virtually identical to the two-way NAM
> time-height, with a marginally colder surface layer late in the window. The
> NAM pair differ from each other far less than either differs from the GFS run.

### wrf_timeheight_theta_trang_ref.png
> θ time-height at Roosevelt from Tran's obs-nudged reference run across the full
> day of 2 February 2013 (00:00–23:00 UTC), possible because this is a continuous
> episode simulation rather than a 6 h forecast. The cold pool is deep all day
> (air below 277 K up to 2000–2200 m), with the coldest surface pocket (265–267
> K) developing at 11:00–15:00 UTC, exactly the touchstone forecast window, and
> the capping inversion sagging near midday before lifting after 18:00 UTC. The
> figure shows genuine diurnal pool evolution and places the touchstone window in
> its context within the day.

### wrf_timeheight_theta_trang_anlnudge_jan17.png
> θ time-height at Roosevelt from Tran's analysis-nudged run over 00:00–11:00 UTC
> 17 January 2013 (evening through pre-dawn MST) during the January baseline
> window. The stratification is smooth and nearly stationary for eleven hours,
> with only a thin surface skin below 270 K strengthening after 06:00 UTC as the
> night progresses; no deep pool structure develops. The almost analysis-like
> smoothness of the nudged fields is visible directly, complementing the January
> surface scores.

---

## Flags before any of these go in the paper (status as of 2026-07-09, post-regen)

The full wrfout figure set in this directory is the shared-scale journal-style
regen of 2026-07-09 (viridis θ, fixed `--vrange` per figure family, ±10 °C h−1
advection cap, station markers, MST beside UTC, 300 dpi PNG + vector PDF pairs).
Exact commands: `scripts/regen_wrfout_figures.sh` and the "Figure regen recipe —
2026-07-09" section of `docs/chpc-feb-touchstones.md`.

**Still open:**

- 14:00 UTC panels are forecast hour 2, the edge of the documented spin-up; the
  500 hPa NW streak and some 700 hPa banding at 14 UTC are initialization
  features. 16:00 UTC is the panel to lean on. (Caveat, not a bug.)
- Tran suite provenance needs John's confirmation: `REF_long` wrfout headers show
  WRF V4.2 with surface-obs nudging on (a later SIP-era suite, not the thesis-era
  v3.x study), no un-nudged run in that archive covers the Feb 2 forecast window,
  and the nudged coefficient variants all end 09 UTC Feb 2 (details:
  `docs/chpc-feb-touchstones.md`, 2026-07-09 session notes).
- Baseline run identity (`WRF_anlnudge` as "the" baseline) needs the same
  header check (ncdump: version + nudging flags) and confirmation with
  John/Trang; d03 = 1.33 km for that run is inferred from the suite config, not
  stated in the baseline scripts.
- Baseline reduction is plain nearest-cell vs the Feb touchstones'
  elevation-aware representative-cell; either document both in Methods or rerun
  the baseline reduction with the newer matcher (CHPC).
