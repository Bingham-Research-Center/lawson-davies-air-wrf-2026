# WRF run → paper/report map (Trang & Huy Tran focus)

Reconciliation of the archived CHPC WRF runs against the papers/reports they belong to,
so the *Air* manuscript cites the right run and nothing is mislabelled.
This is the "Next" step left open by
[`CHPC-WRF-INVENTORY-RESULTS.md`](CHPC-WRF-INVENTORY-RESULTS.md):
*reconcile the manifests/configs against the run lookup table.*

**Scope.** Focus is **Trang Tran** and **Huy Tran** (and the OSIP/SIP lineage).
Runs by **John Lawson** (`pelican2013_*`, `feb2013_*`, `jan2013_*`) and Michael Davies are
**excluded** from the matching (listed in §7 for boundary clarity), except where the
manuscript risks confusing them with Trang's.

**Evidence base.** All claims below are re-derivable, read-only, from the inventory archive
`wrf_provenance_20260709T224907Z.tgz`
(sha256 `b616ec6b4ff70f3a36048904d5cad7a99a2563ba4a19fd79198fbf923332a958`;
generated 2026-07-09 on `notchpeak1` as `u0737349`, script commit `f01b129`; **not** committed
to this public repo, per the handoff) plus the committed
[`namelist_candidates.txt`](namelist_candidates.txt) and `verification/data/*.csv`.
Confidence is stated per claim; four items genuinely need author confirmation (§8).

---

## 1. The one fingerprint that settles most "whose run is it?" questions

| Look at… | John (exclude) | Trang / Huy (`archive:`) |
|---|---|---|
| vertical levels (`e_vert`) | **75** (d04 add-on: 50) | **37 or 42** |
| grid spacing (`dx`) | **3 / 1 / 0.333 km** | **12 / 4 / 1.333 km** |

The two families cannot be confused once you read `dx` + `e_vert`.
All Trang/Huy runs share the same physics — Thompson microphysics (`mp_physics=8`),
RRTMG radiation (`ra_lw/sw=4`), MYJ PBL + MYJ surface layer (`bl_pbl=2`, `sf_sfclay=2`),
Noah LSM (`sf_surface=2`) — so physics options do **not** distinguish runs; resolution,
level count, run length, and FDDA state do.

---

## 2. Plain-language findings — what's labelled right, what looks wrong

Each item: **label → verdict**, the evidence, my confidence, and what to check.

### 2.1 "Everything in a `trang_*` folder is Trang's run" — **WRONG** (storage bucket ≠ authorship)
The archive sorts data into folders named for Trang (`trang`, `trang_G3/G4/G5`, `trang_sound`,
`trang_homebk_*`). But **Huy Tran's runs live inside them**: `WRF_HUY*_Janfeb15`,
`HUY19_b1/b2/b3_*`, `WRFOUT_HUY/Jan31_*`, and a whole `WRF_HUY19/` folder inside Trang's
May-2021 home backup. The folder tells you **where it's stored**, not **who ran it**.
**Rule:** attribute by run-name prefix — `HUY*`/`HUY19*` → Huy; `REF*`/`REIN*`/`anlnudge`/
`T1_`/`T3_`/`sound` → Trang. **Confidence: HIGH** (folder + file listings).

### 2.2 "Janfeb15 is the Jan–Feb 2013 episode" — **WRONG** (it's the year 2015)
`WRF_HUY*_Janfeb15` files are named `wrfout_d01_2015-01-05...` — "15" is **2015**, a different
case. `verification/baseline-eval-2013.md` already says *"WRF_HUY*_Janfeb15 is a 2015 case —
ignore it."* Correctly excluded. **Confidence: HIGH.**

### 2.3 "The un-nudged reference run of Tran (2018) = `REF_long`" — **the word "un-nudged" is OK; the *file* and the *citation* are the soft spots**

