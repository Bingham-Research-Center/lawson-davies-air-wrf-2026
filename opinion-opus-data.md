# Which dataset is the "baseline"? — a data-fidelity opinion

*Working memo for JRL, 2026-07-10. Opinion/analysis only — `main.tex` untouched; changes are proposals for JRL + MJD to accept or reject. Companion to [`verification/provenance/WRF-RUN-TO-REPORT-MAP.md`](verification/provenance/WRF-RUN-TO-REPORT-MAP.md); Tran (2018) numbers are from JRL's own extraction under `~/reviews/tran-2018-fdda/` (`_paper.md`, `critique.md`, `wrf-data-paper-contradictions.md`).*

The question: **which prior WRF run do we contrast our own meteorology runs against, and how do we describe it, to show that WRF-configuration surprises in capturing this cold-air pool are as large as the "bias corrections" nudging was introduced to provide?**

---

## Bottom line

**Use the un-nudged reference staged as `trang_ref` (`verification/data/wrf_trang_ref_per_station.csv`) as the same-case baseline.** It is the one prior run that (a) covers *our* case (2 Feb 2013), (b) we actually hold, and (c) we can document honestly. Describe it as **an un-nudged reference from the Uinta Basin SIP-era modelling, configured after Tran et al. (2018)** — *not* as "the Tran (2018) run."

**Demote the January `anlnudge` run.** It is a *different sub-period* (15–21 Jan), it is the paper's **OAN** family (grid **and** obs nudging on — its *worst* configuration for inversion structure), and it may even be a *post-paper* "revised_nudge" variant. It is not the same-case contrast, whatever it has been called.

**For the "nudging bias-correction" yardstick, cite Tran (2018) Table 1 numbers directly** (below) — do **not** derive it from our staged Jan-nudged-minus-Feb-unnudged difference, which conflates *period* with *nudging*.

---

## The three things that have all been called "the baseline"

| Candidate | Period | Nudged? | 2 m-T bias | Same case? | Provenance you can defend |
|---|---|---|---|---|---|
| **`trang_ref`** (staged CSV) | **2 Feb 2013** ✓ | **No** (empty `&fdda`) | **−4.7 °C** (cold) | **Yes** | MED–HIGH: an un-nudged **SIP re-run** (WRF v3.9), config *descended from* Tran 2018 — **not** the 2018 file |
| **`anlnudge` Jan baseline** | **15–21 Jan 2013** ✗ | **Yes (OAN)** | **+4 to +6 °C** (warm) | **No — wrong sub-period** | MED, and it's the paper's *worst-for-structure* config; namelist vintage unresolved |
| **The literal Tran (2018) run(s)** | Jan 16–Feb 4 2013 | 4 configs (NON/ONU/ANU/OAN) | see Table 1 below | Yes | We **do not hold** these v3.6 files — only a later re-run of the same case |

The key realisation: **there is no nudged WRF run covering 1–2 Feb in our staged data.** The only nudged runs are January (`anlnudge`) or start *after* the case (`revised_nudge`, Feb 4). A clean "nudged-vs-un-nudged on *this* case" comparison **cannot be built from what we have** — the manuscript currently fakes it by gluing the Feb un-nudged run to the Jan nudged run.

---

## What our data actually says (same case, same 11 stations, 2 Feb, post-spin-up)

Mean 2 m-T bias (from `wrf_runs_scores_feb0102_postspinup_withtrang.csv`):

- **Un-nudged reference `trang_ref`: −4.7 °C** (station range −1.5 to −8.8) — too cold, cold pool too deep
- **NAM 1-way: +0.8 °C**, **NAM 2-way: +0.8 °C** (near-identical — nesting barely matters)
- **GFS 2-way: +2.1 °C** (manuscript draft says +1.75 on a narrower station subset)

→ **Across-configuration spread ≈ 6.8 °C** (`trang_ref` → GFS). Among *our three* runs alone it is only **~1.3 °C** — the big spread comes from adding the un-nudged reference. For context, the **nudged** January run still carried **+4 to +6 °C** residual bias.

---

## The nudging yardstick — Tran (2018), stated rigorously

From JRL's extraction of Table 1 (7 BRC sites, Jan 16–Feb 4 **episode-mean** 2 m-T bias):

| Run | Nudging | 2 m-T bias | Pearson r |
|---|---|---|---|
| **NON** | none | **+1.0 °C** | 0.829 |
| **ONU** | observational | **−0.5 °C** (best) | **0.963** |
| **OAN** | obs + analysis | **+3.0 °C** | 0.846 |
| **ANU** | analysis | **+5.0 °C** (worst) | 0.821 |

