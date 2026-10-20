# HDZero Halo FC — ArduCopter board port (project docs)

Versioned project documentation for the HDZero Halo flight-controller ArduCopter
port. These files live under `Tools/HDZeroHalo/` so they can be committed on the
development branch without touching vehicle code.

## Document index (in Git)

| File | Purpose |
| ------ | --------- |
| `PROJECT_SCOPE.md` | Definitive goals, non-goals, status taxonomy |
| `HARDWARE_REQUIREMENTS.md` | Target hardware capabilities and evidence status |
| `PORT_STATUS.md` | Feature matrix (SUPPORTED / NEEDS_CONFIG / …) |
| `BUILD_BASELINE.md` | Toolchain qualification and H743 reference build |
| `WP1_REFERENCE_INVENTORY.md` | Read-only H743 hwdef comparison (WP0) |
| `WP1A_HARDWARE_AUDIT.md` | WP1A consolidated hardware audit |
| `WP1A_PINMAP.md` | Halo pin inventory (BF + HDZero) |
| `WP1A_DSHOT_DMA.md` | DShot300/600/bdshot + DMA feasibility |
| `WP1A_BOOTLOADER.md` | Oscillator, flash layout, DFU, board ID |
| `WP1A_DRIVER_COMPATIBILITY.md` | Existing driver coverage |
| `WP1A_BLOCKERS.md` | HARD/SOFT gates before flash |
| `WP1A_FINAL_REPORT.md` | WP1A status block + readiness |
| `WP1B_BUILD_REPORT.md` | Configure / Copter / bootloader results |
| `WP1B_DSHOT_DMA.md` | DMA generator evidence |
| `WP1B_MEMORY_LAYOUT.md` | Provisional flash / param layout |
| `WP1B_INDEPENDENT_REVIEW.md` | Review findings + fixes |
| `WP1B_FINAL_REPORT.md` | WP1B status block + readiness |
| `WP2A_HSE.md` | Oscillator evidence (still UNKNOWN) |
| `WP2A_FLASH_LAYOUT.md` | BF vs AP flash map + DFU recovery |
| `WP2A_TIM3_DMA.md` | Shared TIM3 DMA / bdshot review |
| `WP2A_PE3_POLARITY.md` | 9V PINIO polarity inference |
| `WP2A_IMU_VBAT.md` | Dual-SKU IMU + battery scales |
| `WP2A_FINAL_REPORT.md` | WP2A status block + blockers |
| `WP2A_BAROMETER.md` | External barometer defaults, retained prearm checks and USB recovery |
| `WP2A_REVIEW_FIX_REPORT.md` | Nine review findings, changes, offline validation and remaining hardware blockers |
| `WP2B_A_BETAFLIGHT_SOURCES.md` | OEM/BF provenance, CLI, hashes (WP2B-A) |
| `WP2B_A_FIRMWARE_BUILD.md` | Reproduced BF 4.5.1 Halo build |
| `WP2B_A_CLOCK_ANALYSIS.md` | HSE8 software chain vs physical unknown |
| `WP2B_A_IMU_ANALYSIS.md` | Dual SKU IMU / rotation evidence |
| `WP2B_A_POWER_ADC.md` | PE3 PINIO + VBAT/current scales |
| `WP2B_A_DSHOT_COMPARISON.md` | BF bitbang vs AP TIM3 DMA |
| `WP2B_A_BOOTLOADER_RECOVERY.md` | Flash maps and DFU return-to-BF plan |
| `WP2B_A_FINAL_REPORT.md` | WP2B-A status block |
| `WP2B_A_INDEPENDENT_REVIEW.md` | Read-only verification of key claims |
| `WP2B_B_CONNECTION.md` | WSL2 `/dev/ttyACM0` access (WP2B-B) |
| `WP2B_B_CLI_IDENTITY.md` | Live BF CLI identity dump |
| `WP2B_B_HARDWARE_COMPARE.md` | Live FC vs AP hwdef |
| `WP2B_B_FINAL_REPORT.md` | WP2B-B status block |
| `WP2B_C_SENSOR_ORIENTATION.md` | Six-face MSP Acc (corrected frame verdict) |
| `WP2B_C_FRAME_RECONCILIATION.md` | BF Y-left/Z-up vs AP FRD; ROLL_180 indicated |
| `WP2B_C_HARDWARE_GATES.md` | Remaining conditions before first AP flash |
| `WP2B_C_FINAL_REPORT.md` | WP2B-C status block |
| `WP2B_D_IMU_ROTATION_FIX.md` | Applied ICM ROLL_180 / MPU YAW_270 |
| `WP2B_D_FINAL_REPORT.md` | WP2B-D status block |
| `WP2B_F_HSE_QUALIFICATION.md` | HSE8 software vs physical unproved |
| `WP2B_F_BETAFLIGHT_RECOVERY.md` | Recovery images + DFU plan (untested) |
| `WP2B_F_FLASH_READINESS.md` | First AP USB-bench gate score |
| `WP2B_F_FINAL_REPORT.md` | WP2B-F status block |
| `WP2B_G_NO_BARO_RESTORE.md` | HAL_BARO_ALLOW_INIT_NO_BARO for no-baro startup |
| `WP2B_H_DFU_ENTRY.md` | Unsupported software DFU disabled; physical BOOT recovery retained |
| `WP3_C_USB_CLOCK_FIX.md` | HSI64/HSI48 USB clock path |
| `WP3_E_DIAG_BOOTLOADER.md` / `WP3_E2_*.md` | Isolated diagnostic bootloader |
| `WP3_H_USB_RECOVERY.md` / `WP3_H2_RMVF_FIX.md` | `strlen` + RCC_RSR recovery |
| `WP3_J_PRODUCTION_USB_BOOT.md` | Production BL+app rebuild (images) |
| `WP3_K_PRODUCTION_FIRST_BOOT.md` | Hardware flash + first USB boot |
| `WP4_A_USB_IMU_ATTITUDE.md` | USB IMU / attitude qualification |
| `WP4_B_QUAD_X.md` | Live Quad/X frame params |
| `WP4_C_FC_USB_INVENTORY.md` | Full 1195-param inventory |
| `HARDWARE_BASELINE.md` | Locked USB/MAVLink baseline summary |
| `evidence/` | Curated reports + hashes (no flash dumps) |

**Board target:** `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/`

**Hardware USB baseline:** TESTED on WP3-K / WP4-A/B/C — see `HARDWARE_BASELINE.md`.
Further flash / ARM / flight still require separate authorization
(`HARDWARE_FLASH_ALLOWED = NO`).

## Outside Git (project root)

Path: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/`

| Path | Purpose |
| ------ | --------- |
| `docs/` | Working notes / mirrors not required in the ArduPilot fork |
| `evidence/` | Full logs, flash dumps, staging trees — keep out of Git |

Large flash dumps and raw captures under the project `evidence/` tree must not
be committed. Curated report copies live in `Tools/HDZeroHalo/evidence/`.

## Branch / base

- Development branch: `board/hdzero-halo`
- Upstream base SHA: see `BUILD_BASELINE.md`
- No Halo hwdef implementation in WP0