**Nudging status (correcting a first-pass misread).** A quick look suggests `REF_long`'s
namelist has obs-nudging on (`obs_nudge_wind = 0,1,1`, `obs_nudge_temp = 0,1,1`). It does
**not**: the master switches are **off** — `grid_fdda = 0,0,0` **and** `obs_nudge_opt = 0,0,0`
— so those coefficients are inactive. `REF_long` as captured is **un-nudged**, consistent with
the manuscript's wording. **But** *every* captured SIP `_frozone` namelist (`REF_long`,
`REIN_b1/b2/b3`) is FDDA-off-at-the-master while still carrying staged nudging machinery
(`gfdda_inname`, obs coefficients) — i.e. they read like **templates**. So you **cannot** read a
SIP run's true nudging state from these captured copies; confirm from the *as-run* namelist +
`rsl` logs. (For contrast, the one genuinely nudged Trang capture is the `anlnudge`/
`revised_nudge` baseline: `grid_fdda = 1,1,1`, obs on d03.)

**Which file (solid).** The staged `trang_ref` data in
`verification/data/wrf_trang_ref_per_station.csv` covers **2013-02-02 00:00–23:00** (264 rows =
11 stations × 24 h), i.e. through the 14–18 UTC evaluation window and beyond. The captured
`REF_long` namelist runs only **96 h** (Jan 29 12Z → **Feb 2 12Z**) and **cannot** produce the
13–23 UTC frames. A longer run can: **`REF_nonudge`** (324 h → Feb 12; single 1.333 km domain;
empty `&fdda`), or a `REF_long` restart/continuation. So FIRST-50 **task 12's "`REF_long`" is
imprecise** about which staged file actually backs the comparison. **Confidence base-96 h
`REF_long` is not the direct source: HIGH.** (Mean post-spin-up 2 m-T bias in that table ≈
**−4.7 °C** over 11 stations — same sign/size as the manuscript's draft −4.4 °C; finalise per
FIRST-50 task 20.)

**Which paper (attribution).** The reference is credited to **Tran et al. (2018)**, the
published FDDA paper. But the recovered `REF_long`/`REF_nonudge` settings come from Trang's
**2020 and 2021** home backups, are built on **WRF v3.9**, and live under **`WRF_SIP`** — SIP =
**State Implementation Plan**, the later regulatory ozone modelling (OSIP-2021 / annual-report
lineage). Same 2013 weather case, configuration descended from Tran (2018), but the specific run
looks like a **2020–21 SIP re-run**, not the 2018 paper's file. Citing it as "the Tran (2018)
run" likely over-claims. Safer: *"an un-nudged reference from the Uinta Basin SIP modelling
(Trang Tran; configuration after Tran et al. 2018)."* **Confidence 2020–21 SIP vintage:
MEDIUM–HIGH** (backup dates + WRF3.9 + `WRF_SIP`).

### 2.4 "The frozone run" — **AMBIGUOUS** (a config nickname, not one run)
"frozone" appears as a folder (`WRF_TRANG_frozone`) *and* a namelist suffix (`..._USGS33_frozone`),
reused across several runs — the nudged baseline, SIP `REF_long`, the `REIN` variants, and Huy's
`HUY19/run_HEI`. It denotes the winter-("frozen")-ozone configuration family. Always say *which*
frozone run. **Confidence: HIGH.**

### 2.5 The baseline run's date vs its recovered namelist don't line up — **CHECK**
`baseline-eval-2013.md` scores `WRF_TRANG_frozone/WRF_anlnudge` over **Jan 15–21 2013**, but the
only recovered nudging namelist (`revised_nudge`, the closest to "anlnudge") starts **Feb 4 2013**
with **42 levels**. So the recovered config doesn't obviously belong to the Jan-15–21 run scored —
either that run used a namelist we haven't captured, or "anlnudge" and "revised_nudge" differ.
Confirm before Methods quotes any of these as "the baseline config." **Confidence a mismatch needs
resolving: MEDIUM.**

### 2.6 `ldavid` — **AMBIGUOUS** owner, and empty anyway
The `ldavid` archive folder holds **0 WRF files** (nothing matched `wrfout*`/`namelist*`/…). The
name reads like "L. David"; the bibliography has **"David, L."** (RMP 2022) — but coauthors are
Michael J. **Davies** and Loknath **Dhar**, and FIRST-50 task 42 already flags an **"L?D" initials
typo**. David / Davies / Dhar may be getting tangled. It backs no figure (empty), but don't assume
it's Michael's or Loknath's. **Confidence empty: HIGH; owner: LOW.**

