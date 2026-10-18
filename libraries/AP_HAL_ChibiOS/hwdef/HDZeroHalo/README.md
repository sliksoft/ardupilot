# HDZero Halo — ArduPilot hwdef (WP1B)

**HARDWARE_FLASH_ALLOWED = NO**  
**OSCILLATOR_STATUS = UNKNOWN** (provisional `OSCILLATOR_HZ 8000000` for compile only)

Standard ArduCopter ChibiOS board port. Pin map from Betaflight
`configs/HDZO/HDZERO_HALO/config.h`. Motor TIM3 PC6–PC9 follows `AnyleafH7`.

## Do not flash

Until HSE frequency, flash layout vs factory BF, IMU rotation, VBAT scale, and
PE3 9V polarity are verified on hardware, treat all binaries as
**NOT VERIFIED — DO NOT FLASH**. Recovery remains STM32 DFU → Betaflight.

## Build (offline)

```sh
source .venv/bin/activate
./waf configure --board HDZeroHalo
./waf copter
Tools/scripts/build_bootloaders.py HDZeroHalo
```

## Board ID

`AP_HW_HDZERO_HALO` = **1414** (provisional development ID in
`board_types.txt`). Not an official manufacturer reservation.

## Deviations from Betaflight

| Topic | BF | This hwdef |
| ------- | ---- | ------------ |
| DShot path | bitbang default | Timer DMA TIM3 (+ BIDIR) |
| Buzzer | Active HIGH with `BEEPER_INVERTED` | GPIO idle LOW, active HIGH in application; idle LOW in bootloader |
| LED strip | TIM1 CH3 | Addressable LEDs unsupported: PWM5 **NODMA** |
| PE3 9V | CLI PINIO | LOW after GPIO initialisation; reset/ROM DFU unverified; no RELAY default |
| HSE | Makefile defaults to 8 MHz | HSE8 retained for builds; physical source unverified |

See `Tools/HDZeroHalo/WP1B_*.md` for build evidence and review.

## External barometer and bench startup

The normal Copter configuration requires an external barometer on I2C1
(PB8 SCL, PB9 SDA). The default `BARO_PROBE_EXT` mask is 1030: BMP280 (2),
MS5611 (4), BMP388 (1024). Existing saved parameter values override defaults.
`BARO_EXT_BUS=-1` scans external buses; this board exposes I2C1 as external.
Select a supported probe mask, save, and reboot after changing it.

Without a detected barometer the existing configuration-error loop keeps USB
MAVLink available for parameter recovery. It does not complete normal startup,
initialise the OSD, or provide a no-baro flight configuration. No fake barometer,
arming-check override, or `HAL_BARO_ALLOW_INIT_NO_BARO` is used. An unhealthy
detected barometer remains subject to standard prearm checks.

## IMU orientation

Both gyro SKUs remain probed on both chip selects. MPU probes apply
`ROTATION_ROLL_180_YAW_90` to cancel the driver's internal `(y,x,-z)` mapping;
ICM42688 probes retain `ROTATION_NONE`. This only aligns their raw-register
frames. Absolute mounting orientation and signed accel/gyro responses on each
SKU remain hardware blockers. See `Tools/HDZeroHalo/WP2A_IMU_VBAT.md`.
