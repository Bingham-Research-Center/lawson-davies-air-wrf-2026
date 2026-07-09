#!/usr/bin/env bash
# chpc_pathcheck.sh — provenance probe for the 2013 baseline (Trang "frozone" WRF).
#
# READ-ONLY: only ls/stat/find/grep/diff, rclone ls*, and ncdump -h. Writes nothing
# except (optionally) its own log via the tee command below.
#
# Run ON CHPC. A login node is enough for sections A–C, E; section D reads a wrfout,
# so a compute node (or a node that can see /scratch) is better.
#
#   bash chpc_pathcheck.sh 2>&1 | tee chpc_pathcheck_$(date +%F).log
#
# Edit the CONFIG block if any guessed path/name is wrong, then re-run.
# When done: paste the log back to Claude, or `git add` it under verification/ as a record.

# ------------------------------ CONFIG (edit if wrong) ------------------------------
ARCHIVE_REMOTE="archive:"                                   # Loknath's rclone remote
TRANG_TREE="${ARCHIVE_REMOTE}trang"                         # Trang's subtree on that remote
SCRATCH_WRF="/scratch/general/vast/u6060939/wrf_trang_2013" # staged wrfout (uNID owner = ?)
BRC_TOOLS="$HOME/brc-tools"                                 # verification lib + data/ outputs
BRC_WRF="$HOME/brc-wrf"                                     # WRF run configs / namelists
TRANG_RUN="WRF_TRANG_frozone"; TRANG_CONF="WRF_anlnudge"    # the baseline run id / config
HUY_PAT="WRF_HUY.*Janfeb15"                                 # the 2015 run to locate (NOT used)
RCLONE_MAXDEPTH=4                                           # bound recursive remote listings
# ------------------------------------------------------------------------------------

hdr(){ printf '\n══════════════════ %s ══════════════════\n' "$*"; }
sub(){ printf '\n---- %s ----\n' "$*"; }
fs(){  # $1=path  $2=label
  if [ -e "$1" ]; then printf '[FOUND]   %-40s %s\n' "$2" "$1"; ls -ldh "$1" 2>/dev/null
  else               printf '[MISSING] %-40s %s\n' "$2" "$1"; fi; }

hdr "0 · ENVIRONMENT"
printf 'host=%s  user=%s  date=%s\n' "$(hostname)" "$(whoami)" "$(date)"
id 2>/dev/null
command -v rclone >/dev/null && echo "rclone: $(command -v rclone)  [$(rclone version 2>/dev/null | head -1)]" || echo "rclone: NOT ON PATH  (try: module load rclone)"
command -v ncdump >/dev/null && echo "ncdump: $(command -v ncdump)" || echo "ncdump: NOT ON PATH  (try: module load netcdf-c   or   module load nco)"
command -v git    >/dev/null && echo "git:    $(command -v git)"

hdr "A · SCRATCH STAGING  (Trang wrfout, as read by Michael's pipeline)"
fs "$SCRATCH_WRF" "scratch wrf dir"
if [ -d "$SCRATCH_WRF" ]; then
  sub "who owns the uNID in this path?  (resolves 'u6060939 = who')"
  UNID=$(printf '%s' "$SCRATCH_WRF" | grep -oE 'u[0-9]{6,7}' | head -1)
  echo "owner(stat) = $(stat -c '%U' "$SCRATCH_WRF" 2>/dev/null)   uNID-in-path = ${UNID:-none}"
  [ -n "$UNID" ] && getent passwd "$UNID" 2>/dev/null
  sub "wrfout_d03 files: count / first / last / total size"
  ls -1 "$SCRATCH_WRF"/wrfout_d03_* 2>/dev/null | wc -l | sed 's/^/count: /'
  ls -1 "$SCRATCH_WRF"/wrfout_d03_* 2>/dev/null | head -1 | sed 's/^/first: /'
  ls -1 "$SCRATCH_WRF"/wrfout_d03_* 2>/dev/null | tail -1 | sed 's/^/last:  /'
  du -sh "$SCRATCH_WRF" 2>/dev/null
  sub "anything else staged?  (namelists / logs / met_em / per-station csv)"
  ls -1 "$SCRATCH_WRF" 2>/dev/null | grep -ivE '^wrfout_d03' | head -40
