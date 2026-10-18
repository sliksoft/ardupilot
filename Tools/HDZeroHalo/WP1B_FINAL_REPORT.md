# WP1B_FINAL_REPORT — first HDZeroHalo ArduCopter build

**Date:** 2026-10-18  
**Parent HEAD:** `ea49cd912e67da1df72f7858a0d1f8543c855205`  
**WP1B HEAD:** `a8ecfa2edb085bcdeaf82939b65669445f01bcaf`

```text
WP1B_STATUS = PARTIAL

HALO_BOARD_CONFIGURE = PASS (./waf configure --board HDZeroHalo)
ARDUCOPTER_BUILD = PASS (./waf copter; 0 warn/err; ~1240 KB flash used)
BOOTLOADER_BUILD = PASS (build_bootloaders.py; ~19 KB)
DSHOT300_CONFIG = PASS (MOT_PWM_TYPE 5 default; TIM3 DMA path)
DSHOT600_CONFIG = PASS (same path; set MOT_PWM_TYPE 6 for bench)
BIDIR_DSHOT_DMA = PASS configure (HAL_WITH_BIDIR_DSHOT; TIM3 UP/CH1/CH3 share DMA1.0; not TESTED)
IMU_VARIANTS = PASS compile (ICM+MPU probe on PB4 and PB3 CS)
FLASH_LOGGER = PASS compile (W25Q128 SPI2 PB12; JEDEC)
ELRS = PASS compile (USART1 RCIN)
HDZERO_OSD = PASS compile (UART5 MSP DisplayPort; OSD_TYPE 5)
MEMORY_LAYOUT = PASS internal consistency (128 KB BL load = reserve; page 14); NOT verified vs BF
OSCILLATOR_STATUS = UNKNOWN
HARDWARE_FLASH_ALLOWED = NO

REMAINING_BLOCKERS = HSE Hz; BL layout vs factory BF; VBAT scale; IMU rotation; PE3 polarity proof
```

## What was added

- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/` (`hwdef.dat`, `hwdef-bl.dat`, `defaults.parm`, `README.md`)
- Provisional `AP_HW_HDZERO_HALO` **1414** in `board_types.txt`
- Bootloader binaries under `Tools/bootloaders/HDZeroHalo_bl.*`
- WP1B evidence docs under `Tools/HDZeroHalo/WP1B_*.md`
- Build logs under `evidence/wp1b/` (outside Git)

## Provisional assumptions (**NOT VERIFIED — DO NOT FLASH**)

1. `OSCILLATOR_HZ 8000000`  
2. `FLASH_RESERVE_START_KB 128` / storage page 14  
3. `HAL_BATT_VOLT_SCALE 11.0`  
4. `ROTATION_NONE` for IMUs  
5. PE3 held LOW = safe off (polarity unproven)  
6. USB on PA11/PA12 (peer convention; absent from BF config.h)

## Independent review

See `WP1B_INDEPENDENT_REVIEW.md`. Buzzer on-level and SERIAL_ORDER labels fixed; rebuild green.

## WP2 readiness

**Yes for planning hardware bring-up** (DFU recovery, HSE measure, IMU detect, DShot bench).  
**No automatic hardware tests.** Do not flash until CRITICAL blockers close.
