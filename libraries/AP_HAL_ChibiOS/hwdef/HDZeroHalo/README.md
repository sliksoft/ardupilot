# HDZero Halo — ArduPilot hwdef

**HARDWARE_FLASH_ALLOWED = NO** (no further flash without new authorization)

**OSCILLATOR_STATUS = HSI64 software path** (`OSCILLATOR_HZ 0` → 400 MHz SYSCLK;
physical HSE unused). USB via HSI48 (`STM32_USBSEL_HSI48_CK`).

Standard ArduCopter ChibiOS board port. Pin map from Betaflight
`configs/HDZO/HDZERO_HALO/config.h`. Motor TIM3 PC6–PC9 follows `AnyleafH7`.

## Hardware USB baseline (2026-10-21)

Production BL + ArduCopter were flashed and qualified on USB bench
(WP3-K / WP4-A/B/C). See `Tools/HDZeroHalo/HARDWARE_BASELINE.md`.
Images: BL `4f92d710…`, app `ec4e56ca…` (`c1a1fc2d`, board 1414).

Still unproven: motor spin, RC, mag, baro, pack, PE3 9V rail, physical HSE,
ARM/flight. Recovery remains STM32 ROM DFU (+ archived BF / DiagBL images).

ROM DFU recovery uses the physical BOOT button at USB power-on. Software
ROM-DFU entry is disabled in both application and bootloader: the pinned
ChibiOS startup does not call `__entry_hook`. Normal AP USB bootloading is
separate. See `Tools/HDZeroHalo/WP2B_H_DFU_ENTRY.md` for offline evidence;
the physical recovery procedure remains untested on this FC.

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
| SYSCLK | HSE8 → up to 480 MHz | HSI64 → 400 MHz PLL1 (WP3-J); HSE unused |
| USB 48 MHz | HSI48 + CRS | HSI48 via `STM32_USBSEL_HSI48_CK` (app+BL); CRS not in this ChibiOS HAL |

See `Tools/HDZeroHalo/WP1B_*.md` for build evidence and review.

## External barometer and no-baro startup

`HAL_BARO_ALLOW_INIT_NO_BARO 1` is set so ArduCopter can complete normal startup
without an onboard or external barometer (same upstream option used on other
FPV boards without a baro). That option also skips the default barometer
prearm check. No extra Halo-specific arming blockade is added.

External barometers on I2C1 (PB8 SCL, PB9 SDA) remain supported. The default
`BARO_PROBE_EXT` mask is 1030: BMP280 (2), MS5611 (4), BMP388 (1024). Saved
parameter values override defaults. `BARO_EXT_BUS=-1` scans external buses;
this board exposes I2C1 as external. A future BMP388 (or other masked probe)
is detected when connected after save/reboot as usual.

This is **not** proof of flight safety or working altitude control without a
baro. Altitude-dependent modes still need a healthy barometer when used.

## IMU orientation

Both gyro SKUs remain probed on both chip selects. ICM42688 probes use
`ROTATION_ROLL_180` (BF body X-fwd/Y-left/Z-up → AP FRD), proved on the live
ICM unit via WP2B-C six-face Acc. MPU probes use `ROTATION_YAW_270` so that
after the driver's `(y,x,-z)` remap the composed map equals the same
`ROLL_180(raw)` FRD target; the MPU SKU itself is **not** physically qualified.
Gyro rate polarity and first AP AHRS check remain open.
See `Tools/HDZeroHalo/WP2B_D_IMU_ROTATION_FIX.md`.
