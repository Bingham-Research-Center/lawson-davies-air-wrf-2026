# Difficult meteorological forecasts during a wintertime surface-ozone IOP

MDPI **Air** manuscript — Lawson, Davies, Dhar & Lyman (Bingham Research Center, Utah State University).
A WRF evaluation of a Uinta Basin wintertime cold-air-pool / surface-ozone episode, toward improved
meteorological fidelity as a basis for photochemical modeling.

> New here? Read this file, then skim [`CLAUDE.md`](CLAUDE.md) (the machine-facing brief). Don't open
> `Definitions/` — that's the vendored MDPI template, not our content.

## Key documents
- **Rendered PDF:** [`main.pdf`](main.pdf) — latest build, tracked in git (overwritten each compile).
- **Manuscript source:** [`main.tex`](main.tex) — single-file MDPI document.
- **Bibliography:** [`references.bib`](references.bib) — not yet wired in (see House style).
- **Figure provenance:** [`figures/SOURCES.md`](figures/SOURCES.md).
- **Archived drafts:** [`drafts/`](drafts/) — dated PDF snapshots of milestones.
- **AI / automation brief:** [`CLAUDE.md`](CLAUDE.md).

## Build
- **Overleaf** (primary) — this repo is linked; just recompile in the GUI.
- **Local** (TinyTeX + Ghostscript): `latexmk -pdf main.tex`
  - manual fallback (current inline-bib setup): `pdflatex main && pdflatex main` (add `bibtex main`
    between passes only after switching to the external `references.bib`)
- Engine: **pdfLaTeX + BibTeX** (not XeLaTeX). A fairly complete TeX is needed
  (`tlmgr install collection-latexextra collection-fontsrecommended`) plus **Ghostscript** (`gs`) to
  embed the EPS logos; without `gs` the PDF still builds but the logos show as draft boxes.

## House style (manuscript)
- **American English.**
- **One sentence per line** (semantic line breaks) for new or edited prose — keeps git diffs and PR
  review readable. Don't reflow existing paragraphs wholesale.
- The **MDPI Air template is locked** — fill in content; don't restyle layout or macros, and don't
  edit `Definitions/`.
- **Citations:** the inline list in `main.tex` is currently authoritative; `references.bib` is not yet
  connected, so don't cite from it yet. The target is MDPI's numbered (ACS) style — the inline list is
  hand-formatted to it, and `mdpi.bst` applies only with the external BibTeX variant. We do **not** use
  AMS here, even though that's the usual house default. Verify every tech-report citation against the
  source document; never invent one.
- **Disclose any generative-AI use** in the Methods section.

## Working in this repo
- Branch as `<initials>/<topic>` (e.g. `jrl/methods-draft`); open a **PR into `main`**.
- `main` is **protected**: a PR is required. Admins (currently the lead author) can override-merge when
  justified — e.g. this foundational setup. Only BRC collaborators can push branches; the repo is
  public (anyone can read).
- **Rendered-PDF policy:** `main.pdf` is tracked and **overwritten on each accepted build**. To keep a
  milestone, copy it first: `cp main.pdf drafts/main_$(date +%F)_<label>.pdf`.
- **Overleaf** is linked to `main` and syncs there. If sync ever breaks under branch protection, point
  Overleaf at an `overleaf` branch and PR into `main`.

## Managing CLAUDE.md (and AI assistants)
- `CLAUDE.md` is the **machine-facing** brief; this README is the **human-facing** one. Keep them
  consistent, not duplicated.
- When a convention changes (build, style, workflow), **update `CLAUDE.md` first** — that's what an AI
  assistant reads at the start of every session — then mirror the human-relevant parts here.
- Keep `CLAUDE.md` **terse and path-based**; its main job is to save tokens at cold start (e.g. telling
  the assistant not to read the ~1.3 MB `Definitions/` template).
- All coauthors may use Claude. Shared settings live in `.claude/settings.json` (committed); personal
  overrides go in `.claude/settings.local.json` (git-ignored). A deny-rule blocks edits to
  `Definitions/`.

## To-do
- [ ] Replace placeholder ORCID for J. Lawson in `main.tex`.
- [ ] Draft **Materials and Methods**, **Results**, **Discussion**, **Conclusions**.
- [ ] Review and merge `origin/mjdavies` (2013 baseline verification: writeup, scripts, figures, scores).
- [ ] Decide bibliography migration: Paperpile export → `references.bib` + `mdpi.bst`.
- [ ] Add real figures to `figures/`; log each in `figures/SOURCES.md`.
- [ ] Confirm all tech-report citations against source documents.
- [ ] Fill back-matter placeholders (funding, data availability, acknowledgments, author contributions).

## Status
Early draft → submit to MDPI Air → post a preprint on [preprints.org](https://www.preprints.org).
