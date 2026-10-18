# WP1B_INDEPENDENT_REVIEW

**Date:** 2026-10-18  
**Reviewer:** independent read-only agent vs WP1A + BF `HDZERO_HALO`  
**Implementer:** applied fixes and rebuilt

## Verdict

| Scope | Result |
|-------|--------|
| Offline configure / Copter / bootloader | **PASS** (after fixes) |
| Hardware flash readiness | **FAIL** (expected — HSE + layout UNKNOWN) |

## Findings and disposition

| Sev | Finding | Action |
|-----|---------|--------|
| CRITICAL | HSE UNKNOWN | Kept provisional 8 MHz + DO NOT FLASH banners |
| CRITICAL | Flash layout vs BF UNKNOWN | Kept 128 KB layout; documented alt 384 KB |
| MAJOR | Inverted buzzer missing `DEFAULT_BUZZ_ON_LVL 0` | **Fixed** in `hwdef.dat` |
| MAJOR | VBAT scale placeholder | Documented; left 11.0 provisional |
| MAJOR | IMU ROTATION_NONE | Documented provisional |
| MINOR | SERIAL7/8 vs UART7/8 labeling | **Fixed** → `DEFAULT_SERIAL6/7` |
| MINOR | `MOT_PWM_TYPE 6` before DShot300 bench | **Fixed** → `5` |
| MINOR | Gyro EXTI omitted | Accepted (optional) |
| MINOR | Missing WP1B docs refs | **Fixed** (this file set) |

## Post-fix rebuild

- `./waf configure --board HDZeroHalo` SUCCESS  
- `./waf copter` SUCCESS (0 warnings/errors)  
- Confirmed in `hwdef.h`: `DEFAULT_BUZZ_ON_LVL 0`, `DEFAULT_SERIAL6/7`, `HAL_WITH_BIDIR_DSHOT`
