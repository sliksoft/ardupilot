# WP2B_A_BOOTLOADER_RECOVERY — flash layout, DFU, return to Betaflight

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## STM32H743 boot process (reference)

| Stage | Behaviour |
| ----- | --------- |
| Hardware BOOT pin | Low → boot from main flash; High → system memory (ROM bootloader) |
| ROM DFU | USB DFU in system memory (AN2606 H7 family; ROM version caveats apply) |
| Option bytes / RDP | Not readable without the physical MCU |

OEM Halo DFU procedure (docs): power off → Configurator “No reboot sequence” + “Full chip erase” → hold **BOOT**, power USB-C, release BOOT → flash `HDZERO_HALO`.

**Level:** OEM_CONFIRMED procedure text; **not exercised** this WP.

## Betaflight flash map (SOURCE + BINARY)

From `stm32_flash_h743_2m.ld` and reproduced ELF:

| Region | Address | Size | Contents |
| ------ | ------- | ---- | -------- |
| Vectors / startup | `0x08000000` | 128 KiB | `.isr_vector` (~0x298 used) |
| Config | `0x08020000` | 128 KiB | EEPROM/config (`FLASH_CONFIG`); empty in hex image |
| Application | `0x08040000` | 1792 KiB | `.text` and loadable segments |

Do **not** call the first 128 KiB a separately replaceable “Betaflight bootloader” without OEM proof. It is the unified image’s vector region.

## ArduPilot HDZeroHalo map (build-proved, factory-unverified)

| Item | Value |
| ---- | ----- |
| BL reserve | 128 KiB @ `0x08000000` |
| Application | `0x08020000`, length 1664 KiB |
| Parameters | `STORAGE_FLASH_PAGE` 14 (and 15) → `0x081C0000+` |
| Board ID | 1414 provisional |

## Overlap implications

| Action | Effect |
| ------ | ------ |
| Flash full AP image | Overwrites BF vectors **and** BF config sector **and** occupies BF’s former config VMA with AP code |
| Dual-boot BF+AP | **Not** supported by these layouts |
| Return to BF | Requires ROM DFU (or equivalent) + reflash Halo BF image + re-apply CLI/PINIO as needed |

## Preparing a reliable return to Betaflight (plan only)

1. **Before any AP flash:** save MSP `diff all` / `dump` from the live board; archive gyro SKU, `ibata_scale`, PINIO, serial, VTX table.  
2. Keep OEM CLI zip + User Manual DFU steps.  
3. Prefer obtaining a **Halo-named** BF hex (Configurator online build) and store SHA256; generic `STM32H743.hex` is not a Halo target image.  
4. Local reproduction (`evidence/wp2b-a/firmware/reproduced/`) can serve as a recovery candidate **after** human validation — still not bit-identical to factory.  
5. Use BOOT-button ROM DFU with full chip erase when recovering a non-responsive board (OEM steps).  
6. After BF restore: re-apply PINIO PE3 if required; confirm ELRS / MSP DP.  
7. Record MCU UID, flash size, option bytes, ROM version from the physical unit when first connected (**HARDWARE_REQUIRED**).

## What only the physical unit can prove

| Item | Why firmware is insufficient |
| ---- | ---------------------------- |
| Exact flash size / dual-bank option | Package marking / `FLASH_SIZE` register |
| ROM bootloader version | AN2606 errata depends on it |
| RDP / write protection | Option bytes |
| BOOT button wiring | Schematic / continuity |
| Factory image bytes | Need dump or matched cloud artifact |
| Post-erase first-boot behaviour | Electrical |

## AP bootloader DFU note

`hwdef-bl.dat` sets `ENABLE_DFU_BOOT 1` (bootloader can request ROM DFU). Application does **not** enable `HAL_ENABLE_DFU_BOOT`. Physical BOOT remains the OEM recovery path.

## Verdict

```text
FLASH_LAYOUT = BF_SOURCE_AND_LOCAL_BINARY_CONFIRMED; FACTORY_IMAGE_UNVERIFIED
DFU_RECOVERY = OEM_PROCEDURE_DOCUMENTED_UNTESTED
RETURN_TO_BETAFLIGHT = PLANNABLE_VIA_ROM_DFU; NO_DUAL_BOOT
```
