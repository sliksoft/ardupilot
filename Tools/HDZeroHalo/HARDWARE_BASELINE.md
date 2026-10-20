# HDZero Halo — hardware-tested ArduCopter USB baseline

Date locked: 2026-10-21. Branch: `board/hdzero-halo`.

This document marks the first hardware-proven USB/MAVLink baseline for the
HDZero Halo STM32H743 ArduCopter port. It does **not** authorize flight, ARM,
or further flash without a new authorization.

## Proven on hardware

| Gate | Status |
| --- | --- |
| WP3-K production BL + ArduCopter flash / cold USB boot | PASS |
| USB CDC enumerate `1209:5741` product `HDZeroHalo` | PASS |
| MAVLink HEARTBEAT + Mission Planner wire path | PASS |
| WP4-A roll / pitch / level IMU attitude | PASS |
| WP4-B Quad/X (`FRAME_CLASS=1`, `FRAME_TYPE=1`) | PASS |
| WP4-C 1195-parameter inventory | COMPLETE |
| DShot300 configured on outputs 1–4 | PASS (config / STATUSTEXT) |
| Internal MAVLink error counters | none reported |

## Image hashes (flashed)

| Image | SHA256 |
| --- | --- |
| `HDZeroHalo_bl.bin` | `4f92d710e21be29daed876084be9db7045e6f29ef08d290c4f9ab0253cb1d52f` |
| `arducopter.bin` | `ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7` |

Live identity: `ArduCopter V4.8.0-dev (c1a1fc2d)`, board 1414.

## Source / docs map

| Area | Location |
| --- | --- |
| Production hwdef | `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/` |
| Diagnostic BL hwdef | `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHaloDiagBL/` |
| Bootloader images | `Tools/bootloaders/HDZeroHalo_bl.{bin,elf,hex}` |
| Evidence + hashes | `Tools/HDZeroHalo/evidence/` |
| Feature matrix | `PORT_STATUS.md` |

## Explicit non-goals of this baseline

- No motor spin / ESC / bidirectional DShot proof
- No RC, GPS, mag, baro, or battery pack qualification
- No ARM / flight
- Production ECC recovery still able to erase flash sectors later
