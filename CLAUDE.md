# CLAUDE.md — lawson-davies-air-wrf-2026

MDPI **Air** manuscript: *"Difficult meteorological forecasts during a wintertime surface-ozone IOP"*
(Davies, Lawson, Dhar, Lyman). WRF / Uinta Basin winter ozone / cold-air pool. Built from the
official MDPI LaTeX template. Public repo under `Bingham-Research-Center`. Coauthors may all use Claude.

## Read these (source of truth)
- `main.tex` — the entire manuscript (single file: front matter, body, inline bibliography).
- `references.bib` — bib database, **currently unused** (see Bibliography).
- `figures/SOURCES.md` — where each figure came from (CHPC scripts/data).

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
- Coauthors: MJD (corresponding), JRL (lead), LD, SNL. Only BRC collaborators can push branches.
- Branch `<initials>/<topic>`; PR into `main`. `main` is **protected** (PR required; admins bypass).
- `origin/mjdavies` holds unmerged 2013-baseline-verification work (writeup/scripts/figures/scores) —
  review/merge is a separate task.
- Repo is **public** (visible to anyone; only collaborators can write).
- Overleaf caveat: syncs to `main`; admin pushes bypass protection. If sync ever fails, point Overleaf
  at an `overleaf` branch and PR into `main`.

## Lifecycle
Submit to MDPI Air → then post to preprints.org. Figures in `figures/`; log provenance in
`figures/SOURCES.md`.
