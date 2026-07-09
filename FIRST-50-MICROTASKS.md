# First 50 microtasks — taking ownership of the manuscript

Starting checklist for `jrl/first-draft` (created 2026-07-09). Each item is small and
self-contained. Most map directly to the `[TODO:]` / `[DRAFT:]` markers left in `main.tex`
by the Methods/Results scaffold (commit `32ec147`). Verify every `[DRAFT:]` number against
the CSVs in `verification/data/` before it goes final. This file is a living checklist —
edit, reorder, and tick as you go.

## A. Introduction (drafted — close the gaps)
- [ ] 1. Fill `[STATE THE AIM: ...]` at the end of §Introduction (1–2 sentences on the objective).
- [ ] 2. Fill `[State principal findings.]` with a 2–3 sentence summary of the touchstone results.
- [ ] 3. Confirm the emissions-inventory vs. meteorology framing still matches Seth's argument.
- [ ] 4. Sanity-check each Introduction citation (year/title) against its source document.

## B. Methods (fill the scaffold from the recovered namelist)
- [ ] 5. Set the WRF version (`[TODO: model version]`) from `verification/provenance/namelist_candidates.txt`.
- [ ] 6. Confirm the 3 / 1 / 0.333 km nesting ratios and one-/two-way settings; replace the `[TODO]`.
- [ ] 7. Confirm 75 vertical levels, model top, and level distribution.
- [ ] 8. Fill the physics suite (PBL, land-surface, microphysics, radiation, surface layer) from the namelist.
- [ ] 9. State GFS forcing resolution/cycle; keep the `\citep{ncep2019gfs}`.
- [ ] 10. Add a bibliography entry for the **NAM** model and cite it in §Initial and boundary conditions.
- [ ] 11. State forecast length + valid window (2013-02-02 12–18 UTC) and the ~2 h spin-up handling.
- [ ] 12. Identify the specific Tran (2018) reference run (`REF_long`) and its config in §Numerical experiments.
- [ ] 13. State N stations; describe the selection + QC gate (`verification/data/stations_2013_selection.csv`).
- [ ] 14. State that d02 (1 km) is the comparison domain and why (0.333 km nest excludes most bench stations).
- [ ] 15. Edit the generative-AI disclosure sentence to match actual usage across coauthors.

## C. Results (verify the [DRAFT] numbers, then write prose)
- [ ] 16. Verify NAM/GFS surface-T bias + MAE against `wrf_runs_scores_feb0102_postspinup.csv`; unbracket.
- [ ] 17. Confirm the "one- and two-way NAM near-identical" claim from the per-run score tables.
- [ ] 18. Verify the 8 K CAP threshold and the GFS 6–8 K underprediction (inversion index + spread tables).
- [ ] 19. Verify the 500 hPa convergence and 700 hPa +1.5–2 K warm-layer values from the upper-air figures.
- [ ] 20. Verify the Tran REF −4.4 °C cold bias against `wrf_trang_ref_per_station.csv` / `*_withtrang` tables.
- [ ] 21. Write the observed cold-air-pool description (surface cooling, θ profiles, inversion index).
- [ ] 22. Add the fair-comparison caveat (6 h window vs. multi-week continuous runs) to the nudged-reference subsection.
- [ ] 23. Decide whether d03 (0.333 km) interior-only resolution sensitivity gets its own subsection or an aside.
- [ ] 24. Add a per-run scores table (bias/MAE/RMSE/corr) built from the `verification/data` CSVs.
- [ ] 25. Add the mechanism note (inherited profile vs. CAP-top entrainment), or mark it explicitly as future work.

## D. Figures (wire into `figures/`, keep provenance)
- [ ] 26. Copy the observed-case panels (`obs_temp_timeseries` / `obs_theta_profiles` / `obs_inversion_index`) into `figures/`.
- [ ] 27. Copy the WRF-vs-obs overlays (`wrf_temp_timeseries_feb0102`, `wrf_inversion_index_feb0102`) into `figures/`.
- [ ] 28. Copy the chosen cross-section panels (`wrf_xsect_theta_*_d02_16z`) into `figures/`.
- [ ] 29. Copy the upper-air panels (`wrf_upper_500hPa_*`, `wrf_upper_700hPa_*`, diff panels) into `figures/`.
- [ ] 30. Copy the Tran REF cross-section (`wrf_xsect_theta_trang_ref`) into `figures/`.
- [ ] 31. Uncomment and complete the `\includegraphics` blocks in Results for each wired-in figure.
- [ ] 32. Write a real caption + `\label` for each figure and cross-reference it (`Figure~\ref{...}`) in prose.
- [ ] 33. Log every figure's provenance (generating script + data) in `figures/SOURCES.md`.

## E. Discussion & Conclusions (start from empty)
- [ ] 34. Draft a Discussion opening tying the IC-driven inter-run spread to cold-pool forecast difficulty.
- [ ] 35. Draft the implication for photochemical modeling (meteorological fidelity as the limiting constraint).
- [ ] 36. Draft Conclusions: 3–4 sentence summary of the touchstone finding.
- [ ] 37. State limitations (single 6 h case, d02 vs. d03, un-nudged reference only) in Discussion.

## F. Front matter (replace the placeholders)
- [ ] 38. Replace `\abstract{ABSTRACT}` with a ~200-word structured abstract.
- [ ] 39. Review `\keyword{...}`; add e.g. "surface ozone" / "FDDA" if wanted.
- [ ] 40. Fill `\funding{...}` with the real funder + grant number.
- [ ] 41. Fill `\dataavailability{...}` (obs = Synoptic; WRF config in `verification/`; figures tracked in repo).
- [ ] 42. Fix `\authorcontributions{...}` to CRediT roles and resolve the `L?D` typo (→ LD).
- [ ] 43. Replace `\acknowledgments{shout out to all my homies}` with real acknowledgments.
- [ ] 44. Confirm author order, ORCIDs, and affiliations in the front matter.

## G. Bibliography (verify before submission)
- [ ] 45. Verify the five USU/DAQ tech-report citations (titles, years, sections, authorship) against the documents.
- [ ] 46. Decide inline `thebibliography` vs. external `references.bib` for this submission (inline for now, per CLAUDE.md).
- [ ] 47. Confirm the NAM reference (task 10) and any other newly cited works have bib entries.
- [ ] 48. Check for unused bib keys (e.g. `mansfield2021ozone`) — cite or remove.

## H. Repo / build
- [ ] 49. Full Overleaf build (has `gs`) to confirm logos + two-pass citations resolve; copy a milestone to `drafts/`.
- [ ] 50. When ready: PR `jrl/first-draft → main`; later decide on the `verification/ → analysis/` rename and pruning `jrl/first-edits`.
