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
|-------|----|------------|
| DShot path | bitbang default | Timer DMA TIM3 (+ BIDIR) |
| Buzzer | TIM4 mapping available | GPIO idle HIGH (inverted) |
| LED strip | TIM1 CH3 | TIM1 PWM5 **NODMA** |
| PE3 9V | CLI PINIO | GPIO held LOW; no RELAY default |
| HSE | unset in config.h | Provisional 8 MHz (UNKNOWN) |

See `Tools/HDZeroHalo/WP1B_*.md` for build evidence and review.