### 2.7 Michael's "own run" (the pre-warned clash) — **likely elsewhere, not in this inventory**
In this repo Michael's role is **verification/scoring/figures** — he scored *Trang's* run;
**no separate Michael-authored WRF run appears in this CHPC inventory** (the archive is
Trang/Huy/OSIP; the only brand-new runs are John's). His separate paper — **Davies et al. (2025),
the "snow shadow" study** — presumably has its own snow-depth WRF runs, and those are **not** here
(no snow/Davies tree; `ldavid` is empty). If Michael says "my run," he most likely means the
snow-shadow runs, stored somewhere un-inventoried. **Clash risk:** Methods borrowing config numbers
that are really from his snow-shadow setup. **Confidence no MJD run in this inventory: HIGH.**

---

## 3. Mapping table — archive tree → true owner → case → likely report

| Archive tree (`archive:`) | True owner | Case / dates | Config fingerprint | Likely paper/report | Conf. |
|---|---|---|---|---|---|
| `trang/WRFOUT/WRF_TRANG_frozone/WRF_anlnudge` | Trang | 2013 (scored Jan 15–21; namelist says Feb 4–10) | 12/4/1.333 km, **42 lev**, `grid_fdda=1` + obs d03 → **nudged** | Manuscript **baseline** ("beat this", +4–6 °C warm); Tran-2018 → **UBAQR-2019** sonde-nudge lineage | baseline HIGH / report MED |
| `trang/WRFOUT/WRF_HUY*_Janfeb15` (×9) | **Huy** | **Jan–Feb 2015** | — | A **2015** study — **NOT this paper** | HIGH (exclude) |
| `trang/WRFOUT/WRF_ONU`, `WRF_sounding*` | Trang | 2013? | sounding / FDDA | Tran-2018 FDDA lineage | LOW–MED |
| `trang_G5/WRF_SIP` (`REF_long*`, `REF_hybrid`, `REIN_b1/b2/b3`, MODIS, `namelists/`) | Trang | Jan 29–Feb 12 2013 | 12/4/1.333 km, **37 lev**, SIP suite | **SIP / OSIP** modelling; **source of the manuscript comparison run** | suite HIGH / exact member MED |
| — `REF_long` (within SIP) | Trang | Jan 29 12Z, **96 h → Feb 2 12Z** | 3-dom; captured `&fdda` masters **off** (template-like) | reference-run family; but too short to be the direct `trang_ref` source | MED |
| — `REF_nonudge` (within SIP) | Trang | Jan 29 12Z, **324 h → Feb 12** | **single** 1.333 km, empty `&fdda` → **un-nudged** | **best fit** for the reduced `trang_ref` (covers 13–23 UTC Feb 2) | MED |
| `trang_G3` (`HUY19_*` + large `OBSGRID`) | **Huy** (HUY19) + shared obs prep | 2013 Jan-29 case; OBSGRID spans 2010–15 | 12/4/1.333 km, 37 lev | Huy's 2019 FDDA sensitivity (Tran-2018 / OSIP lineage) | HUY19=Huy HIGH / report MED |
| `trang_G4` (`WRFOUT_HUY/Jan31_sradi*` + `WRF_SIP/REF_long*`) | **Huy** + Trang | 2013 | mixed 37/42 lev | Huy Jan-31 radiation tests + Trang SIP `REF_long` restarts | MED |
| `WRF_UB_OSIP` (inputs + outputs `REF/REIN/HYBRID/MODIS/WRFv3.9`) | Trang / group | 2013 | SIP config, packaged | **OSIP-2021** deliverable (feeds UBAQR / Ramboll / Top-Down / RMP) | HIGH (named) |
| `trang_sound` (`T1_/T3_` strong_w / weak_w / MOIS / noVerT / noVerRH) | Trang | 2013? | nudging-strength / moisture / vertical **sensitivity** | **Tran-2018** FDDA sensitivity study | MED–HIGH |
| `ldavid` | ? (L. David?) | — | **0 WRF files** | none (empty) | owner LOW |

---

## 4. Config-fingerprint appendix (the evidence that separates the runs)

From the archive's `config-key-values.txt` / full `configs/*.txt` and committed
`namelist_candidates.txt`. `&fdda` state is **as captured** — treat SIP `_frozone` copies as
templates (see §2.3).

| Config (source) | Start 2013 | Length | `max_dom` / `dx` (km) | `e_vert` | `&fdda` master state (as captured) |
|---|---|---|---|---|---|
| `revised_nudge` — May 2021 **&** July 2020 backups (`.../WRF3.9/namelist.input_revised_nudge_d03`) | Feb 04 12Z | 132 h → Feb 10 | 3 / 12·4·1.333 | **42** | `grid_fdda=1,1,1` (ON) + `obs_nudge_opt=0,0,1` → **nudged** |
| `HUY19/run_HEI` — May 2021 backup (`WRF_HUY19/WRF/run_HEI/…_USGS33_frozone`) — **Huy** | Jan 29 12Z | 96 h | 3 / 12·4·1.333 | 37 | `grid_fdda=0`; `obs_nudge_opt=0,0,0` (masters off; machinery staged) |
| `sip_ref_long` (`WRF_SIP/WRF/run_REF_long/…_USGS33_frozone`) | Jan 29 12Z | 96 h → Feb 2 12Z | 3 / 12·4·1.333 | 37 | `grid_fdda=0`; `obs_nudge_opt=0,0,0` (template-like) |
| `sip_ref_nonudge` (`run_REF_nonudge/…_sdom_nonudge`) | Jan 29 12Z | **324 h → Feb 12** | **1** / 1.333 | 37 | **empty `&fdda`** → un-nudged |
| `sip_rein_b1/b2/b3` (`run_REIN_b*/…_USGS33_frozone`) | Jan 29 12Z | 96 h | 3 / 12·4·1.333 | 37 | `grid_fdda=0`; `obs_nudge_opt=0,0,0` (template-like) |
| `sip_wps` (`WPS3.8.1_SIP/namelist_UDAQ_SIP.wps`) | Jan 29 → Feb 12 | — | `dx=12` | — | — (ingests SNODAS snow; prefix `.../TRANG/WRF_SIP/…`) |
| **JRL `pelican*` (local — EXCLUDE)** | Feb 1–2 | 6 h | 3 / 3·1·0.333 | **75** | — |

---

## 5. Which reports each lineage feeds (targets from the handoff + bibliography)

- **Tran et al. (2018)** — FDDA-impacts paper → the FDDA-sensitivity playground: `trang_sound`
  (T1/T3 nudging-strength / moisture / vertical-nudging experiments) and the nudged-vs-un-nudged
  REF contrast. **MED–HIGH.**
- **UBAQR-2019** (Lyman et al., §8) — sonde-extended nudging → the `revised_nudge` / `anlnudge`
  baseline (obs/sonde nudging on the inner domain). **MED.**
- **UBAQR-2020** (Lyman et al., §5) — coupled met–chem, realistic 2013 ozone → the SIP WRF that
  drove CMAQ (likely `REF_long`-family met). **LOW–MED.**
- **OSIP-2021** — `WRF_UB_OSIP` (literally named; curated REF/REIN/HYBRID/MODIS/WRFv3.9 with
  inputs). **HIGH.**
- **This *Air* manuscript** — John's `pelican` touchstones (excluded) + Trang's SIP un-nudged
  reference (§2.3).

---

## 6. Explicitly **not** in this inventory (state it so it isn't assumed present)

- The **2019 simulation** behind **Ramboll-2023 / Top-Down-2023 / RMP-2022** (those reports used a
  weak-inversion **2019** run — there is **no 2019-case tree** in this inventory).
- **Davies et al. (2025)** snow-shadow runs (Michael's; stored elsewhere).

---

## 7. Excluded per instruction (John's + Michael's), listed for boundary clarity

- **JRL local** (`lawson-group6/jrlawson/wrf_archive`, 75-lev 3/1/0.333 km): `pelican2013_{gfs,nam,rap}_3_1_333m_75lev` (+`_oneway`/`_terrain3s`/`_terrain5m`), `pelican2013_nam_3_1km_75lev`, `pelican2013_nam_d04_111m_50lev_*`, `feb2013_basin_nam_12_4km`, `jan2013_basin_gefs` — the manuscript's own touchstones (GFS-2way / NAM-2way / NAM-1way).
- **MJD**: verification / scoring / figures role; no dedicated WRF run in this inventory (see §2.7).

---

## 8. Open questions for the authors (confirm before Methods goes final)

**Update 2026-07-10 (JRL + Opus):** the "which dataset is the baseline?" question is now resolved —
see the root memo [`opinion-opus-data.md`](../../opinion-opus-data.md), cross-checked against JRL's
own Tran-2018 extraction in `~/reviews/tran-2018-fdda/` (`_paper.md`, `critique.md`,
`wrf-data-paper-contradictions.md`). Resolutions and the still-open residue:

**Resolved**
- [x] **Baseline = the un-nudged `trang_ref` (2 Feb), *not* the Jan `anlnudge` run.** There is **no
  nudged run covering 1–2 Feb** in the archive; the Jan `anlnudge` run is a different sub-period.
- [x] **Attribution: it is a later re-run, not the 2018 file.** `trang_ref` runs **−4.7 °C cold**,
  opposite in sign to *all four* Tran-2018 runs (Table 1: +1.0/−0.5/+3.0/+5.0 °C, all warm) — plus
  the WRF **v3.9** vs paper **v3.6** gap (contradictions §3.2). Describe as "un-nudged SIP-era
  reference, config after Tran 2018."
- [x] **`anlnudge` date "mismatch" explained** (contradictions §1): 5-day re-init batches predict
  *both* windows — Jan 15–21 = batch 1, Feb 4–10 = batch 5. And `anlnudge` ≈ the paper's **OAN**
  (grid + obs nudging), its *worst* config for inversion structure.
- [x] **Nudging yardstick quantified:** Tran-2018 Table 1 nudging-choice spread = **5.5 °C** (−0.5
  to +5.0); the "~10 °C" is peak-nighttime, not a mean (critique C1). Use for the comparison.

**Still open (need Trang or a `wrfout`/`&fdda` dump)**
- [ ] **Which staged file backs `wrf_trang_ref_per_station.csv`** — `REF_nonudge` (324 h) or a
  `REF_long` restart? Read its **as-run** namelist; the captured `_frozone` copies are template-like.
- [ ] **Is the Jan `anlnudge`/`revised_nudge` the *published* OAN, or the post-paper "targeted"
  revision** sketched in Tran-2018 §2.2.2 (contradictions §3.3)? Dictates whether a published
  evaluation of that config exists at all.
- [ ] **`ldavid` identity** (§2.6) and the **L?D** author-initials typo — David / Davies / Dhar.

---

## 9. Suggested manuscript reconciliations — **PROPOSALS ONLY (`main.tex` untouched)**

Offered for you + Michael to accept/reject; nothing has been edited. The rationale and the
proposed replacement wording now live in [`opinion-opus-data.md`](../../opinion-opus-data.md).

- **`main.tex:156–157` & `216–217`** ("un-nudged reference run of `\citet{tran2018}`"): keep
  "un-nudged" (it checks out), but (a) pin the run to the file confirmed in §8, and (b) soften the
  attribution, e.g. *"…an un-nudged reference from the Uinta Basin SIP modelling (WRF v3.9;
  configuration after Tran et al. 2018), reduced over the identical 14–18 UTC window."*
- **`main.tex:214` section title** "Same-case comparison with the **nudged** reference": mislabelled
  — `trang_ref` is *un-nudged* and there is no nudged Feb run. Retitle "…with an **un-nudged**
  reference"; keep the Jan nudged run only as clearly-flagged cross-period context.
- **`main.tex:216–217` gap number:** frame it as *configuration spread* — our four Feb configs span
  **~6.8 °C** in 2 m-T bias vs Tran-2018's **5.5 °C** nudging spread (Table 1). Same order → the
  paper's headline "difficult forecast" point.
- **Window mismatch:** `trang_ref` is scored over **10 h**, the touchstones over **5 h** (14–18 UTC);
  recompute on the identical window before quoting the gap (§2.3 / opinion memo).
- **FIRST-50 task 12** ("`REF_long`"): update to the confirmed file (likely `REF_nonudge`) once §8
  is answered.
- **FIRST-50 task 20**: the score CSV gives ≈ **−4.7 °C** (post-spin-up, 11 stations); reconcile the
  draft **−4.4 °C** (window/station subset).
- **Author contributions / `L?D` typo** (FIRST-50 task 42): resolve David / Davies / Dhar (§2.6).

---

*Regenerate the evidence:* `tar -xzOf wrf_provenance_20260709T224907Z.tgz <member>` for any
`manifests/*.directories.txt`, `config-key-values.txt`, or `configs/*.txt`; owner splits come from
the directory listings, the 2015 dating from `manifests/trang_wrfout.tsv`, and the FDDA states from
the `&fdda` blocks in `configs/*.txt`.