- **Nudging-choice spread = −0.5 to +5.0 °C = 5.5 °C.** That is how much the *nudging configuration alone* moved the episode-mean surface temperature.
- **The famous "~10 °C" is a peak, not a mean.** The abstract's "correcting a 10 °C warm surface temperature bias" is the *peak hourly error on the coldest inversion nights* (Fig 2a), which obs nudging removed — JRL's critique **C1** already flags calling it a "bias." Use the Table 1 means (−0.5 to +5.0 °C) as the quantitative yardstick; the ~10 °C is a "peak nighttime error" aside only.
- **`WRF_anlnudge` ≈ OAN**, the +3.0 °C row and the paper's *worst* config for inversion structure ("unrealistically extreme stratified stability") — not a run to hold up as a target.

---

## The comparison, cleanly (the paper's payoff)

> On the same basin and winter, **turning nudging on/off across its four forms moved the episode-mean surface temperature over a 5.5 °C range (Tran et al. 2018, Table 1).** In this study, on a single case and a common station set, **changing only the driving analysis and run formulation moves the surface temperature over a ~6.8 °C range** (−4.7 °C in the un-nudged long reference to +2.1 °C in the GFS short forecast). Configuration and driving-analysis choices are therefore a first-order control on near-surface temperature for this cold-air pool — **as large as the entire nudging-sensitivity spread that motivated four-dimensional data assimilation in the first place.**

Two supporting points that strengthen it:

- **A short, un-nudged NAM forecast (+0.8 °C) rivals Tran's best *nudged* long run (ONU, −0.5 °C) at the surface.** Short-forecast IC fidelity buys what nudging buys, without nudging — direct support for the touchstone approach.
- **`trang_ref` (−4.7 °C cold) matches none of Tran's four runs (all +1 to +5 °C warm).** The opposite sign is independent evidence it is a later re-run (WRF v3.9 / SIP), not one of the paper's v3.6 files — so describe it as lineage, not the paper's run.

---

## How to describe the dataset (proposed wording — `main.tex` untouched)

Replace "un-nudged reference run of `\citet{tran2018}`" (lines 156, 216) with, e.g.:

> *"…an un-nudged reference simulation of the same 1–2 February 2013 episode, drawn from the Uinta Basin State Implementation Plan modelling (WRF v3.9; configuration descended from the FDDA framework of Tran et al., 2018), reduced to the identical evaluation window."*

Keeps the Tran (2018) citation as the *configuration lineage* (defensible); stops claiming we ran their exact file.

---

## Two fidelity fixes to flag (not edit)

1. **§214 title "Same-case comparison with the *nudged* reference" is wrong.** `trang_ref` is *un-nudged*, and there is no nudged Feb run. Retitle to "…with an *un-nudged* reference"; move any nudged-run mention into clearly-labelled cross-period context.
2. **The windows don't match yet.** `trang_ref` is scored over **10** matched hours, the touchstones over **5** (14–18 UTC). The cold sign is robust (every station is cold), but **recompute `trang_ref` on the exact 14–18 UTC window** before quoting the gap. *(Qualitative story: HIGH; exact gap: verify.)*

---

## Caveats carried

- **Not identical protocol.** Tran: 7 sites, Jan 16–Feb 4 episode-mean. This study: 11 stations, Feb 2 14–18 UTC. The claim is about *comparable magnitude* ("on the order of"), not identical scoring.
- **Short vs equilibrated.** `trang_ref` is a multi-day continuous run at its own attractor; our touchstones are short forecasts near their IC. State this fair-comparison caveat (already stubbed at `main.tex:221`).
- **Warm-bias attribution is not settled.** Per `wrf-data-paper-contradictions.md` §3.4, the MYJ PBL collapses to ~18 m in inversions, so nudging reaches into the inversion column — the warm bias in nudged runs is *partly a nudging artifact*, not purely physics. Soften any "model physics" attribution to "this configuration" until a no-nudge sibling is differenced.

---

## Sources

- `verification/data/wrf_runs_scores_feb0102_postspinup_withtrang.csv`, `wrf_trang_ref_per_station.csv` — our numbers.
- `verification/baseline-eval-2013.md` — the Jan `anlnudge` +4–6 °C evaluation (MJD).
- `~/reviews/tran-2018-fdda/_paper.md` (Table 1), `critique.md` (C1), `wrf-data-paper-contradictions.md` (§3.2 version, §3.3 OAN identity, §3.4 attribution) — Tran (2018) numbers and their caveats.
- Tran, T.; Tran, H.; Mansfield, M.; Lyman, S.; Crosman, E. *Atmos. Environ.* **2018**, *177*, 75–92. <https://doi.org/10.1016/j.atmosenv.2018.01.012>.
