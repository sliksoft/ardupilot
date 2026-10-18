# WP2B_A_FIRMWARE_BUILD — reproducible Halo Betaflight 4.5.1 build

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Goal

Reproduce the official Halo target with the toolchain Betaflight 4.5.1 expects, pinned to the OEM CLI’s config revision.

## Build identity

| Field | Value |
| ----- | ----- |
| BF source | tag `4.5.1` / `77d01ba3b76a22909d5f09cb0628820141f95eaa` |
| Config | `009607753079525bbdec1395a1773b79127990ab` (`0096077`) |
| Toolchain | Official BF `make arm_sdk_install` → GCC **10.3.1** 2021.10 |
| Host gcc rejected | System `13.2.1` (tools.mk version gate) |
| Command | `make -j hex CONFIG=HDZERO_HALO` |
| Output hex | `obj/betaflight_4.5.1_STM32H743_HDZERO_HALO.hex` |

Artifacts: `evidence/wp2b-a/firmware/reproduced/`  
Log: `evidence/wp2b-a/build/build_hdzero_halo_4.5.1.log`

| Artifact | SHA256 |
| -------- | ------ |
| Hex | `d2f590334043684e1339c71e8e2767cc7d5da4bdd1e6ded26e829b1325ef3a03` |
| ELF | `0d38a2b79345cee3f9950d1c93134c8b9f5b8ed3e1445291c6f1094d9a7c68d9` |

ELF strings embed `4.5.1`, `77d01ba`, `0096077`, `HDZERO_HALO`, `STM32H743` (**BINARY_CONFIRMED** for this local image).

## Compiler / MCU flags (SOURCE + build log)

Verbose compile of `system_stm32h7xx.c` recorded `-DHSE_VALUE=8000000` (twice: Makefile + `STM32H7.mk`), `-DSTM32H743xx`, `-DTARGET_FLASH_SIZE=2048`, `-DUSE_CONFIG`, `-D'__CONFIG_REVISION__="0096077"'`, `-D'__REVISION__="77d01ba"'`, LTO `-O2`, hard-float `fpv5-sp-d16`.

Evidence: `evidence/wp2b-a/analysis/system_stm32h7xx_compile.txt`.

## Clock / PLL / USB (software configuration)

| Topic | Finding | Level |
| ----- | ------- | ----- |
| HSE_VALUE | `8000000`; Halo config has **no** `SYSTEM_HSE_MHZ` | SOURCE_CONFIRMED |
| PLL source | `#define PLL_SRC RCC_PLLSOURCE_HSE` when `HSE_VALUE` defined (`system_stm32h7xx.c` L85–90) | SOURCE_CONFIRMED |
| HSE oscillator enable | `RCC_HSE_ON` (not bypass) in `SystemClockHSE_Config` | SOURCE_CONFIRMED |
| PLL1 Rev.V (480 MHz) | `m=4`, `n=960e6/PLL_SRC_FREQ*4`, `p=2` → 480 MHz sysclk for 8 MHz HSE | SOURCE_CONFIRMED |
| USB | `RCC_USBCLKSOURCE_HSI48` + CRS sync — **USB clock not from HSE** | SOURCE_CONFIRMED |
| Physical crystal | Not measured; no schematic | HARDWARE_REQUIRED |

## Flash / linker / vectors

Linker selected: `src/link/stm32_flash_h743_2m.ld` (`DEFAULT_LD_SCRIPT` in `mk/mcu/STM32H7.mk` L151).

| Region | Origin | Length |
| ------ | ------ | ------ |
| FLASH (vectors/startup) | `0x08000000` | 128 KiB |
| FLASH_CONFIG | `0x08020000` | 128 KiB |
| FLASH1 (application) | `0x08040000` | 1792 KiB |

ELF program headers (**BINARY_CONFIRMED**):

- `.isr_vector` @ `0x08000000` size `0x298`
- `.text` @ `0x08040000` size `0x73104`
- Entry `0x809f141`

Hex occupancy: vectors 664 B, config region 0 B in image, app ~500119 B.  
Linker report: FLASH 664 B / 128K; FLASH1 500119 B / 1792K.

This first 128 KiB is the **vector/startup region of the unified image**, not a proved independently replaceable Betaflight bootloader.

## Comparison with official assets

| Compare | Result |
| ------- | ------ |
| Local Halo hex vs GitHub generic `STM32H743` 4.5.1 hex | Different size and vector contents; **not** Halo-specific |
| Bit-identical match to factory/cloud Halo 4.5.1 | **Impossible here** — no Halo-named official binary retrieved; build timestamps / cloud `EXTRA_FLAGS` also differ |
| Local vs community `2026.6.2` Halo | Different BF major; stored only as community reference |

**BETAFLIGHT_BUILD_REPRODUCED = YES** (local official toolchain + pinned config).  
**Bit-identical to factory = NO / UNKNOWN** (factory image not obtained).

## Interrupt / startup notes

- Startup object `startup_stm32h743xx.s` linked; vectors in FLASH region.
- `VECT_TAB_OFFSET 0x00` in `system_stm32h7xx.c`.
- Config EEPROM uses `FLASH_CONFIG` symbols `__config_start` / `__config_end`.

## Residual build unknowns

1. Exact cloud-builder `EXTRA_FLAGS` / `BUILD_KEY` for OEM Dec-2024 online image.  
2. Whether factory boards ever received post-`0096077` config defaults without CLI.  
3. Option bytes / RDP on physical units.
