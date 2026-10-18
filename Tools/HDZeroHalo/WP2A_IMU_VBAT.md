# WP2A_IMU_VBAT — dual-SKU IMU probe and battery calibration

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
**On-hardware probe:** not possible (no USB Halo)

## IMU variants

| Field | Value |
|-------|-------|
| `IMU_VARIANTS` | **Two SKUs (docs/BF)** — MPU6000 **or** ICM42688P, one fitted |
| Probe strategy in hwdef | Both drivers × both CS (PB4, PB3) |
| Hardware detect this WP | **NOT RUN** |
| `IMU_ROTATION` | **UNKNOWN** (`ROTATION_NONE` provisional) |

### Evidence

| Source | Content | Class |
|--------|---------|-------|
| BF `HDZERO_HALO` config | `USE_GYRO_SPI_MPU6000` + `USE_GYRO_SPI_ICM42688P`; `GYRO_1_CS PB4` / EXTI PC13; `GYRO_2_CS PB3` / EXTI PA15 | PROVEN |
| Closed BF PR #835 | CS↔SKU inference: ICM→PB4/PC13, MPU→PB3/PA15 | INFERRED (community merge intent) |
| HDZero product/manual | Dual gyro SKU wording (WP1A audit) | PROVEN at product level |
| AP drivers | `Invensense` (MPU6000), `Invensensev3` (ICM42688P) | SUPPORTED |
| SPI WHO_AM_I / MAVLink INS on Halo | No device connected | ABSENT |

`hwdef.dat` probes:

```text
IMU Invensensev3 SPI:icm42688_1 ROTATION_NONE
IMU Invensense   SPI:mpu6000_1  ROTATION_NONE
IMU Invensensev3 SPI:icm42688_2 ROTATION_NONE
IMU Invensense   SPI:mpu6000_2  ROTATION_NONE
```

Compile-time only until a board is available for read-only SPI identify (still requires flashed firmware or BF CLI — flash forbidden this WP).

## Battery voltage / current

| Field | Value | Class |
|-------|-------|-------|
| ADC pins | VBAT `PC0`, CURR `PC2`, RSSI `PC1` | PROVEN (BF config) |
| `DEFAULT_CURRENT_METER_SCALE` | **100** (BF FC ADC) | PROVEN for BF; mapped to `HAL_BATT_CURR_SCALE 100.0` |
| `VBAT_SCALE` / `HAL_BATT_VOLT_SCALE` | **11.0 placeholder** | **PROVISIONAL / UNPROVEN** |
| Halo ESC “current scale 170” | ESC-side telemetry, **not** FC ADC scale | Do not conflate |
| Divider ratio from schematic / measured | ABSENT | |

Manual/PDF and BF config do **not** publish a voltage divider constant usable as ArduPilot `BATT_VOLT_MULT`. Treat `11.0` as offline placeholder only; calibrate on a known supply after approved flash.

## Sources

- `https://github.com/betaflight/config/blob/master/configs/HDZO/HDZERO_HALO/config.h` (ADC / gyro / `DEFAULT_CURRENT_METER_SCALE`)
- Local: `hwdef/HDZeroHalo/hwdef.dat` ADC + IMU blocks  
- Local: `Tools/HDZeroHalo/WP1A_DRIVER_COMPATIBILITY.md`, `WP1A_PINMAP.md`
