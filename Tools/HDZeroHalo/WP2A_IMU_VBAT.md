# WP2A_IMU_VBAT — relative IMU frames and nominal battery scales

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
No on-board identification, calibration or motion tests were performed.

## Both gyro SKUs

Official HDZero documentation describes MPU6000 or ICM42688 variants. Both
drivers remain probed on SPI1, on both PB4/PB3 chip selects. PC13/PA15 are the
BF DRDY resources; the AP drivers support periodic FIFO reads without requiring
these interrupts. WHO_AM_I checks reject the wrong driver before device setup.

MODE3 and the MPU8MHz/ICM16MHz requested maximum speeds match existing AP
patterns. With the retained80MHz SPI kernel the actual high speeds are5MHz
and10MHz respectively; low speeds are0.625MHz and1.25MHz. These are clock-tree
calculations, not scope measurements.

## Exact relative axis matrices

Let r be the sensor's signed raw-register vector. This applies separately to
accelerometer and gyroscope data, excluding bias/scale calibration:

```text
A_MPU = [ 0  1  0 ]    A_ICM = [ 1  0  0 ]
        [ 1  0  0 ]            [ 0  1  0 ]
        [ 0  0 -1 ]            [ 0  0  1 ]

MPU driver output = A_MPU * r
ICM driver output = A_ICM * r

R(ROLL_180_YAW_90) = A_MPU
A_MPU * A_MPU = I; determinant(A_MPU) = +1

MPU configured output = A_MPU * A_MPU * r = r
ICM configured output = I * I * r = r
```

`Invensense.cpp:613-615,633-635` performs the MPU transformation. Its fast
FIFO path also exchanges X/Y and negates Z for both sensors. Invensensev3 uses
XYZ in the normal and high-resolution paths. `AP_Math/vector3.cpp:80-83`
implements the compensating rotation. Existing rotation unit tests exercise
the production rotation implementation.

The board definition now uses:

```text
IMU Invensensev3 SPI:icm42688_1 ROTATION_NONE
IMU Invensense   SPI:mpu6000_1  ROTATION_ROLL_180_YAW_90
IMU Invensensev3 SPI:icm42688_2 ROTATION_NONE
IMU Invensense   SPI:mpu6000_2  ROTATION_ROLL_180_YAW_90
```

This establishes a common raw-register reference, **not a proven body frame**.
If Q maps that reference to the mounted board, both still require Q. No
unproved absolute mounting rotation has been added.

Official BF4.5.1 enables both drivers, defaults both alignments to CW0 without
Halo overrides, and uses the common raw-XYZ readers. This supports relative
normalisation, but cannot prove actual package orientation, installation
direction or factory alignment overrides.

Required on each SKU: verify part/CS identity, six static faces and signed
rotations about all three axes against board markings; then determine the
absolute mapping. Until then `H3_IMU_ROTATION = HARDWARE_BLOCKED`.

## Nominal voltage and current

| Item | Source-derived value | Physical qualification |
| ------ | ---------------------- | ------------------------ |
| VBAT PC0 | ADC channel10; nominal `HAL_BATT_VOLT_SCALE=11.0` | Uncalibrated |
| Current PC2 | ADC channel12; nominal100 A/V | Uncalibrated |
| RSSI PC1 | ADC channel11 | Unmeasured |

BF voltage defaults are scale110, divider10, multiplier1. Its centivolt
conversion corresponds to11 times the ADC pin voltage. AP multiplies ADC volts
by `BATT_VOLT_MULT` at `AP_BattMonitor_Analog.cpp:160`;11.0 is therefore a
software-supported nominal setting, not an arbitrary peer placeholder.

BF current scale is in mV/10A; AP uses A/V. Conversion is
`AP_A_PER_V = 10000 / BF_scale`, so BF100 gives AP100. Do not generalise this
numerical equality to other scales. The ESC-side170 setting is unrelated.

These formulas do not measure actual resistors, reference voltage, current
gain or offset. Calibrate voltage against a known supply/DMM and current
against a suitable reference before relying on battery failsafes in flight.

## Sources

- [Official Halo target](https://github.com/betaflight/config/blob/e0273b9564854e0ee1fbadd8200875b30bd35650/configs/HDZO/HDZERO_HALO/config.h)
- [HDZero SKU description](https://github.com/hd-zero/hdzero-docs/blob/main/docs/halo-introduction.md)
- [BF4.5.1 voltage conversion](https://github.com/betaflight/betaflight/blob/77d01ba3b76a22909d5f09cb0628820141f95eaa/src/main/sensors/voltage.c)
- [BF4.5.1 current conversion](https://github.com/betaflight/betaflight/blob/77d01ba3b76a22909d5f09cb0628820141f95eaa/src/main/sensors/current.c)
- Local `AP_InertialSensor_Invensense.cpp`, `AP_InertialSensor_Invensensev3.cpp`,
  `AP_Math/vector3.cpp`, `AP_BattMonitor_Analog.cpp`.
