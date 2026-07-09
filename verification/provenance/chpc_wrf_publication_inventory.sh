#!/usr/bin/env bash
# Read-only WRF provenance inventory for CHPC and the group rclone archive.

set -uo pipefail
IFS=$'\n\t'

ARCHIVE_REMOTE="${ARCHIVE_REMOTE:-archive:}"
JRL_ARCHIVE="${JRL_ARCHIVE:-/uufs/chpc.utah.edu/common/home/lawson-group6/jrlawson/wrf_archive}"
OUT=""
DO_CORE=1
DO_EXTENDED=0
DO_HEADERS=0
HEADER_LIMIT=12

usage() {
  cat <<'EOF'
Usage: chpc_wrf_publication_inventory.sh [options]

Options:
  --out DIR         Output directory (default: ./wrf_provenance_<UTC stamp>)
  --extended        Also scan G3/G4, OSIP, sounding, and Liji archive roots
  --headers-only    Skip rclone searches; fingerprint local JRL wrfout headers
  --headers         Run core searches and local header fingerprints
  --header-limit N  Maximum local run directories to fingerprint (default: 12)
  -h, --help        Show this help

Core and extended searches are read-only. Header mode is also read-only but must
run inside a Slurm allocation because it opens representative wrfout files.
EOF
}

while (($#)); do
  case "$1" in
    --out)
      OUT=${2:?--out needs a directory}
      shift 2
      ;;
    --extended)
      DO_EXTENDED=1
      shift
      ;;
    --headers-only)
      DO_CORE=0
      DO_HEADERS=1
      shift
      ;;
    --headers)
      DO_HEADERS=1
      shift
      ;;
    --header-limit)
      HEADER_LIMIT=${2:?--header-limit needs a number}
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

[[ $HEADER_LIMIT =~ ^[1-9][0-9]*$ ]] || {
  printf 'Invalid --header-limit: %s\n' "$HEADER_LIMIT" >&2
  exit 2
}

OUT=${OUT:-"$PWD/wrf_provenance_$(date -u +%Y%m%dT%H%M%SZ)"}
mkdir -p "$OUT" "$OUT/manifests" "$OUT/configs" "$OUT/headers" "$OUT/status"
exec > >(tee -a "$OUT/run.log") 2>&1

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { printf '[%s] %s\n' "$(stamp)" "$*"; }

manifest_filters=(
  --include 'wrfout_d0[123]_*'
  --include '**/wrfout_d0[123]_*'
  --include 'wrfrst_d0[123]_*'
  --include '**/wrfrst_d0[123]_*'
  --include 'namelist*'
  --include '**/namelist*'
  --include 'OBS_DOMAIN*'
  --include '**/OBS_DOMAIN*'
  --include 'wrffdda*'
  --include '**/wrffdda*'
  --include 'rsl.out.0000'
  --include '**/rsl.out.0000'
  --include 'README*'
  --include '**/README*'
  --include 'Vtable*'
  --include '**/Vtable*'
  --exclude '*'
)

remote_manifest() {
  local label remote out
  label=$1
  remote=$2
  out="$OUT/manifests/${label}.tsv"
  note "inventory $remote"
  if rclone lsf -R --files-only --format pst --separator $'\t' \
      --time-format '2006-01-02T15:04:05Z07:00' \
      "${manifest_filters[@]}" "$remote" >"$out" 2>"$out.stderr"; then
    awk -F '\t' '
      {n++; if ($2 ~ /^[0-9]+$/) bytes += $2}
      END {printf "objects=%d bytes=%d\n", n, bytes}
    ' "$out" | tee "$OUT/status/${label}.summary"
    cut -f1 "$out" | sed '/\//!d; s#/[^/]*$##' | sort -u \
      >"$OUT/manifests/${label}.directories.txt"
  else
    printf 'FAILED %s\n' "$remote" | tee "$OUT/status/${label}.summary"
  fi
}

