# WP2A_HSE — Halo MCU oscillator frequency

**Date:** 2026-10-18  
**Start-HEAD:** `1abdc924450f473670f63c91e60e737a5e534ec1`  
**HARDWARE_FLASH_ALLOWED = NO**

## Verdict

| Field | Value |
|-------|-------|
| `HSE_FREQUENCY` | **UNKNOWN** |
| Proven physical crystal Hz | **NO** |
| Safe to flash with `OSCILLATOR_HZ 8000000` | **NO** |

## Evidence matrix

| Source | What it says | Classification |
|--------|--------------|----------------|
| BF `HDZERO_HALO` `config.h` | **No** `#define SYSTEM_HSE_MHZ` | PROVEN (config blob) |
| BF `config/README.md` | `SYSTEM_HSE_MHZ` required for boards with HSE crystal; omit for internal oscillator | PROVEN (docs) |
| BF `src/main/target/common_post.h` | If undefined, `#define SYSTEM_HSE_MHZ 0` | PROVEN |
| BF `mk/config.mk` | Sets `HSE_VALUE` only when `SYSTEM_HSE_MHZ` is present in config | PROVEN |
| BF `system_stm32h7xx.c` | `#if !defined(HSE_VALUE)` → `PLL_SRC = HSI`, `PLL_SRC_FREQ = HSI_FREQ` (64 MHz) | PROVEN |
| Peer H743 BF configs (Matek/Foxeer/Mamba/iFlight) | Also omit `SYSTEM_HSE_MHZ` | PROVEN (sample) |
| HDZero Halo PDF manual / `halo-firmware.md` | No MCU crystal frequency | ABSENT |
| Public schematic / BOM | Not found | ABSENT |
| Hardware scope / RCC measurement | No Halo on USB this session | ABSENT |
| dogjutsu / unofficial forks claiming 8 MHz | Non-authoritative | REJECTED as proof |
| AP `hwdef.dat` `OSCILLATOR_HZ 8000000` | Peer H743 convention for offline compile only | **ASSUMPTION** (labelled in hwdef) |

## Interpretation

1. **Betaflight Halo firmware does not configure an HSE crystal value.** On STM32H7, that selects the **HSI → PLL** path (`HSI_FREQ = 64 MHz`), not an 8/16/25 MHz HSE.
2. That proves the **BF clock software path**, not the **presence or absence** of a physical HSE part on the PCB. Schematics and scope measurement are still required before trusting ArduPilot `OSCILLATOR_HZ`.
3. ArduPilot/ChibiOS H743 boards almost always use **HSE** via `OSCILLATOR_HZ`. Wrong Hz breaks UART baud, DShot timing, and USB. The provisional `8000000` in `HDZeroHalo/hwdef.dat` remains **compile-only**.
4. ELRS “TCXO” references (Gemini RX) are **not** the MCU HSE.

## Required before flash

- Prefer: OEM schematic / crystal marking / RCC register dump from a running BF image.  
- Or: frequency measurement of OSC_IN / confirmed HSE pin.  
- Until then: keep `HARDWARE_FLASH_ALLOWED = NO`.

## Sources (URLs / paths)

- `https://github.com/betaflight/config/blob/master/configs/HDZO/HDZERO_HALO/config.h`
- `https://github.com/betaflight/config/blob/master/README.md` (`SYSTEM_HSE_MHZ`)
- `https://github.com/betaflight/betaflight/blob/master/src/platform/STM32/startup/system_stm32h7xx.c` (HSI fallback)
- `https://github.com/betaflight/betaflight/blob/master/src/main/target/common_post.h`
- Local: `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat` L22–24; `build/HDZeroHalo/hwdef.h` `STM32_HSECLK 8000000U`
