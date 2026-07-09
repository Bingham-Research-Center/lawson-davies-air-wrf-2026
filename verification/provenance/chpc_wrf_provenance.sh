#!/usr/bin/env bash
# chpc_wrf_provenance.sh — close the methods gap for Trang's frozone / anlnudge WRF baseline.
#
# The first probe (chpc_pathcheck.sh) showed: scratch wrfout are purged, and the WRF namelist
# never surfaced at shallow depth. This one digs the specific archive subtrees that should hold
# the run's config and extracts what the paper's methods needs:
#   forcing dataset · PBL / land-surface / microphysics schemes · # vertical levels · d03 dx ·
#   analysis-nudging settings · run window.
#
# READ-ONLY, except an OPTIONAL, size-capped, auto-deleted single-wrfout download used ONLY as a
# fallback when no namelist.input is found. Run on CHPC (a node that can reach /scratch):
#
#   module load rclone netcdf-c        # (or: module load nco)
#   bash chpc_wrf_provenance.sh 2>&1 | tee chpc_wrf_provenance_$(date +%F).log
#
# Edit CONFIG if section 1 finds nothing, then re-run.

# ------------------------------- CONFIG -------------------------------
ARCHIVE="archive:"
TRANG="${ARCHIVE}trang"
# Subtrees most likely to hold the WRF run dir + its namelist (bounded — not the whole archive):
WRF_SUBTREES=(
  "${TRANG}/WRFOUT"
  "${TRANG}/input_frozone"
  "${TRANG}/run_PA_anlnudge"
  "${TRANG}/CAMx_old/input_frozone"
  "${ARCHIVE}trang_homebk_MAy2021"
  "${ARCHIVE}trang_homebk_29July2020"
)
WRFOUT_CAP_MB=800                 # fallback: skip auto-download if the smallest d03 exceeds this
MAX_CAT=4                         # cat at most this many namelists of each kind
# Run-namelist candidates identified from the 2026-07-01 dig. The revised_nudge_d03 pair have
# grid_fdda=1 => the analysis-nudged ("anlnudge") baseline config (Feb-dated file, same setup as the
# scored Jan 15-21 d03 output); USGS33_frozone is the no-nudge "frozone" physics variant.
KNOWN_NAMELISTS=(
  "${ARCHIVE}trang_homebk_MAy2021/WRF3.9/namelist.input_revised_nudge_d03"
  "${ARCHIVE}trang_homebk_29July2020/WRF3.9/namelist.input_revised_nudge_d03"
  "${ARCHIVE}trang_homebk_MAy2021/WRF_HUY19/WRF/run_HEI/namelist.input_USGS33_frozone"
)
# Backups to scan for the matching WPS namelist (names the forcing via prefix / fg_name):
WPS_SCAN_ROOTS=( "${ARCHIVE}trang_homebk_MAy2021/WRF3.9" "${ARCHIVE}trang_homebk_29July2020/WRF3.9" )
# ----------------------------------------------------------------------

hdr(){ printf '\n══════════════════ %s ══════════════════\n' "$*"; }
sub(){ printf '\n---- %s ----\n' "$*"; }
NL_KEYS='run_days|run_hours|start_year|start_month|start_day|start_hour|end_year|end_month|end_day|interval_seconds|max_dom|e_we|e_sn|e_vert|num_metgrid_levels|num_metgrid_soil_levels|^ *dx|^ *dy|grid_fdda|gfdda|guv|gt |gq |if_ramping|dtramp_min|bl_pbl_physics|sf_surface_physics|sf_sfclay_physics|mp_physics|ra_lw_physics|ra_sw_physics|cu_physics|num_soil_layers'
WPS_KEYS='wrf_core|max_dom|start_date|end_date|interval_seconds|prefix|fg_name|constants_name|geog_data_res|geog_data_path'
NC_KEYS=':TITLE|:SIMULATION_START|:START_DATE|:DX |:DY |:BOTTOM-TOP_GRID_DIMENSION|:GRID_ID|:GRID_FDDA|:MP_PHYSICS|:BL_PBL_PHYSICS|:SF_SURFACE_PHYSICS|:SF_SFCLAY_PHYSICS|:RA_LW_PHYSICS|:RA_SW_PHYSICS|:CU_PHYSICS|:NUM_LAND_CAT|:NUM_METGRID_LEVELS'

