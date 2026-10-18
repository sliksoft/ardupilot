# WP2A_FINAL_REPORT — HDZero Halo hardware preflight

**Date:** 2026-10-18 (UTC)  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `1abdc924450f473670f63c91e60e737a5e534ec1`  
**Method:** documentation + public BF/HDZ/STM32 sources + local build artifacts  
**Policy:** no flash, no DFU erase, no GPIO power switching, no motor/ESC writes

**Review correction:** the original HSI inference and BF bootloader description
were incorrect. This report is corrected below; current implementation and
validation results are in `WP2A_REVIEW_FIX_REPORT.md`.

## Status block

```text
WP2A_STATUS = PARTIAL

HSE_FREQUENCY = UNKNOWN
HSE_EVIDENCE = normal BF 4.5.1 defaults HSE_VALUE=8000000 and passes it to the compiler; H7 selects HSE; physical source and installed image unverified; AP retains provisional HSE8

FLASH_LAYOUT = BF_SOURCE_LAYOUT_AP_NONOVERLAPPING
  BF H743 2M: vector/startup128K @ 0x08000000, CONFIG128K @ 0x08020000, code @ 0x08040000; no separate replaceable BF bootloader proved
  AP HDZeroHalo: BL 128K, APP @ 0x08020000 len 1664K, STORAGE_FLASH_PAGE 14 (build ldscript; not factory dual-boot)

BOOTLOADER_RECOVERY = SUPPORTED_PROCEDURE_UNTESTED
  HDZ halo-firmware.md BOOT-button STM32 DFU → reflash HDZERO_HALO; AP ENABLE_DFU_BOOT 1 in hwdef-bl.dat (not exercised)

TIM3_DMA_REVIEW = PASS_CODE
  TIM3 UP/CH1/CH3 → DMA1 Stream 0 shared; distinct DMAMUX TIM3_UP/CH1/CH3; intentional bdshot Shared_DMA (RCOutput_bdshot + Anyleaf twin); not TESTED on HW

IMU_VARIANTS = DUAL_SKU_DOCUMENTED_UNPROBED
  MPU6000 and/or ICM42688P per BF USE_GYRO_*; CS PB4/PB3 dual probe in hwdef; no USB WHO_AM_I this WP

IMU_ROTATION = UNKNOWN
  relative driver frames normalised: ICM NONE, MPU ROLL_180_YAW_90; absolute mounting unknown

PE3_POLARITY = ACTIVE_HIGH_INFERRED
  HDZ PINIO 1 E03 + pinio_config=1 → non-inverted; BF pinio idle LOW, USER1 on → HIGH; PCB FET not metered; hwdef holds LOW

VBAT_SCALE = NOMINAL_11.0_UNCALIBRATED
  BF voltage defaults imply factor11; physical calibration absent; BF current scale100 converts to AP100 A/V

HARDWARE_CONNECTED = NO
  lsusb empty / no /dev/ttyACM* /ttyUSB* /serial/by-id (WSL host, 2026-10-18)

READ_ONLY_TESTS = NONE_ON_DEVICE
  Evidence under project evidence/wp2a/readonly_probe.txt (local build greps + USB absence)

HARDWARE_FLASH_ALLOWED = NO

REMAINING_BLOCKERS =
  1. Clock source/image identity, exact MCU/flash/ROM recovery and matched installation artifacts
  2. Absolute IMU orientation on both SKUs and electrical PE3/reset verification
  3. Battery calibration, DShot/eRPM, RC/failsafe, OSD, logging and external-barometer hardware tests

NEXT_STEP =
  Connect Halo USB for read-only BF identity (MCU UID, gyro type via BF CLI) without flashing;
  obtain crystal/schematic or scope HSE; then human approval gate before any DFU/AP flash (WP2B+)
```

## Documents produced

| File | Topic |
| ------ | ------- |
| `WP2A_HSE.md` | Oscillator evidence matrix |
| `WP2A_FLASH_LAYOUT.md` | BF vs AP flash + DFU recovery |
| `WP2A_TIM3_DMA.md` | Shared DMA stream review |
| `WP2A_PE3_POLARITY.md` | 9V PINIO polarity |
| `WP2A_IMU_VBAT.md` | IMU SKUs + battery scales |
| `WP2A_FINAL_REPORT.md` | This status block |

## Proven vs assumption (summary)

| Item | Proven | Assumption / provisional |
| ------ | -------- | --------------------------- |
| Normal BF build selects HSE8 | yes (Makefile + compiler + PLL source) | Physical clock and installed image |
| BF linker regions 128+128+1792 | yes | Factory image; separate bootloader not proved |
| AP linker/param layout self-consistent | yes | Correct vs every OEM BL variant |
| TIM3 shared DMA intentional | yes (code) | Flight eRPM quality |
| PE3 PINIO active-HIGH | yes (BF+HDZ SW) | FET polarity identical |
| Dual IMU SKU support intent | yes (BF) | Probe order / rotation |
| Nominal VBAT11 and CURR100 A/V | yes (BF defaults and conversion) | Physical calibration |

## Safety compliance (this WP)

- No firmware flash or erase  
- No bootloader write  
- No ARM / motor / ESC config  
- No PE3 / power GPIO switching  
- No vehicle algorithm changes  
- No merge / upstream PR  

Local non-doc working tree (`AGENTS.md`, `CLAUDE.md`, `.claude/`) left untouched for commit scope.
