# WP2B_F_HSE_QUALIFICATION — HSE / clock readiness

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**HEAD at start:** `3754c26a820ccfaf0755fc175af4b3299ed46162`  
**HARDWARE_FLASH_ALLOWED = NO**

Evidence: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-f/hse/`

## Scope

Qualify the Halo HSE assumption as far as safe read-only analysis allows.
No clock-parameter or firmware changes. No flash.

## Confidence taxonomy (required)

| Level | Meaning |
| ----- | ------- |
| SOURCE_CONFIRMED | Proven from upstream/OEM source used by this board class |
| BINARY_CONFIRMED | Proven from a local binary / compile artifact |
| LIVE_MEASURED | Observed on the physical unit via read-only interface |
| PHYSICAL_UNPROVED | Not established by crystal photo, OEM BOM, or instrument |

## 1. Installed Betaflight identity (context)

From WP2B-B / WP2B-E read-only CLI/MSP:

| Field | Value | Level |
| ----- | ----- | ----- |
| Version | 2026.6.2 | LIVE_MEASURED |
| Commit | `e0b7bb01b` (“Bump version to 2026.6.2”) | LIVE_MEASURED |
| Config rev | `3a406c5` | LIVE_MEASURED |
| Target | `HDZERO_HALO` / HDZO | LIVE_MEASURED |
| CLI `CLK=` | 480 MHz | LIVE_MEASURED (software `SystemCoreClock` only) |

**480 MHz is not a physical HSE measurement.**

## 2. Betaflight 2026.6.2 clock initialisation

Pinned to commit `e0b7bb01b`:

| Check | Result | Level |
| ----- | ------ | ----- |
| `Makefile` `HSE_VALUE ?= 8000000` | Present | SOURCE_CONFIRMED |
| `-DHSE_VALUE=$(HSE_VALUE)` when set | Present | SOURCE_CONFIRMED |
| Halo `config.h` @ `3a406c5` | **No** `SYSTEM_HSE_MHZ` | SOURCE_CONFIRMED |
| `system_stm32h7xx.c`: `HSE_VALUE` defined → `RCC_PLLSOURCE_HSE` | Present | SOURCE_CONFIRMED |
| `SystemClockHSE_Config`: `RCC_HSE_ON` (crystal, not bypass) | Present | SOURCE_CONFIRMED |
| Rev.V PLL1 path for 8 MHz → 480 MHz SYSCLK | `pll1ConfigRevV` (`m`/`n`/`p` for 960 MHz VCO / ÷2) | SOURCE_CONFIRMED |
| USB clock (normal path) | `RCC_USBCLKSOURCE_HSI48` + CRS | SOURCE_CONFIRMED |

Special case in the same file: if `HSE_VALUE == 24000000`, USB may use PLL3 instead of HSI48.
Halo defaults are **not** 24 MHz HSE in source — that branch is not the Halo config path.

## 3. Halo-specific overrides

| Source | `SYSTEM_HSE_MHZ` / HSE override? |
| ------ | -------------------------------- |
| Config `3a406c5` HDZERO_HALO | None |
| Config history examined in WP2B-A | Never set on Halo |
| Cloud `EXTRA_FLAGS` on this unit | **Unknown** (no build key archived) |

## 4. Agreement with ArduPilot

Current Halo hwdef (unchanged this WP):

```text
OSCILLATOR_HZ 8000000
```

Application path (ChibiOS `stm32h7_mcuconf.h` with `HAL_CUSTOM_MCU_CLOCKRATE 480000000`):

| Item | Configured value |
| ---- | ---------------- |
| HSE | 8 MHz assumed |
| CPU (PLL1P) | 480 MHz |
| PLL3Q | 48 MHz class for USB (HSE-derived) |
| Bootloader | Same 8 MHz HSE assumption; default H743 400 MHz CPU |

**Software-side:** ArduPilot provisional HSE8 matches the normal Betaflight Halo compile default.  
**Hardware-side:** still PHYSICAL_UNPROVED.

Important asymmetry vs Betaflight:

- BF USB: HSI48 + CRS → less diagnostic of wrong HSE.
- AP USB: PLL3 from HSE tree → **more HSE-sensitive** for first USB bench.

## 5. Does 480 MHz CLI further prove 8 MHz crystal?

**No.** CLI prints the firmware’s configured `SystemCoreClock`. If HSE were a different frequency while firmware still assumed 8 MHz, PLL math would be wrong and timed I/O would be wrong — but the printed number would still say “480MHz”.

## 6. Is a crystal photo / OEM BOM / instrument still necessary?

| Need | For first USB bench? | For flight / timing-critical I/O? |
| ---- | -------------------- | --------------------------------- |
| Crystal photo / marking | **Recommended**, not a hard gate if recovery + HSE8 software chain accepted as provisional | Strongly recommended |
| OEM schematic/BOM crystal | Ideal; not found in public docs | Ideal |
| Scope / frequency counter on HSE or MCO | Best physical proof; not performed | Best physical proof |
| Live RCC register dump | Not available via normal BF CLI/MSP | Would help |

Safe read-only options still available (require explicit user permission for physical handling):

1. Photograph crystal / nearby markings.  
2. Re-read CLI `version` / `status` (already done).  
3. Do **not** enter DFU or change option bytes for clock research.

## Verdict

```text
HSE_SOURCE = SOURCE_CONFIRMED_HSE8_DEFAULT_BF_2026_6_2_AND_4_5_1
HSE_BINARY = BINARY_CONFIRMED_FOR_LOCAL_4_5_1_REPRODUCTION
HSE_LIVE_CLK_REPORT = LIVE_MEASURED_480MHZ_SOFTWARE_ONLY
HSE_PHYSICAL = PHYSICAL_UNPROVED
ARDUPILOT_OSCILLATOR_HZ = PROVISIONAL_MATCH_RETAINED_NO_CHANGE
```
