# WP2B_D_IMU_ROTATION_FIX — apply FRD IMU rotations

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `cd0b4503591a7df1d7d7724cdfec5e89348da37d`  
**HARDWARE_FLASH_ALLOWED = NO**

## Why

WP2B-C six-face MSP Acc on the live ICM42688P matched Betaflight body
**X-forward / Y-left / Z-up**. ArduPilot FRD is **X-forward / Y-right / Z-down**.
Map: `ROTATION_ROLL_180` = `(x,y,z)→(x,-y,-z)` (`AP_Math/vector3.cpp`).

## Source proofs

| Item | Evidence |
| ---- | -------- |
| BF MSP Acc after CW0 | `acceleration.c` align + `msp.c` `MSP_RAW_IMU` |
| ICM v3 no axis remap | `AP_InertialSensor_Invensensev3` FIFO `accel[0..2]` |
| ROLL_180 | `vector3.cpp`; `test_math.cpp` `(1,1,1)→(1,-1,-1)` |
| MPU driver `(y,x,-z)` | `Invensense.cpp` `_accumulate` |
| MPU compose | `YAW_270(A_MPU(r)) == ROLL_180(r)` (algebra + unittest) |

## Applied hwdef change

`libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat`:

| Probe | Before | After |
| ----- | ------ | ----- |
| `icm42688_1` / `_2` | `ROTATION_NONE` | **`ROTATION_ROLL_180`** |
| `mpu6000_1` / `_2` | `ROTATION_ROLL_180_YAW_90` | **`ROTATION_YAW_270`** |

Generated `hwdef.h` probes match. Motor / DMA / UART / SPI / baro lines unchanged.

## Not proved on hardware

- Gyro rate polarity (Acc-only six-face)
- MPU6000 SKU physical mounting (composition assumes same register→board map as ICM)
- First AP AHRS / level check after flash
- HSE, DFU, PE3/9V, ADC, DShot on hardware

## Tests / builds

| Check | Result |
| ----- | ------ |
| `hdzero_halo_unittest` (incl. six-face, compose, probes, peripherals) | PASS |
| `test_math` `VectorTest.Rotations` (SITL) | PASS |
| `./waf configure --board HDZeroHalo --Werror` | PASS |
| `./waf copter` | PASS (flash 1240780 B, free 463096 B) |
| `build_bootloaders.py HDZeroHalo` | PASS (BL 18920 B) |

## Impact note

GitNexus upstream impact on Invensensev3 class: **LOW** (2 direct). Hwdef file
itself is not a graph symbol (UNKNOWN if targeted as path). Index was stale
during analysis; conclusions confirmed by generated `hwdef.h` and builds.

## Verdict (software)

```text
ICM42688_ROTATION = ROTATION_ROLL_180
MPU6000_ROTATION = ROTATION_YAW_270 (UNTESTED_SKU)
HARDWARE_FLASH_ALLOWED = NO
```
