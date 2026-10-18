# WP2A_FINAL_REPORT — HDZero Halo hardware preflight

**Date:** 2026-10-18 (UTC)  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `1abdc924450f473670f63c91e60e737a5e534ec1`  
**Method:** documentation + public BF/HDZ/STM32 sources + local build artifacts  
**Policy:** no flash, no DFU erase, no GPIO power switching, no motor/ESC writes

## Status block

```text
WP2A_STATUS = PARTIAL

HSE_FREQUENCY = UNKNOWN
HSE_EVIDENCE = BF HDZERO_HALO omits SYSTEM_HSE_MHZ → H7 PLL from HSI 64 MHz (system_stm32h7xx.c); no schematic/scope; AP OSCILLATOR_HZ 8 MHz remains provisional peer convention only; dogjutsu 8 MHz rejected as proof

FLASH_LAYOUT = BF_PROVEN_AP_PROVISIONAL
  BF H743 2M: BL 128K @ 0x08000000, CONFIG 128K @ 0x08020000, APP @ 0x08040000 (stm32_flash_h743_2m.ld)
  AP HDZeroHalo: BL 128K, APP @ 0x08020000 len 1664K, STORAGE_FLASH_PAGE 14 (build ldscript; not factory dual-boot)

BOOTLOADER_RECOVERY = SUPPORTED_PROCEDURE_UNTESTED
  HDZ halo-firmware.md BOOT-button STM32 DFU → reflash HDZERO_HALO; AP ENABLE_DFU_BOOT 1 in hwdef-bl.dat (not exercised)

TIM3_DMA_REVIEW = PASS_CODE
  TIM3 UP/CH1/CH3 → DMA1 Stream 0 shared; distinct DMAMUX TIM3_UP/CH1/CH3; intentional bdshot Shared_DMA (RCOutput_bdshot + Anyleaf twin); not TESTED on HW

IMU_VARIANTS = DUAL_SKU_DOCUMENTED_UNPROBED
  MPU6000 and/or ICM42688P per BF USE_GYRO_*; CS PB4/PB3 dual probe in hwdef; no USB WHO_AM_I this WP

IMU_ROTATION = UNKNOWN
  ROTATION_NONE provisional in hwdef

PE3_POLARITY = ACTIVE_HIGH_INFERRED
  HDZ PINIO 1 E03 + pinio_config=1 → non-inverted; BF pinio idle LOW, USER1 on → HIGH; PCB FET not metered; hwdef holds LOW

VBAT_SCALE = PROVISIONAL_11.0
  BF CURRENT scale 100 proven for FC ADC; VBAT divider UNKNOWN; ESC scale 170 is ESC-side not FC

HARDWARE_CONNECTED = NO
  lsusb empty / no /dev/ttyACM* /ttyUSB* /serial/by-id (WSL host, 2026-10-18)

READ_ONLY_TESTS = NONE_ON_DEVICE
  Evidence under project evidence/wp2a/readonly_probe.txt (local build greps + USB absence)

HARDWARE_FLASH_ALLOWED = NO

REMAINING_BLOCKERS =
  1. HARD: measure or OEM-document MCU HSE (or confirm HSI-only PCB for AP clock policy)
  2. HARD: approve flash strategy (AP BL@128K vs keep/recover BF); first flash only after HSE decision
  3. SOFT: VBAT divider calibration; IMU rotation on both SKUs; PE3 electrical confirm

NEXT_STEP =
  Connect Halo USB for read-only BF identity (MCU UID, gyro type via BF CLI) without flashing;
  obtain crystal/schematic or scope HSE; then human approval gate before any DFU/AP flash (WP2B+)
```

## Documents produced

| File | Topic |
|------|-------|
| `WP2A_HSE.md` | Oscillator evidence matrix |
| `WP2A_FLASH_LAYOUT.md` | BF vs AP flash + DFU recovery |
| `WP2A_TIM3_DMA.md` | Shared DMA stream review |
| `WP2A_PE3_POLARITY.md` | 9V PINIO polarity |
| `WP2A_IMU_VBAT.md` | IMU SKUs + battery scales |
| `WP2A_FINAL_REPORT.md` | This status block |

## Proven vs assumption (summary)

| Item | Proven | Assumption / provisional |
|------|--------|---------------------------|
| BF uses HSI PLL when HSE_VALUE unset | yes | Physical crystal Hz |
| BF flash map 128+128+1792 | yes | — |
| AP linker/param layout self-consistent | yes | Correct vs every OEM BL variant |
| TIM3 shared DMA intentional | yes (code) | Flight eRPM quality |
| PE3 PINIO active-HIGH | yes (BF+HDZ SW) | FET polarity identical |
| Dual IMU SKU support intent | yes (BF) | Probe order / rotation |
| CURR scale 100 | yes (BF) | VBAT 11.0 |

## Safety compliance (this WP)

- No firmware flash or erase  
- No bootloader write  
- No ARM / motor / ESC config  
- No PE3 / power GPIO switching  
- No vehicle algorithm changes  
- No merge / upstream PR  

Local non-doc working tree (`AGENTS.md`, `CLAUDE.md`, `.claude/`) left untouched for commit scope.
