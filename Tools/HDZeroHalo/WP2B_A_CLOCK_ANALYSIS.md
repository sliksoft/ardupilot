# WP2B_A_CLOCK_ANALYSIS — oscillator / HSE (highest priority)

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Answers to the six required questions

### 1. Does official Halo firmware actually use HSE 8 MHz?

**Software build chain: YES (SOURCE_CONFIRMED + BINARY_CONFIRMED for local reproduction).**  
**Physical crystal: UNKNOWN (HARDWARE_REQUIRED).**

Chain for BF 4.5.1 + Halo config `0096077`:

1. Halo `config.h` has **no** `SYSTEM_HSE_MHZ` → `mk/config.mk` does not override `HSE_VALUE`.
2. `Makefile:128` → `HSE_VALUE ?= 8000000`.
3. `Makefile:195–196` and `mk/mcu/STM32H7.mk:288` pass `-DHSE_VALUE=8000000`.
4. `src/main/startup/system_stm32h7xx.c:85–90`: defined `HSE_VALUE` selects `RCC_PLLSOURCE_HSE` and `PLL_SRC_FREQ = HSE_VALUE`.
5. `SystemClockHSE_Config` enables `RCC_HSE_ON` and starts PLL1 from that source.
6. Local verbose compile of Halo firmware shows `-DHSE_VALUE=8000000`.

OEM CLI identifies the same BF/config pair (`77d01ba` / `0096077`) but does **not** print RCC registers.

### 2. Alternative build flags or revisions?

| Path | Result |
| ---- | ------ |
| Halo config history (`SYSTEM_HSE_MHZ`) | **Never** set on Halo targets examined |
| HSI fallback | Only if `HSE_VALUE` undefined at compile time — **not** the normal Halo path |
| Later BF releases on build.betaflight.com | Still listed as `STM32H743` Halo; no evidence of Halo HSE override in master config |
| Cloud `EXTRA_FLAGS` | Can override anything; factory cloud flags not retrieved |

### 3. Hardware evidence for an external 8 MHz crystal?

| Evidence | Status |
| -------- | ------ |
| Schematic / BOM crystal part | Absent |
| PCB photo with crystal marking | Not in OEM docs text extract |
| Scope / frequency counter | Not performed |
| MCU RCC dump from live board | Not performed |

**PHYSICAL_HSE_PROOF = NO.**

### 4. MCU clock register data, schematics, OEM statements?

| Source | Statement |
| ------ | --------- |
| OEM intro / manual | “STM32H743 (480MHz)” — CPU speed, not HSE Hz |
| OEM docs | No crystal frequency |
| BF PLL tables | Assume `PLL_SRC_FREQ` equals compile-time `HSE_VALUE` |
| Live `RCC->CR` / `PLLCKSELR` | HARDWARE_REQUIRED |

### 5. Agreement with ArduPilot `OSCILLATOR_HZ 8000000`?

**Software-side: consistent provisional choice (INFERRED agreement with BF defaults).**  
AP `hwdef.dat` retains `OSCILLATOR_HZ 8000000` / 480 MHz CPU. That matches BF’s compile-time HSE8 + Rev.V 480 MHz path **if** the physical part is 8 MHz HSE.

Bootloader AP path uses HSE8 with default H743 400 MHz CPU — different CPU rate, same oscillator assumption (already documented in WP2A).

### 6. Residual risks for USB, UART, DShot, SPI?

| Peripheral | Risk if physical HSE ≠ 8 MHz while firmware assumes 8 MHz |
| ---------- | -------------------------------------------------------- |
| USB (BF) | Lower for enumeration: BF H7 uses **HSI48 + CRS** for USB (`RCC_USBCLKSOURCE_HSI48`) — not HSE-derived |
| USB (AP) | Uses PLL3Q 48 MHz from HSE tree in ChibiOS HSE8 config — **more HSE-sensitive** than BF USB |
| UART / CRSF / MSP | Baud error scales with SYSCLK error |
| SPI gyro / flash | SCK error scales with kernel clocks |
| DShot bitbang (BF) | Bit timing from timers/CPU — wrong if HSE wrong |
| DShot DMA (AP) | Same class of risk; independent of BF bitbang success |

**Compiled HSE8 is not a measured oscillator.**

## PLL numbers (for 8 MHz HSE, Rev.V)

From `system_stm32h7xx.c` `pll1ConfigRevV`:

- `m = 4`, VCO target 960 MHz, `p = 2` → **480 MHz** SYSCLK  
- `q = 8` → PLL1Q 120 MHz class for SPI budgeting  

If the crystal were 25 MHz with firmware still using `HSE_VALUE=8000000`, PLL math would be wrong by 25/8 — catastrophic for timed I/O even if USB (BF) still enumerated.

## Verdict line

```text
HSE_CLOCK = SOFTWARE_HSE8_SOURCE_AND_BINARY_CONFIRMED
PHYSICAL_HSE_PROOF = NO
ARDUPILOT_OSCILLATOR_HZ = PROVISIONAL_MATCH_TO_BF_DEFAULT
```
