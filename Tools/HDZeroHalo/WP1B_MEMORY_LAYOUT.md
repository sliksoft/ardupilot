# WP1B_MEMORY_LAYOUT — provisional flash / parameter layout

Status: **NOT VERIFIED against factory Betaflight image — DO NOT FLASH**

## Chosen provisional layout (AP-native / Anyleaf-style)

| Item | Value | Notes |
| ------ | ------- | ------- |
| MCU flash | 2048 KB | H743 assumption |
| App `FLASH_RESERVE_START_KB` | 128 | First sector for BL |
| BL `FLASH_BOOTLOADER_LOAD_KB` | 128 | Matches app reserve |
| BL `FLASH_RESERVE_START_KB` | 0 | BL at 0x08000000 |
| `STORAGE_FLASH_PAGE` | 14 | Last pages for params |
| `HAL_STORAGE_SIZE` | 32768 | bytes |
| `FLASH_TOTAL` (configure) | 1703936 | app usable region |
| Board ID | 1414 (`AP_HW_HDZERO_HALO`) | **Provisional development ID** — not OEM reservation |

## Consistency checks (build artifacts)

| Check | Result |
| ------- | -------- |
| BL load KB == app reserve KB | PASS (128 = 128) |
| App flash used ≪ FLASH_TOTAL | PASS (~1.24 MB used, ~463 KB free) |
| BL size ≪ 128 KB sector | PASS (~18.9 KB) |
| Param page vs app overlap | Consistent with peer 128 KB + page 14 pattern |

Linker excerpts: `evidence/wp1b/ldscript_flash.txt`

## Alternative (not selected)

FPV-style `FLASH_RESERVE_START_KB 384` + `STORAGE_FLASH_PAGE 1` is a different
supported AP layout (Foxeer/TMotor/GEPRC). The BF first128KiB vector region is
not proof of a separate bootloader to retain. No reason was found to change
the nonoverlapping native AP layout merely to match BF regions.

## Oscillator

`STM32_HSECLK 8000000U` in generated `hwdef.h` — **provisional only**. Wrong HSE invalidates all timing. Measure before flash.
