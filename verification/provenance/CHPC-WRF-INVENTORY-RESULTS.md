# CHPC WRF provenance inventory — results (2026-07-09)

Output of running `chpc_wrf_publication_inventory.sh` per
`CHPC-WRF-INVENTORY-HANDOFF.md`, full scope (core + extended + Slurm headers).
Read-only inventory; no raw WRF output was downloaded.
This is the counterpart to the handoff — hand the archive below back for
reconciliation against the run lookup table.

## Deliverable
The report archive `wrf_provenance_20260709T224907Z.tgz` is **not committed** to
this public repo — it holds raw archive listings and namelist contents for the
group's (Trang / OSIP / ldavid) private stores, per the handoff's "do not commit
the generated report." It is transferred out-of-band; verify against:
- `sha256`: `b616ec6b4ff70f3a36048904d5cad7a99a2563ba4a19fd79198fbf923332a958`
- Size: 248,382 bytes, 98 entries.
- Generated on `notchpeak1` as `u0737349`; script at commit `f01b129`.

## Archive manifests (`archive:` remote — all reachable, none FAILED)
| label | remote | objects | bytes | dirs |
|---|---|--:|--:|--:|
| trang_wrfout | `trang/WRFOUT` | 828 | 1,933,151,897,448 | 14 |
| trang_frozone_anlnudge | `trang/WRFOUT/WRF_TRANG_frozone/WRF_anlnudge` | 12 | 70,377,234,444 | — |
| trang_g5_wrf_sip | `trang_G5/WRF_SIP` | 1,147 | 1,476,552,695,884 | 37 |
| trang_g3 | `trang_G3` | 4,221 | 295,888,521,081 | 91 |
| trang_g4 | `trang_G4` | 328 | 315,014,317,734 | 16 |
| wrf_ub_osip | `WRF_UB_OSIP` | 393 | 744,944,296,214 | 9 |
| trang_sound | `trang_sound` | 375 | 667,307,152,136 | 17 |
| ldavid | `ldavid` | 0 | 0 | 0 |

Manifest filters: `wrfout_d0[123]_*`, `wrfrst_*`, `namelist*`, `OBS_DOMAIN*`,
`wrffdda*`, `rsl.out.0000`, `README*`, `Vtable*`.
`ldavid` holds no files matching those patterns — a genuine 0, not a failure.
Full listings (path / size / mtime) and per-tree directory lists are in
`manifests/` inside the archive.

## Candidate configs (`rclone cat` — all 8 captured)
Namelists in `configs/`, hashed in `configs.sha256`, key settings extracted to
`config-key-values.txt` (372 lines): revised-nudge May 2021 & July 2020, SIP
REF_long / REF_nonudge / REIN_b1 / b2 / b3, and the SIP WPS namelist.

## Local header fingerprints (John's `wrf_archive`, inside a Slurm allocation)
16 run directories fingerprinted (`ncdump -h` → `headers/*.fingerprint.txt`).
Ran with `--header-limit 20` (up from the script default 12) so every local
family is represented — including the 111 m d04 family
(`pelican2013_nam_d04_111m_50lev_oneway_terrain3s`) that the 12-cap had
excluded. Covered: `feb2013_basin_nam_12_4km`, `jan2013_basin_gefs` (×3), the
`pelican2013` 333 m / 1 km families, and the 111 m d04 runs.

## Caveat for re-runs — rclone version
The script's manifests use `rclone lsf --time-format`, a flag added in rclone
**1.58**. CHPC's `/usr/bin/rclone` *and* the default `module load rclone` are
**1.57**, which rejects the flag: every manifest then silently FAILs while the
`rclone cat` config captures still succeed (so a naive run looks half-done).
This run used `rclone/1.68.2`
(`/uufs/chpc.utah.edu/sys/installdir/rclone/1.68.2/bin`).
Before re-running, load a ≥1.58 module — e.g. `module load rclone/1.68.2` — or
the manifests come back empty. (The handoff/README's `module load rclone` is
not sufficient.)

## Next
Reconcile these manifests, config key-values, and header fingerprints against
the run lookup table to identify exact run families and the smallest raw files
(if any) whose headers still need controlled staging.