capture_config() {
  local label remote out
  label=$1
  remote=$2
  out="$OUT/configs/${label}.txt"
  note "capture config $remote"
  if ! rclone cat "$remote" >"$out" 2>"$out.stderr"; then
    printf 'FAILED %s\n' "$remote" >"$OUT/status/${label}.summary"
  fi
}

if ((DO_CORE)); then
  command -v rclone >/dev/null || {
    printf 'rclone is required; on CHPC run: module load rclone\n' >&2
    exit 3
  }

  {
    printf 'observed_at=%s\n' "$(stamp)"
    printf 'host=%s\n' "$(hostname)"
    printf 'user=%s\n' "$(whoami)"
    printf 'archive_remote=%s\n' "$ARCHIVE_REMOTE"
    printf 'jrl_archive=%s\n' "$JRL_ARCHIVE"
    rclone version | head -1
  } >"$OUT/environment.txt"

  rclone listremotes >"$OUT/archive-remotes.txt" 2>"$OUT/archive-remotes.stderr" || true
  rclone lsd "$ARCHIVE_REMOTE" >"$OUT/archive-top-level.txt" \
    2>"$OUT/archive-top-level.stderr" || true

  remote_manifest trang_wrfout "${ARCHIVE_REMOTE}trang/WRFOUT"
  remote_manifest trang_frozone_anlnudge \
    "${ARCHIVE_REMOTE}trang/WRFOUT/WRF_TRANG_frozone/WRF_anlnudge"
  remote_manifest trang_g5_wrf_sip "${ARCHIVE_REMOTE}trang_G5/WRF_SIP"

  capture_config revised_nudge_may2021 \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF3.9/namelist.input_revised_nudge_d03"
  capture_config revised_nudge_july2020 \
    "${ARCHIVE_REMOTE}trang_homebk_29July2020/WRF3.9/namelist.input_revised_nudge_d03"
  capture_config sip_ref_long \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF_SIP/WRF/run_REF_long/namelist.input_USGS33_frozone"
  capture_config sip_ref_nonudge \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF_SIP/WRF/run_REF_nonudge/namelist.SIP_REF_long_USGS33_sdom_nonudge"
  capture_config sip_rein_b1 \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF_SIP/WRF/run_REIN_b1/namelist.input_USGS33_frozone"
  capture_config sip_rein_b2 \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF_SIP/WRF/run_REIN_b2/namelist.input_USGS33_frozone"
  capture_config sip_rein_b3 \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF_SIP/WRF/run_REIN_b3/namelist.input_USGS33_frozone"
  capture_config sip_wps \
    "${ARCHIVE_REMOTE}trang_homebk_MAy2021/WRF3.9/WPS3.8.1_SIP/namelist_UDAQ_SIP.wps"

  if ((DO_EXTENDED)); then
    remote_manifest trang_g3 "${ARCHIVE_REMOTE}trang_G3"
    remote_manifest trang_g4 "${ARCHIVE_REMOTE}trang_G4"
    remote_manifest wrf_ub_osip "${ARCHIVE_REMOTE}WRF_UB_OSIP"
    remote_manifest trang_sound "${ARCHIVE_REMOTE}trang_sound"
    remote_manifest ldavid "${ARCHIVE_REMOTE}ldavid"
  fi

  : >"$OUT/configs.sha256"
  : >"$OUT/config-key-values.txt"
  for config in "$OUT"/configs/*.txt; do
    [[ -s $config ]] || continue
    sha256sum "$config" >>"$OUT/configs.sha256"
    printf '\n===== %s =====\n' "${config##*/}" >>"$OUT/config-key-values.txt"
    grep -nEi \
      'run_days|run_hours|start_|end_|interval_seconds|e_vert|p_top|num_metgrid|^[[:space:]]*dx|^[[:space:]]*dy|feedback|grid_fdda|gfdda_|if_no_pbl|guv|^[[:space:]]*gt|^[[:space:]]*gq|obs_nudge|obs_coef|obs_rinxy|obs_twindo|obs_dtramp|mp_physics|bl_pbl|sf_surface|sf_sfclay|ra_lw|ra_sw|cu_physics|num_land_cat|prefix|fg_name' \
      "$config" >>"$OUT/config-key-values.txt" || true
  done
