# WP2B_G — restore standard ArduCopter startup without barometer

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `893e822ae414cd69ae61333772d0ab5a5e81a1d9`  
**HARDWARE_FLASH_ALLOWED = NO**

## Change

Halo `hwdef.dat` now includes the standard ArduPilot board option:

```text
define HAL_BARO_ALLOW_INIT_NO_BARO 1
```

External probing is unchanged:

```text
define AP_BARO_PROBE_EXTERNAL_I2C_BUSES 1
define HAL_BARO_PROBE_EXT_DEFAULT 1030
```

No shared `AP_Baro` / `AP_Arming` / Copter source edits. No extra arming blockade.

## Upstream behaviour retained

| Path | Effect when macro defined |
| ---- | ------------------------- |
| `AP_Baro` driver init | No fatal `config_error` if zero drivers/sensors |
| `AP_Baro` calibrate | Skips calibration with “no sensors found” GCS text |
| `AP_Arming::barometer_checks` | Returns `true` immediately (default baro prearm skipped) |

An attached BMP280/MS5611/BMP388 on I2C1 can still be probed later via the existing mask.

## Validation

| Step | Result |
| ---- | ------ |
| Halo hwdef generation (unittest) | PASS |
| `hdzero_halo_unittest.py` (11 tests) | PASS |
| Generated `hwdef.h` defines | `HAL_BARO_ALLOW_INIT_NO_BARO 1`, probe 1030 present |
| `./waf configure --board HDZeroHalo --Werror` + `./waf copter` | PASS (flash ≈ 1240544 B) |
| `Tools/scripts/build_bootloaders.py HDZeroHalo` | PASS (≈ 18920 B) |
| Shared AP_Baro / AP_Arming / Copter edits | None |

## Not claimed

- Flight safety without a barometer  
- Working altitude hold / baro-dependent modes  
- Hardware flash authorisation  

## Files

- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat`
- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/README.md`
- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/defaults.parm`
- `Tools/autotest/unittest/hdzero_halo_unittest.py`
- `Tools/bootloaders/HDZeroHalo_bl.{bin,elf,hex}` (rebuild)
- `Tools/HDZeroHalo/WP2B_G_NO_BARO_RESTORE.md`
- `Tools/HDZeroHalo/PORT_STATUS.md`, `README.md`

## Status

```text
WP2B_G_STATUS = PASS
NO_BARO_STARTUP = STANDARD_AP_OPTION
HAL_BARO_ALLOW_INIT_NO_BARO = 1
BAROMETER_PROBING = EXTERNAL_1030_RETAINED
ARDUCOPTER_BUILD = PASS
BOOTLOADER_BUILD = PASS
REGRESSION_TESTS = PASS
FILES_CHANGED = hwdef.dat,README.md,defaults.parm,hdzero_halo_unittest.py,WP2B_G_NO_BARO_RESTORE.md,PORT_STATUS.md,Tools/HDZeroHalo/README.md,HDZeroHalo_bl.*
COMMIT_SHA = dc90586623508f553a1b54834a79e2dd3798978a
PUSH_STATUS = PUSHED_origin_board_hdzero-halo
HARDWARE_FLASH_ALLOWED = NO
```
