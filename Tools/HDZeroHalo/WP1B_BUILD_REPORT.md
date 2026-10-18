# WP1B_BUILD_REPORT — HDZeroHalo offline builds

**Date:** 2026-10-18  
**Base (pre-WP1B):** `ea49cd912e67da1df72f7858a0d1f8543c855205`  
**HARDWARE_FLASH_ALLOWED = NO**  
**OSCILLATOR_STATUS = UNKNOWN** (provisional 8 MHz — **NOT VERIFIED — DO NOT FLASH**)

## Toolchain

| Item | Value |
|------|-------|
| GCC | arm-none-eabi-gcc 13.2.1 (Ubuntu) |
| Python | `.venv` (empy 3.3.4) |
| Host | WSL2 Ubuntu 24.04 |

## Configure

```sh
source .venv/bin/activate
./waf configure --board HDZeroHalo
```

Result: **SUCCESS** (after bootloader binary present).  
Logs: `evidence/wp1b/configure_HDZeroHalo.log`, `configure_HDZeroHalo_postreview.log`

## Bootloader

```sh
Tools/scripts/build_bootloaders.py HDZeroHalo
```

| Metric | Value |
|--------|-------|
| Result | SUCCESS |
| Text / flash used | 18828 / 18920 B |
| Free (BL region) | 112148 B |
| Outputs | `Tools/bootloaders/HDZeroHalo_bl.{bin,elf,hex}` |
| SHA256 `.bin` | `c14a6f119fc936b2cf7c06327017f78b8155f2f3b7befcbdd5d53171670d066a` |
| Warnings/errors | 0 |

Log: `evidence/wp1b/build_bootloader_HDZeroHalo.log`

## ArduCopter (post-review)

```sh
./waf copter
```

| Metric | Value |
|--------|-------|
| Result | SUCCESS |
| Text / Data / flash used | 1237076 / 3348 / 1240424 B |
| Free flash | 463448 B |
| Outputs | `build/HDZeroHalo/bin/arducopter{.apj,.bin,_with_bl.hex}` |
| SHA256 `.apj` | see `evidence/wp1b/SHA256SUMS.txt` |
| Warnings/errors | 0 |

Log: `evidence/wp1b/build_HDZeroHalo_copter_postreview.log`

## Generated defines (sample)

- `APJ_BOARD_ID 1414`
- `HAL_WITH_BIDIR_DSHOT`
- `DEFAULT_BUZZ_ON_LVL 0`
- Four IMU probes: `icm42688_1/2`, `mpu6000_1/2`
- `DEFAULT_SERIAL1_PROTOCOL` RCIN; `DEFAULT_SERIAL5_PROTOCOL` MSP DisplayPort
- `HAL_LOGGING_DATAFLASH_ENABLED 1`
- `MOT_PWM_TYPE 5` (defaults.parm)

## Files changed (source)

- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/*`
- `Tools/AP_Bootloader/board_types.txt` (`AP_HW_HDZERO_HALO` 1414 provisional)
- `Tools/bootloaders/HDZeroHalo_bl.*`
- `Tools/HDZeroHalo/WP1B_*.md`, `PORT_STATUS.md`, `README.md`
