# WP1B_INDEPENDENT_REVIEW

**Date:** 2026-10-18  
**Reviewer:** independent read-only agent vs WP1A + BF `HDZERO_HALO`  
**Implementer:** applied fixes and rebuilt

**Historical review correction:** the buzzer conclusion below was wrong.
BF `BEEPER_INVERTED` maps to active HIGH, not LOW. The new fix uses PD12 LOW
after GPIO initialisation and `DEFAULT_BUZZ_ON_LVL=1`; see
`WP2A_REVIEW_FIX_REPORT.md`. Original build observations below are historical.

## Verdict

| Scope | Result |
| ------- | -------- |
| Offline configure / Copter / bootloader | **PASS** (after fixes) |
| Hardware flash readiness | **FAIL** (expected — HSE + layout UNKNOWN) |

## Findings and disposition

| Sev | Finding | Action |
| ----- | --------- | -------- |
| CRITICAL | HSE UNKNOWN | Kept provisional 8 MHz + DO NOT FLASH banners |
| CRITICAL | Flash layout vs BF UNKNOWN | Kept 128 KB layout; documented alt 384 KB |
| MAJOR | Original recommendation `DEFAULT_BUZZ_ON_LVL 0` was incorrect | Superseded: active HIGH / initial LOW in review fix |
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