fi

hdr "B · brc-tools  (verification lib + the outputs the plots read)"
fs "$BRC_TOOLS" "brc-tools repo"
if [ -d "$BRC_TOOLS" ]; then
  sub "branch / HEAD  (scripts came from branch mjdavies/synoptic-2013-verify)"
  git -C "$BRC_TOOLS" branch -a 2>/dev/null | head -30
  git -C "$BRC_TOOLS" log --oneline -3 2>/dev/null
  sub "data/ outputs"
  for f in wrf_trang_2013_per_station.csv obs_basin_2013_jan1521.parquet obs_basin_2013_stids2013.parquet baseline_scores_jan1521.csv; do
    fs "$BRC_TOOLS/data/$f" "$f"
  done
  fs "$BRC_TOOLS/data/figures" "figures dir"; ls -1 "$BRC_TOOLS/data/figures" 2>/dev/null | head
  sub "station lookups (which STIDs / waypoint_groups brc_tools defines)"
  find "$BRC_TOOLS" -maxdepth 3 -iname 'lookups.toml' 2>/dev/null
fi

hdr "C · ARCHIVE REMOTE  (Loknath's rclone 'archive:')"
if command -v rclone >/dev/null; then
  sub "configured remotes  (confirm 'archive:' is real / its true name)"
  rclone listremotes 2>&1 | head
  sub "top level of $ARCHIVE_REMOTE"
  rclone lsd "$ARCHIVE_REMOTE" 2>&1 | head -40
  sub "Trang subtree — locate WRFOUT / $TRANG_RUN / $TRANG_CONF / namelists"
  rclone lsf -R --max-depth "$RCLONE_MAXDEPTH" "$TRANG_TREE" 2>/dev/null \
    | grep -iE 'wrfout|frozone|anlnudge|namelist|WRF_' | head -60
  sub "Huy run (2015, NOT used) — locate $HUY_PAT"
  rclone lsf -R --max-depth "$RCLONE_MAXDEPTH" "$ARCHIVE_REMOTE" 2>/dev/null \
    | grep -iE 'huy|Janfeb15|WRF_HUY' | head -30
else
  echo "rclone not on PATH — 'module load rclone' then re-run section C."
fi

hdr "D · WRF NAMELIST / FORCING / PHYSICS / LEVELS  (the methods gap)"
sub "D1 · physics+grid+levels+version straight from a staged wrfout (ncdump -h global attrs)"
W1=$(ls -1 "$SCRATCH_WRF"/wrfout_d03_* 2>/dev/null | head -1)
if [ -n "$W1" ] && command -v ncdump >/dev/null; then
  echo "reading: $W1"
  ncdump -h "$W1" 2>/dev/null | grep -iE \
    ':TITLE|:SIMULATION_START|:START_DATE|:DX |:DY |:BOTTOM-TOP_GRID_DIMENSION|:GRID_ID|:GRID_FDDA|:MP_PHYSICS|:BL_PBL_PHYSICS|:SF_SURFACE_PHYSICS|:SF_SFCLAY_PHYSICS|:RA_LW_PHYSICS|:RA_SW_PHYSICS|:CU_PHYSICS|:NUM_LAND_CAT'
  echo "(:BOTTOM-TOP_GRID_DIMENSION = # vertical levels; :GRID_FDDA = nudging on/off; :TITLE = WRF version)"
else
  echo "no wrfout readable here or ncdump missing — skip D1 (module load netcdf-c / nco), covered by D2/D3 instead"
fi
sub "D2 · find the run namelists (nudging + forcing live here, not in wrfout attrs)"
for base in "$SCRATCH_WRF" "$BRC_WRF"; do
  [ -d "$base" ] && find "$base" -maxdepth 3 -iname 'namelist.*' 2>/dev/null