hdr "0 · TOOLS"
command -v rclone >/dev/null && echo "rclone: $(rclone version 2>/dev/null | head -1)" || { echo "rclone NOT on PATH — 'module load rclone' and re-run"; }
command -v ncdump >/dev/null && echo "ncdump: present" || echo "ncdump NOT on PATH (only needed for the fallback) — 'module load netcdf-c' / 'module load nco'"
echo "user=$(id -un)  host=$(hostname)  date=$(date)"

hdr "1 · LOCATE NAMELISTS in the likely subtrees"
ALL_NL=""
for st in "${WRF_SUBTREES[@]}"; do
  sub "$st"
  found=$(rclone lsf -R --fast-list "$st/" 2>/dev/null | grep -i 'namelist')
  if [ -n "$found" ]; then
    printf '%s\n' "$found" | sed "s#^#  $st/#"
    ALL_NL+=$(printf '%s\n' "$found" | sed "s#^#$st/#")$'\n'
  else
    echo "  (none, or subtree absent)"
  fi
done
NLI_LIST=$(printf '%s' "$ALL_NL" | grep -iE 'input' | grep -viE '\.log$|README' )
NLW_LIST=$(printf '%s' "$ALL_NL" | grep -iE 'wps' )
echo; echo "namelist.input candidates: $(printf '%s' "$NLI_LIST" | grep -c . )    namelist.wps candidates: $(printf '%s' "$NLW_LIST" | grep -c . )"

hdr "2 · CONFIRM THE d03 BASELINE (WRFOUT/ contents — Jan 15-21 2013?)"
d03=$(rclone ls "${TRANG}/WRFOUT/" 2>/dev/null | awk '$2 ~ /wrfout_d03/')
if [ -n "$d03" ]; then
  echo "wrfout_d03 under WRFOUT/: $(printf '%s\n' "$d03" | wc -l) files"
  sub "earliest / latest (by name) + sizes (bytes)"
  printf '%s\n' "$d03" | sort -k2 | sed -n '1,3p'
  echo "   ..."
  printf '%s\n' "$d03" | sort -k2 | tail -3
else
  echo "no wrfout_d03 directly under ${TRANG}/WRFOUT/ — listing its top level:"
  rclone lsf --dirs-only "${TRANG}/WRFOUT/" 2>/dev/null | head -30
  echo "(look for a subdir holding the Jan-2013 d03 files, then set that as WRFOUT path)"
fi

hdr "3 · WRF namelist.input → physics / levels / nudging / window"
if [ -n "$NLI_LIST" ]; then
  n=0
  while IFS= read -r nl; do
    [ -z "$nl" ] && continue
    n=$((n+1)); [ "$n" -gt "$MAX_CAT" ] && { echo "(more namelist.input candidates not shown)"; break; }
    sub "$nl"
    rclone cat "$nl" 2>/dev/null | grep -iE "$NL_KEYS" | sed 's/^/  /'
  done <<< "$NLI_LIST"
else
  echo "No namelist.input found in the probed subtrees — see the fallback in section 5,"
  echo "and consider asking Michael for the exact archive:trang/WRFOUT/<subpath> he staged from."
fi

hdr "4 · WPS namelist / forcing dataset (GFS? ERA5? FNL? NARR?)"
if [ -n "$NLW_LIST" ]; then
  n=0
  while IFS= read -r nl; do
    [ -z "$nl" ] && continue
    n=$((n+1)); [ "$n" -gt "$MAX_CAT" ] && break
    sub "$nl"
    rclone cat "$nl" 2>/dev/null | grep -iE "$WPS_KEYS" | sed 's/^/  /'
  done <<< "$NLW_LIST"
