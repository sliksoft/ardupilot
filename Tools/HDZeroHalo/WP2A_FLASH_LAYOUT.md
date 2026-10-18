# WP2A_FLASH_LAYOUT — STM32H743 flash, AP BL, params, DFU

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Verdict

| Field | Value |
| ------- | ------- |
| Standard BF source layout | **PROVEN** (H743 2M linker); factory image unverified |
| AP provisional layout | **Internally consistent** (build artifacts); **not** equal to BF app VMA |
| DFU recovery | Vendor-supported procedure; exact board/ROM version unverified |
| Flash AP without approval | **FORBIDDEN** this WP |

## Betaflight H743 2 MB layout (PROVEN)

From `betaflight/.../link/stm32_flash_h743_2m.ld`:

| Region | Origin | Length | Role |
| -------- | -------- | -------- | ------ |
| `FLASH` | `0x08000000` | 128 KB | Interrupt vectors / startup region |
| `FLASH_CONFIG` | `0x08020000` | 128 KB | BF config sector |
| `FLASH1` | `0x08040000` | 1792 KB | BF application |

The H743 normal build selects this linker. It places `.isr_vector` in `FLASH`
and `.text` in `FLASH1`; this does not prove a separate, independently replaceable
128 KB BF bootloader. This source layout is not an inspected factory image.

## ArduPilot HDZeroHalo provisional layout (build-proven, factory-unverified)

From `hwdef.dat` / `hwdef-bl.dat` / `build/HDZeroHalo/ldscript.ld`:

| Item | Value |
| ------ | ------- |
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
| ------- | --------- |
| BF app vs AP app start | BF app @ `0x08040000`; AP app @ `0x08020000` |
| Implication | Full AP installation replaces BF vectors, configuration and code; no dual-boot or preserved independent BF bootloader established |
| FPV `FLASH_RESERVE_START_KB 384` | Different supported AP layout; not required merely because BF uses different linker regions |
| Params | Page 14 is consistent with 128 KB reserve on 128 KB H743 pages; **not** verified against a flashed board |

## Bootloader recovery (PROVEN procedure, not executed)

HDZero `halo-firmware.md` DFU path (read-only citation):

1. Power off Halo  
2. BF Configurator: enable “No reboot sequence”, “Full chip erase”  
3. Hold **BOOT**, power via USB-C, release BOOT  
4. Flash target `HDZERO_HALO` (factory note: 4.5.1)

AP `hwdef-bl.dat` sets `ENABLE_DFU_BOOT 1` so an installed AP bootloader can re-enter STM32 ROM DFU — peer pattern; **not tested** on Halo.

The application does not enable `HAL_ENABLE_DFU_BOOT`. Do not advertise an
application-initiated ROM-DFU request as enabled. Physical FC BOOT recovery is
independent of that application option.

ST AN2606 Rev70 section60/table136 documents ROM-version-specific limitations,
including DFU mass erase on V13.3 and bank-erase timing issues on V9.1. Record
actual MCU/ROM identity and confirm BOOT/USB enumeration before destructive
work; preserve a matching BF image, configuration and option-byte information.
No recovery round-trip is proved here.

## AP sector and erase boundaries

H743 global pages are 128 KiB. Bootloader page0 is `0x08000000-0x0801FFFF`.
Application pages1-13 end at `0x081BFFFF`. Parameter pages14/15 occupy
`0x081C0000-0x081FFFFF`. The hwdef generator truncates the application before
storage (`chibios_hwdef.py:1407-1417`) and reserves the final256 KiB for the
bootloader's application erase boundary (`:1183-1191`). `Storage.cpp:415-449`
erases selected storage pages and permits erase only while disarmed. No overlap
was found. Exact physical flash capacity/bank configuration remains unverified.

**This WP did not enter DFU, erase, or flash.**

## Sources

- `https://github.com/betaflight/betaflight/blob/master/src/platform/STM32/link/stm32_flash_h743_2m.ld`
- `https://github.com/hd-zero/hdzero-docs/blob/main/docs/halo-firmware.md`
- `https://www.st.com/resource/en/application_note/an2606-stm32-microcontroller-system-memory-boot-mode-stmicroelectronics.pdf`
- Local: `Tools/HDZeroHalo/WP1B_MEMORY_LAYOUT.md`, `hwdef/HDZeroHalo/hwdef*.dat`, `build/HDZeroHalo/ldscript.ld`
