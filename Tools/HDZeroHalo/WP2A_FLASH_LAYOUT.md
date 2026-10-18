# WP2A_FLASH_LAYOUT — STM32H743 flash, AP BL, params, DFU

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Verdict

| Field | Value |
|-------|-------|
| Factory BF layout | **PROVEN** (BF H743 2M linker) |
| AP provisional layout | **Internally consistent** (build artifacts); **not** equal to BF app VMA |
| Safe DFU recovery | **SUPPORTED** (vendor BOOT-button procedure) |
| Flash AP without approval | **FORBIDDEN** this WP |

## Betaflight H743 2 MB layout (PROVEN)

From `betaflight/.../link/stm32_flash_h743_2m.ld`:

| Region | Origin | Length | Role |
|--------|--------|--------|------|
| `FLASH` | `0x08000000` | 128 KB | ISR / BF bootloader |
| `FLASH_CONFIG` | `0x08020000` | 128 KB | BF config sector |
| `FLASH1` | `0x08040000` | 1792 KB | BF application |

Comments in that linker script state the same map explicitly.

## ArduPilot HDZeroHalo provisional layout (build-proven, factory-unverified)

From `hwdef.dat` / `hwdef-bl.dat` / `build/HDZeroHalo/ldscript.ld`:

| Item | Value |
|------|-------|
| MCU flash | 2048 KB |
| App `FLASH_RESERVE_START_KB` | 128 |
| BL load | 128 KB (`FLASH_BOOTLOADER_LOAD_KB`) |
| App flash org | `0x08020000`, len **1664K** |
| `STORAGE_FLASH_PAGE` | 14 |
| `HAL_STORAGE_SIZE` | 32768 |
| Board ID | 1414 (`AP_HW_HDZERO_HALO`) provisional |

BL binary size (~19 KB) fits in the first 128 KB sector (`evidence/wp1b/`, WP1B reports).

## Comparison / risk

| Topic | Finding |
|-------|---------|
| BF app vs AP app start | BF app @ `0x08040000`; AP app @ `0x08020000` |
| Implication | Full AP install **replaces** BF BL+config+app map; do not expect dual-boot with stock BF BL |
| FPV `FLASH_RESERVE_START_KB 384` | Still an alternative if a future OEM BL occupies more than 128 KB; **not selected**; not proven necessary once AP BL is installed |
| Params | Page 14 is consistent with 128 KB reserve on 128 KB H743 pages; **not** verified against a flashed board |

## Bootloader recovery (PROVEN procedure, not executed)

HDZero `halo-firmware.md` DFU path (read-only citation):

1. Power off Halo  
2. BF Configurator: enable “No reboot sequence”, “Full chip erase”  
3. Hold **BOOT**, power via USB-C, release BOOT  
4. Flash target `HDZERO_HALO` (factory note: 4.5.1)

AP `hwdef-bl.dat` sets `ENABLE_DFU_BOOT 1` so an installed AP bootloader can re-enter STM32 ROM DFU — peer pattern; **not tested** on Halo.

**This WP did not enter DFU, erase, or flash.**

## Sources

- `https://github.com/betaflight/betaflight/blob/master/src/platform/STM32/link/stm32_flash_h743_2m.ld`
- `https://github.com/hd-zero/hdzero-docs/blob/main/docs/halo-firmware.md`
- Local: `Tools/HDZeroHalo/WP1B_MEMORY_LAYOUT.md`, `hwdef/HDZeroHalo/hwdef*.dat`, `build/HDZeroHalo/ldscript.ld`
