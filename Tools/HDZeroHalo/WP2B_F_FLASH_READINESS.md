# WP2B_F_FLASH_READINESS — first ArduPilot USB bench vs flight

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO** (no flash authorised by this document)

## Two bars

| Bar | Meaning |
| --- | ------- |
| **FIRST_AP_USB_BENCH** | Flash AP BL+app on USB-only FC; enumerate MAVLink/USB; no motors, no LiPo, no flight |
| **FLIGHT_READY** | Full vehicle: baro, ESC/DShot, power, failsafes, IMU polarity complete, etc. |

This WP only scores readiness toward **FIRST_AP_USB_BENCH**.

## Gate checklist

| Gate | Status | Notes |
| ---- | ------ | ----- |
| HSE software chain HSE8 | PASS (provisional) | SOURCE_CONFIRMED BF + AP match; PHYSICAL_UNPROVED |
| HSE physical proof | OPEN | Photo/scope optional for bench; stronger need before timing-critical flight I/O |
| Exact BF recovery hex `e0b7bb01b` | **MISSING** | Plan: cloud Online + `diff all`; alt 4.5.1 Halo hex archived |
| BF config backup | PASS | WP2B-B `diff all` / `dump` copied to evidence/wp2b-f |
| DFU procedure documented | PASS | OEM + checkpoints; **hardware DFU untested** |
| DFU hardware exercise | **NOT_PERFORMED** | Requires separate user approval |
| Flash layout understood | PASS | BF app @ `0x08040000` vs AP app @ `0x08020000`; full wipe; no dual-boot |
| ArduPilot Halo build | PASS (offline) | Copter + bootloader artifacts present under `build/HDZeroHalo/` (WP2B-D) |
| IMU rotation ICM | PASS (software) | `ROTATION_ROLL_180` (WP2B-D); Acc six-face proved |
| Gyro polarity | **OPEN** | WP2B-E stopped incomplete |
| MPU SKU rotation | UNTESTED on HW | `YAW_270` composed; this board is ICM |
| External barometer | Not required for USB bench | **Blocks normal Copter startup / flight** without baro or special recovery path |
| PE3 / 9V safe default | PASS (software intent) | AP holds PE3 LOW after GPIO init; electrical unproved; live BF had PINIO unmapped |
| DShot / current / VTX | Out of scope for first USB bench | Explicitly deferred |

## FIRST_AP_USB_BENCH readiness

```text
FIRST_AP_BENCH_READINESS = NOT_READY
```

### Open blockers (must clear or accept in writing before any flash approval)

1. **User flash authorisation** — still `HARDWARE_FLASH_ALLOWED = NO`.  
2. **DFU round-trip untested** — recommend one BF→DFU→BF restore drill *before* first AP flash (separate approval).  
3. **Exact 2026.6.2 `e0b7bb01b` image not archived** — recovery depends on cloud Online or accepting 4.5.1 / near-build risk.  
4. **Physical HSE unproved** — acceptable only as *explicit provisional* for USB bench; AP USB is HSE-derived.  
5. **Gyro polarity incomplete** — Acc map applied; rate signs not closed (WP2B-E stopped).  
6. **No baro** — expect Copter startup/prearm limitations; USB config-error recovery only if that path is used.

### Acceptable “bench-only” risk acceptances (human decision)

A human may waive (1)–(5) partially for a **USB-only** experiment if recovery plan + backups are accepted — that waiver is **not** granted by this WP.

## Out of scope for this readiness bar

- DShot / ESC / motors  
- Current / VBAT calibration with pack  
- VTX / PINIO switching tests  
- Flight modes / failsafes validation  
- WP3 bring-up automation
