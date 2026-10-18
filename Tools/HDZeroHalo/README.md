# HDZero Halo FC — ArduCopter board port (project docs)

Versioned project documentation for the HDZero Halo flight-controller ArduCopter
port. These files live under `Tools/HDZeroHalo/` so they can be committed on the
development branch without touching vehicle code.

## Document index (in Git)

| File | Purpose |
|------|---------|
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

**Board target:** `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/` — **NOT VERIFIED — DO NOT FLASH**.  
**WP2A:** `HARDWARE_FLASH_ALLOWED = NO`.

## Outside Git (project root)

Path: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/`

| Path | Purpose |
|------|---------|
| `docs/` | Working notes / mirrors not required in the ArduPilot fork |
| `evidence/` | Build logs, size reports, screenshots — keep out of Git |

Large logs and binaries under `evidence/` must not be committed.

## Branch / base

- Development branch: `board/hdzero-halo`
- Upstream base SHA: see `BUILD_BASELINE.md`
- No Halo hwdef implementation in WP0
