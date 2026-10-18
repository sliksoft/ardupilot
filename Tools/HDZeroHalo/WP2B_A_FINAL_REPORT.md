# WP2B_A_FINAL_REPORT — Betaflight Halo forensic analysis

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Start HEAD:** `eef7aa1c0be92665828586fe0ae13113067f3de0`  
**Method:** OEM docs/CLI download, BF 4.5.1 + config `0096077` source build, ELF/hex/linker analysis, AP hwdef comparison  
**Policy:** documentation only — no ArduPilot hwdef edits, no flash, no DFU, no motor/GPIO power tests

Evidence: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-a/`  
Detail reports: `WP2B_A_*.md` in this directory.

## Main conclusion

**From original Betaflight sources, OEM docs/CLI, and a reproducible 4.5.1 Halo build we can definitively reconstruct the software pinmap, HSE8 compile/PLL selection, flash VMA map, dual-SKU IMU probe layout, ADC defaults, DShot bitbang/TIM3 motor map, and PE3 PINIO active-HIGH semantics.**

**We still cannot claim a measured 8 MHz crystal, absolute IMU mounting, PE3/9V electrical truth across reset, factory image bytes, option bytes/ROM version, or that ArduPilot’s TIM3-DMA bdshot path matches Betaflight’s bitbang path on hardware.**

## Status block

```text
WP2B_A_STATUS = PARTIAL

BETAFLIGHT_RELEASE = 4.5.1 (77d01ba3b76a22909d5f09cb0628820141f95eaa)
BETAFLIGHT_TARGET_SHA = 009607753079525bbdec1395a1773b79127990ab (OEM CLI config rev); later d3abecf/e0273b95 add MSP DP + ibata default 100
OFFICIAL_FIRMWARE_FOUND = NO (Halo-named 4.5.1 hex not downloadable; generic STM32H743 release hex only)
OFFICIAL_CLI_FOUND = YES (HDZEROHALO_Rev20250205 / HDZERO_HALO.txt)
BETAFLIGHT_BUILD_REPRODUCED = YES (GCC 10.3.1 SDK; not bit-identical to factory)

HSE_CLOCK = SOFTWARE_HSE8_CONFIRMED
PHYSICAL_HSE_PROOF = NO
MCU_IDENTIFICATION = STM32H743_CLASS_SOURCE_OEM; PACKAGE_MARKING_UNKNOWN
IMU_MPU6000 = DRIVER_AND_SKU_DOCUMENTED
IMU_ICM42688 = DRIVER_AND_SKU_DOCUMENTED
IMU_ROTATION = RELATIVE_RAW_FRAME_NORMALISED; ABSOLUTE_MOUNT_UNKNOWN
PE3_9V = ACTIVE_HIGH_SOFTWARE_INFERRED; ELECTRICAL_UNVERIFIED
VBAT_SCALE = NOMINAL_BF_110_10_1 -> AP_11.0_UNCALIBRATED
CURRENT_SCALE = BF_100_OEM_CLI -> AP_100_A_PER_V_UNCALIBRATED
TIM3_DSHOT = PINS_TIMER_SOURCE_CONFIRMED
BIDIR_DSHOT = BF_DEFAULT_OFF; AP_DMA_PATH_UNVERIFIED
FLASH_LAYOUT = BF_128_128_1792_SOURCE_BINARY; AP_128_BL_APP_0x08020000_DIFFERENT
DFU_RECOVERY = OEM_BOOT_BUTTON_PROCEDURE_DOCUMENTED_UNTESTED

NEW_HARDWARE_INFORMATION =
  OEM CLI pins BF 4.5.1+0096077; ibata_scale 100; LED2 C14; no PINIO in CLI zip
  Manufacturer config PR d3abecf baked MSP DisplayPort UART5 + current scale 100
  BF H7 USB clock is HSI48+CRS (not HSE) — USB less diagnostic for crystal than UART/DShot
  Closed PR835 CS split ICM=PB4 / MPU=PB3 reinforced; still unmerged
  ESC manual: DSHOT up to 2400; AM32/BLHeli32; ESC current scale 170 (not FC ADC)
  Local Halo ELF/hex/map produced with official BF toolchain

ARDUPILOT_DIFFERENCES =
  App VMA 0x08020000 vs BF 0x08040000; params pages 14/15 vs BF config @ 0x08020000
  DShot: AP TIM3 DMA/bdshot vs BF bitbang default ON
  Default DShot rate: AP defaults.parm DShot300 vs BF DShot600 default
  USB clock tree: AP HSE-derived 48M vs BF HSI48
  PE3 held LOW in hwdef; BF requires PINIO resource CLI for 9V control
  Addressable LED unsupported in AP NODMA map vs BF LED strip feature