done
command -v rclone >/dev/null && { echo "(archive candidates:)"; rclone lsf -R --max-depth 5 "$TRANG_TREE" 2>/dev/null | grep -i 'namelist' | head; }
sub "D3 · key params from the first namelist.input found (local first, else archive)"
NLI=$(for base in "$SCRATCH_WRF" "$BRC_WRF"; do [ -d "$base" ] && find "$base" -maxdepth 3 -iname 'namelist.input' 2>/dev/null; done | head -1)
GREP_KEYS='run_days|run_hours|start_|end_|interval_seconds|max_dom|e_we|e_sn|e_vert|num_metgrid|^ *dx|^ *dy|grid_fdda|gfdda|bl_pbl_physics|sf_surface_physics|sf_sfclay|mp_physics|ra_lw|ra_sw|cu_physics|damp'
if [ -n "$NLI" ]; then
  echo "namelist.input = $NLI"
  grep -iE "$GREP_KEYS" "$NLI" | sed 's/^/  /'
elif command -v rclone >/dev/null; then
  NLA=$(rclone lsf -R --max-depth 5 "$TRANG_TREE" 2>/dev/null | grep -i 'namelist.input' | head -1)
  if [ -n "$NLA" ]; then
    echo "archive namelist.input = ${TRANG_TREE}/$NLA"
    rclone cat "${TRANG_TREE}/$NLA" 2>/dev/null | grep -iE "$GREP_KEYS" | sed 's/^/  /'
  else echo "no namelist.input found locally or on archive (depth<=5)"; fi
fi
sub "D4 · forcing dataset hints (namelist.wps prefix / met_em / README / rsl logs)"
NLW=$(for base in "$SCRATCH_WRF" "$BRC_WRF"; do [ -d "$base" ] && find "$base" -maxdepth 3 -iname 'namelist.wps' 2>/dev/null; done | head -1)
[ -n "$NLW" ] && { echo "namelist.wps = $NLW"; grep -iE 'prefix|fg_name|start_date|end_date|interval_seconds|geog_data' "$NLW" | sed 's/^/  /'; }
for base in "$SCRATCH_WRF" "$BRC_WRF"; do
  [ -d "$base" ] && find "$base" -maxdepth 3 \( -iname 'met_em*' -o -iname 'README*' -o -iname 'rsl.*0000' \) 2>/dev/null | head
done
echo "note: the forcing (GFS/ERA5/FNL/NARR?) is named by the ungrib prefix / Vtable / README — NOT by wrfout."
echo "      main.tex \\dataavailability currently just guesses 'GFS WRF SYNOPTIC HRRR ETC.'"

hdr "E · brc-wrf repo  (WRF run configs / namelists)"
fs "$BRC_WRF" "brc-wrf repo"
if [ -d "$BRC_WRF" ]; then
  git -C "$BRC_WRF" branch -a 2>/dev/null | head -20
  find "$BRC_WRF" -maxdepth 3 -iname 'namelist.*' 2>/dev/null | head
  grep -riE 'frozone|anlnudge|WRF_TRANG' "$BRC_WRF" 2>/dev/null | head
fi

hdr "F · cross-check: repo's committed scores vs the CHPC copy (optional)"
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
REPO_SCORES="$REPO_ROOT/verification/data/baseline_scores_jan1521.csv"
fs "$REPO_SCORES" "repo scores csv"
if [ -f "$REPO_SCORES" ] && [ -f "$BRC_TOOLS/data/baseline_scores_jan1521.csv" ]; then
  echo "diff repo-vs-brc-tools scores:"
  diff "$REPO_SCORES" "$BRC_TOOLS/data/baseline_scores_jan1521.csv" && echo "  -> identical"
fi

hdr "SUMMARY — resolved paths (compare against Claude's table)"
printf '%-20s %s\n' "archive remotes:" "$(command -v rclone >/dev/null && rclone listremotes 2>/dev/null | tr '\n' ' ' || echo 'rclone missing')"
printf '%-20s %s   [see section C]\n' "trang WRFOUT:" "$TRANG_TREE/..."
printf '%-20s %s   [%s]\n' "scratch staging:" "$SCRATCH_WRF" "$([ -d "$SCRATCH_WRF" ] && echo FOUND || echo MISSING)"
printf '%-20s %s   [%s]\n' "brc-tools:" "$BRC_TOOLS" "$([ -d "$BRC_TOOLS" ] && echo FOUND || echo MISSING)"
printf '%-20s %s   [%s]\n' "brc-wrf:" "$BRC_WRF" "$([ -d "$BRC_WRF" ] && echo FOUND || echo MISSING)"
echo
echo "→ paste this output back to Claude, or:  git add chpc_pathcheck_*.log  (as a provenance record)"
