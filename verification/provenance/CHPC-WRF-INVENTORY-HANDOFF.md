# CHPC WRF provenance inventory handoff

Goal: return path/config/header evidence that can connect archived WRF runs to
Tran-2018, UBAQR-2019, OSIP-2021, later reports, and the current Air manuscript.
The script is read-only and does not download raw WRF output.

## 1. Archive search on a login node

```bash
ssh <your-unid>@notchpeak1.chpc.utah.edu
cd ~/gits/lawson-davies-air-wrf-2026
git switch jrl/first-draft
git pull --ff-only
module load rclone

export OUT="$HOME/wrf_provenance_$(date -u +%Y%m%dT%H%M%SZ)"
bash verification/provenance/chpc_wrf_publication_inventory.sh --out "$OUT"
```

This inventories the core Trang `WRFOUT` and `WRF_SIP` trees, retrieves the
small candidate namelists, and records John's top-level `*333m*` directories.

Optional broader search after the core run succeeds:

```bash
bash verification/provenance/chpc_wrf_publication_inventory.sh \
  --extended --out "$OUT"
```

The extended pass searches `trang_G3`, `trang_G4`, `WRF_UB_OSIP`,
`trang_sound`, and `ldavid`. It may take longer because rclone must list large
S3 prefixes.

## 2. Fingerprint John's raw runs on a compute node

```bash
salloc -A lawson-np -p lawson-np -N 1 -n 1 --mem=4G -t 00:30:00
module load netcdf-c
cd ~/gits/lawson-davies-air-wrf-2026
bash verification/provenance/chpc_wrf_publication_inventory.sh \
  --headers-only --out "$OUT"
exit
```

This opens at most 12 representative local wrfout files and records only their
NetCDF headers. It refuses to run header mode outside a Slurm allocation.

## 3. Return the evidence

```bash
tar -C "$(dirname "$OUT")" -czf "$OUT.tgz" "$(basename "$OUT")"
sha256sum "$OUT.tgz"
```

Do not commit the generated report. Return the `.tgz` and checksum, or at
minimum these paths:

- `report-index.tsv`
- `status/`
- `manifests/*.tsv` and `*.directories.txt`
- `configs.sha256` and `config-key-values.txt`
- `headers/*.fingerprint.txt`

The next pass will use those files to identify exact run families and select
the smallest raw archive files, if any, whose headers still need controlled
staging.