SOFTWARE_QUESTIONS_RESOLVED =
  Normal Halo BF build HSE_VALUE=8000000 and PLL from HSE
  Flash linker regions and local ELF placement
  Dual IMU driver/CS/EXTI map; WHO_AM_I constants; CW0 default align
  PE3 PINIO software polarity; VBAT/current nominal formulas
  Motor TIM3 map; bitbang default; bidir default off
  OEM recovery procedure text; no dual-boot with AP layout

HARDWARE_QUESTIONS_REMAINING = (see table below)

HARDWARE_FLASH_ALLOWED = NO

HEAD_SHA = (set at commit)
PUSH_STATUS = (set at push)
NEXT_ACTION =
  Read-only USB identity on physical Halo (MCU UID, BF version, gyro WHO_AM_I, RCC if available);
  photograph crystal/IMU; scope or OEM crystal confirmation before any flash approval
```

## Remaining hardware questions (complete list)

| # | Question | Why firmware cannot close it |
| - | -------- | ---------------------------- |
| 1 | Physical HSE frequency / part | Compile flag ≠ crystal measurement; no schematic |
| 2 | Exact MCU package, flash size, silicon rev, ROM version | Need marking / registers / AN2606 identity |
| 3 | Option bytes, RDP, write protection | Not in application hex |
| 4 | Factory image SHA / cloud EXTRA_FLAGS | Halo-named 4.5.1 binary not obtained |
| 5 | Absolute IMU orientation both SKUs | BF CW0 + AP relative fix ≠ PCB mounting |
| 6 | Live CS population (PB4 vs PB3) | Needs WHO_AM_I on hardware |
| 7 | PE3 vs 9V rail across reset/DFU/bootloader | GPIO init docs ≠ electrical truth table |
| 8 | VBAT divider resistors / calibration | Defaults only |
| 9 | FC current shunt gain/offset | Scale 100 nominal; ESC 170 is different sensor |
| 10 | AP TIM3 DMA / bdshot eRPM quality | BF bitbang success irrelevant |
| 11 | DShot300/600/2400 with installed ESC firmware | Needs bench |
| 12 | ELRS Gemini bind/telemetry/failsafe on UART1 | Wiring known; RF behaviour not |
| 13 | MSP DisplayPort canvas with HDZero VTX | Config known; link not tested |
| 14 | W25Q128 logging endurance/throughput | Driver enabled; not tested |
| 15 | Buzzer PD12 / LED PE2 / LED2 C14 electrical | Levels inferred |
| 16 | External GPS/mag/baro on pads | Probe defaults only |
| 17 | BOOT button / DFU round-trip | Procedure only |
| 18 | Post-AP recovery to BF on this unit | Needs controlled DFU later |

## Other features (BF vs AP) — brief

| Feature | Betaflight Halo | ArduPilot HDZeroHalo |
| ------- | --------------- | -------------------- |
| ELRS / CRSF | UART1 SerialRX; onboard Gemini ESP32+2×SX1280 (OEM) | SERIAL1 RCIN |
| MSP DisplayPort | UART5 (CLI serial 4 / later config default) | SERIAL5 MSP DP, OSD_TYPE 5 |
| SPI flash | W25Q128FV SPI2 | dataflash SPI2 |
| Buzzer | PD12 inverted | PD12 active HIGH level, idle LOW |
| Status LED | PE2; OEM CLI also LED2 C14 | PE2 LED0 |
| LED strip | PA10 TIM1 | PA10 NODMA unsupported addressable |
| I²C | PB8/PB9 pads | External baro/compass probe |
| USB | Type-C; BF HSI48 | OTG1; HSE-PLL USB clock tree |
| GPS/mag/baro | External | External required (baro); no onboard baro |

## Independent review

See `WP2B_A_INDEPENDENT_REVIEW.md` (filled after read-only gate).

## Documents produced

| File | Topic |
| ---- | ----- |
| `WP2B_A_BETAFLIGHT_SOURCES.md` | Provenance, hashes, OEM vs official vs local |
| `WP2B_A_FIRMWARE_BUILD.md` | Repro build, flags, ELF/hex |
| `WP2B_A_CLOCK_ANALYSIS.md` | HSE questions |
| `WP2B_A_IMU_ANALYSIS.md` | Gyro SKUs / rotation |
| `WP2B_A_POWER_ADC.md` | PE3 + ADC scales |
| `WP2B_A_DSHOT_COMPARISON.md` | TIM3 / bitbang vs AP DMA |
| `WP2B_A_BOOTLOADER_RECOVERY.md` | Flash map / DFU plan |
| `WP2B_A_FINAL_REPORT.md` | This status block |

## Safety compliance

- No firmware flash or erase  
- No ArduPilot hwdef / driver changes  
- No motor, ESC, or PE3 switching  
- Local `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.serena/` left unstaged