else
  echo "No namelist.wps found. Forcing hints to chase next:"
fi
sub "met_em / Vtable / GRIBFILE / README near the run (name the forcing)"
for st in "${WRF_SUBTREES[@]}"; do
  rclone lsf -R --fast-list "$st/" 2>/dev/null | grep -iE 'met_em|Vtable|GRIBFILE|ungrib|README|namelist\.wps' | sed "s#^#  $st/#" | head -20
done

hdr "5 · FALLBACK — read one wrfout header (only if no namelist.input above)"
if [ -n "$NLI_LIST" ]; then
  echo "skipped — namelist.input was found (section 3 is authoritative)."
elif ! command -v ncdump >/dev/null; then
  echo "skipped — ncdump missing. 'module load netcdf-c' (or nco) and re-run to use this fallback."
else
  cand=$(rclone ls "${TRANG}/WRFOUT/" 2>/dev/null | awk '$2 ~ /wrfout_d03/' | sort -n | head -1)
  sz=$(printf '%s' "$cand" | awk '{print $1}'); rel=$(printf '%s' "$cand" | awk '{print $2}')
  if [ -z "$rel" ]; then
    echo "no d03 wrfout under WRFOUT/ to sample."
  elif [ "${sz:-0}" -gt $(( WRFOUT_CAP_MB * 1024 * 1024 )) ]; then
    printf 'smallest d03 is %s MB > cap %s MB — NOT auto-downloading. To do it manually:\n' "$(( sz/1024/1024 ))" "$WRFOUT_CAP_MB"
    echo "  rclone copy \"${TRANG}/WRFOUT/$rel\" \$SCRATCH_TMP/ && ncdump -h \$SCRATCH_TMP/$(basename "$rel") | grep -E '$NC_KEYS'"
  else
    stg="/scratch/general/vast/$(id -un)"; [ -d "$stg" ] || stg=$(mktemp -d)
    tmp=$(mktemp -d "${stg}/wrfmeta.XXXXXX")
    echo "downloading $(basename "$rel")  (${sz} bytes) to $tmp ..."
    if rclone copy "${TRANG}/WRFOUT/$rel" "$tmp/" 2>/dev/null; then
      echo "global attrs (physics / levels / nudging / WRF version):"
      ncdump -h "$tmp/$(basename "$rel")" 2>/dev/null | grep -iE "$NC_KEYS" | sed 's/^/  /'
      echo "(NUM_METGRID_LEVELS hints the forcing; BOTTOM-TOP_GRID_DIMENSION = # vertical levels; GRID_FDDA = nudging on)"
    else
      echo "download failed (network / quota) — try the manual one-liner above."
    fi
    rm -rf "$tmp"
  fi
fi

hdr "6 · DUMP the identified run-namelist candidates (regenerates namelist_candidates.txt)"
for nl in "${KNOWN_NAMELISTS[@]}"; do
  echo "########## $nl ##########"
  rclone cat "$nl" 2>/dev/null || echo "(cat failed — path moved; re-run section 1 to relocate)"
  echo
done

hdr "6b · FORCING — prefix/fg_name from the real WPS namelists (names GFS/ERA/FNL/NARR)"
for root in "${WPS_SCAN_ROOTS[@]}"; do
  rclone lsf -R --fast-list "$root/" 2>/dev/null \
    | grep -iE 'namelist\.wps$' | grep -viE 'geogrid|/util/|/test/|WRFDA' \
    | while IFS= read -r w; do
        echo "-- $root/$w"
        rclone cat "$root/$w" 2>/dev/null | grep -iE 'prefix|fg_name|start_date|end_date|interval_seconds' | sed 's/^/    /'
      done
done

hdr "SUMMARY"
echo "namelist.input found : $( [ -n "$NLI_LIST" ] && echo YES || echo NO )"
echo "namelist.wps found   : $( [ -n "$NLW_LIST" ] && echo YES || echo NO )"
echo "→ paste this log back to Claude; sections 3/4 (or 5) are what I need for the methods paragraph."