fi

note "inventory local JRL archive"
if [[ -d $JRL_ARCHIVE ]]; then
  find "$JRL_ARCHIVE" -maxdepth 2 -type d -name '*333m*' \
    -printf '%p\t%TY-%Tm-%TdT%TH:%TM:%TS\n' | sort \
    >"$OUT/jrl-333m-directories.tsv"
else
  printf 'MISSING %s\n' "$JRL_ARCHIVE" >"$OUT/status/jrl-archive.summary"
fi

if ((DO_HEADERS)); then
  [[ -n ${SLURM_JOB_ID:-} ]] || {
    printf 'Header mode requires a Slurm allocation. Use --headers-only inside salloc.\n' >&2
    exit 4
  }
  command -v ncdump >/dev/null || {
    printf 'ncdump is required; on CHPC run: module load netcdf-c\n' >&2
    exit 5
  }
  find "$JRL_ARCHIVE" -maxdepth 6 -type f \
    \( -name 'wrfout_d0[123]_*' -o -name 'wrfrst_d0[123]_*' \
       -o -name 'namelist.input*' -o -name 'namelist.wps*' \) \
    -printf '%p\t%s\t%TY-%Tm-%TdT%TH:%TM:%TS\n' | sort \
    >"$OUT/jrl-archive-files.tsv"
  [[ -s $OUT/jrl-archive-files.tsv ]] || {
    printf 'No local JRL archive manifest found in %s\n' "$OUT" >&2
    exit 6
  }

  cut -f1 "$OUT/jrl-archive-files.tsv" | grep '/wrfout_d0[123]_' \
    | sed 's#/wrfout_d0[123]_[^/]*$##' | sort -u \
    >"$OUT/header-run-directories.txt"

  count=0
  while IFS= read -r run_dir && ((count < HEADER_LIMIT)); do
    sample=$(find "$run_dir" -maxdepth 1 -type f -name 'wrfout_d02_*' -print -quit)
    [[ -n $sample ]] || sample=$(find "$run_dir" -maxdepth 1 -type f -name 'wrfout_d03_*' -print -quit)
    [[ -n $sample ]] || continue
    count=$((count + 1))
    label=$(printf '%03d_%s' "$count" "$(basename "$run_dir")")
    printf '%s\t%s\n' "$label" "$sample" >>"$OUT/header-samples.tsv"
    ncdump -h "$sample" >"$OUT/headers/${label}.ncdump.txt"
    grep -Ei \
      ':TITLE|:SIMULATION_START|:START_DATE|:DX|:DY|:GRID_ID|:PARENT_ID|:WEST-EAST_GRID_DIMENSION|:SOUTH-NORTH_GRID_DIMENSION|:BOTTOM-TOP_GRID_DIMENSION|:GRID_FDDA|:MP_PHYSICS|:BL_PBL_PHYSICS|:SF_SURFACE_PHYSICS|:SF_SFCLAY_PHYSICS|:RA_LW_PHYSICS|:RA_SW_PHYSICS|:CU_PHYSICS|:NUM_LAND_CAT' \
      "$OUT/headers/${label}.ncdump.txt" >"$OUT/headers/${label}.fingerprint.txt" || true
  done <"$OUT/header-run-directories.txt"
fi

find "$OUT" -type f ! -name report-index.tsv -printf '%P\t%s\n' | sort \
  >"$OUT/report-index.tsv"
note "done: $OUT"
note "return report-index.tsv, status/, manifests/, configs.sha256, config-key-values.txt, and headers/"
