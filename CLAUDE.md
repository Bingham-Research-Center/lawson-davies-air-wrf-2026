# CLAUDE.md — lawson-davies-air-wrf-2026

MDPI **Air** manuscript: *"Difficult meteorological forecasts during a wintertime surface-ozone IOP"*
(Lawson, Davies, Dhar, Lyman). WRF / Uinta Basin winter ozone / cold-air pool. Built from the
official MDPI LaTeX template. Public repo under `Bingham-Research-Center`. Coauthors may all use Claude.

## Read these (source of truth)
- `main.tex` — the entire manuscript (single file: front matter, body, inline bibliography).
- `references.bib` — bib database, **currently unused** (see Bibliography).
- `figures/SOURCES.md` — where each figure came from (CHPC scripts/data).

## Data, provenance & verification
- `verification/` — the 2013 evaluation pipeline (`scripts/`), per-station scores (`data/*.csv`), and
  figures. `baseline-eval-2013.md` = the Jan 15–21 nudged-run eval; the Feb 1–2 touchstone scores are
  `data/wrf_runs_scores_feb0102*.csv`.
- `verification/provenance/WRF-RUN-TO-REPORT-MAP.md` — which archived CHPC WRF run belongs to which
  paper/report (Trang/Huy Tran; SIP/OSIP lineage). Open/closed questions in its §8.
- `opinion-opus-data.md` (root) — **resolved baseline question:** the same-case baseline is the
  un-nudged `trang_ref` (a SIP re-run, config *after* Tran 2018) — **not** the Jan `anlnudge` run and
  **not** the 2018 paper's own file; our config spread (~6.8 °C) ≈ Tran-2018's nudging spread (5.5 °C).
  Read before touching any baseline/Tran wording in `main.tex`.
- Off-repo: `~/reviews/tran-2018-fdda/` — full paper extraction + journal-club critique (the Tran
  Table 1 numbers). Bulk WRF output and the provenance tarball (`wrf_provenance_*.tgz`) stay LOCAL,
  never committed (public repo).
- Attribution fingerprint: 75-lev · 3/1/0.333 km = JRL's own runs; 37/42-lev · 12/4/1.333 km =
  Trang/Huy. `trang_*` folders are storage buckets, not authorship.

## Do NOT ingest (cold-start cost)
- `Definitions/**` — vendored MDPI template (~1.3 MB: `mdpi.cls`, `mdpi*.bst`, `mdpi_apacite.sty`,
  `journalnames.tex`, logos). Don't read unless debugging a LaTeX class/style error. This is the
  largest ingest cost in the repo — skip it by default.

## Do NOT edit
- `Definitions/**` — vendored; replace only by re-downloading from MDPI, never hand-edit.
- Don't reformat MDPI layout/macros — template is locked for submission. Small, justified comment
  cleanup only; never structural changes.

## Build
House SOP (cf. sibling repos `latex-nsf-dprog`, `ffion-preprint`): **Overleaf is primary** (linked to
this repo). Local fallback on any host with TinyTeX:
- `latexmk -pdf main.tex`   (preferred)
- manual (current inline bib): `pdflatex main && pdflatex main` — no BibTeX pass needed yet; add
  `bibtex main` between passes only once the external `references.bib` is wired in

Engine = **pdfLaTeX + BibTeX** (`pdftex` documentclass option; `mdpi.bst`) — NOT XeLaTeX/biber (that's
other repos). Don't hand-edit compiled artefacts; build output is git-ignored.

Local-build deps: the MDPI class needs a fairly full TeX (`tlmgr install collection-latexextra
collection-fontsrecommended`) **and Ghostscript (`gs`)** to embed the EPS logos in `Definitions/`.
Without `gs` the PDF still builds but logos render as draft boxes. Overleaf/CHPC have both; a minimal
TinyTeX box does not.

Rendered output: `main.pdf` **is tracked** (a key reviewable document). Intermediate artefacts
(`*.aux`, `*.log`, `*-eps-converted-to.pdf`, …) are git-ignored. Overwrite `main.pdf` on each build;
copy milestones to `drafts/main_<date>_<label>.pdf` before overwriting. Don't hand-edit artefacts.

## Bibliography
- Source of truth **today** = the inline `thebibliography` in `main.tex`, hand-formatted to MDPI's
  numbered (ACS) style. `references.bib` is stale/unused — keep them from drifting; don't cite from
  the `.bib` until migrated.
- `mdpi.bst` only takes effect **if/when** you switch to the external BibTeX variant; it is not used
  by the inline list. Either way, do NOT use AMS (`ametsocV6.bst`) here — that's the house default
  elsewhere, not for MDPI.
- Planned migration (later, not now): Paperpile export → `references.bib` → `\bibliography{references}`.
- Verify tech-report citations (years, titles, sections) against the actual documents before
  submission — flagged in `main.tex`. Never invent citations.

## Writing conventions
- **American English** (matches Michael's drafts).
- New/edited prose: **semantic line breaks** (≈one sentence per line) for clean PR diffs. Do NOT
  mass-reflow Michael's existing paragraphs.
- Methods must disclose any GenAI use (placeholder already in `main.tex`).

## Hosts (3)
- **CHPC** — WRF runs, heavy compute / big data; repos `brc-wrf`, `brc-tools`. Figures/data originate here.
- **This box (Akamai/Linode)** — writing, light Python, local LaTeX builds.
- **Overleaf GUI** — linked to this repo; GUI edits sync to `main`.

## Git / collaboration
- Coauthors (manuscript order): JRL (lead + corresponding), MJD, LD, SNL. Only BRC collaborators can push branches.
- Branch `<initials>/<topic>`; PR into `main`. `main` is **protected** (PR required; admins bypass).
- 2013-baseline-verification work (writeup/scripts/figures/scores) is merged into `main` under
  `verification/` (PR #1). Reproduce-script fixes are tracked in issue #3.
- Repo is **public** (visible to anyone; only collaborators can write).
- Overleaf caveat: syncs to `main`; admin pushes bypass protection. If sync ever fails, point Overleaf
  at an `overleaf` branch and PR into `main`.

## Lifecycle
Submit to MDPI Air → then post to preprints.org. Figures in `figures/`; log provenance in
`figures/SOURCES.md`.
