# WP4-A: HDZero Halo USB IMU & attitude qualification

Date: 2026-10-21. **Read-only hardware test.** No flash, erase, ARM, motor
test, calibration, parameter write, commit, push or merge.

```text
USB_MAVLINK                    = PASS
IMU_DETECTION                  = PASS_ICM42688P_ASSUMED_FROM_HEALTH_AND_HWDEF
GYRO_AXES                      = PASS
ACCEL_AXES                     = PASS
ROLL_DIRECTION                 = PASS
PITCH_DIRECTION                = PASS
LEVEL_ATTITUDE                 = PASS
AHRS_STATUS                    = PASS_ATTITUDE_LIVE_EKF_FLAGS_NOISY
SENSOR_HEALTH                  = PASS_GYRO_ACCEL_ATTITUDE
PREARM_STATUS                  = FAIL_FRAME_CLASS_ZERO_EXPECTED_BENCH
CONFIGURATION_FINDINGS         = SEE_BELOW
WP4_A_RESULT                   = PASS
NEXT_RECOMMENDED_STEP          = SET_FRAME_CLASS_THEN_BENCH_PREARM_REVIEW
HARDWARE_FLASH_ALLOWED         = NO
```

Evidence:
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp4-a-usb-imu-attitude/`

Primary motion dataset (USB-referenced redo): `samples/redo/`  
(`REDO_SUMMARY.csv`, `redo_*_result.txt`, `capture_redo_*.jsonl`)

## Method notes

- Single reader on COM14 (Mission Planner disconnected during captures).
- Attitude from MAVLink `ATTITUDE`; accel/gyro from `SCALED_IMU` (mg / mdeg/s).
- Earlier session `RAW_IMU` values were **untrusted** (parser byte-offset bug);
  redo conclusions use `SCALED_IMU` + `ATTITUDE` only.
- Board reference: **USB = BACK**, front = opposite USB, top = component side.

## USB_MAVLINK = PASS

| Item | Result |
| --- | --- |
| USB | `1209:5741`, ArduPilot COM14, product `HDZeroHalo` |
| HEARTBEAT | Stable ~1–2 Hz during captures |
| Identity | `type=QUADROTOR`, `autopilot=ARDUPILOTMEGA` |
| Mode | `custom_mode=0` (STABILIZE), `system_status=STANDBY` |
| Armed | **Always DISARMED** (`base_mode` bit7 clear) |
| Errors | `errors_comm=0` on sampled `SYS_STATUS` |
| Firmware hint | `AUTOPILOT_VERSION.os_custom` contains `c1a1fc2d` |

## IMU_DETECTION = PASS (measured + static config)

**Measured:** gyro and accel present/enabled/**healthy** in `SYS_STATUS`.
Attitude stream continuous; ~1 g accel magnitude in all static poses.

**Static config (not a live chip-ID MAVLink field in this capture):**
hwdef probes `IMU Invensensev3 SPI:icm42688_* ROTATION_ROLL_180` (WP2B-D).
This unit historically ran ICM42688P @ PB4 (WP2B-B/C). Live `INS_*` params:
`INS_USE=1`, `INS_ENABLE_MASK=127`.

## Motion redo table (authoritative)

| Pose | Physical | Roll ° | Pitch ° | Accel X/Y/Z (mg) |
| --- | --- | ---: | ---: | --- |
| A | Top up, flat | −0.7 | +2.2 | 41 / 21 / **−1021** |
| B | Right edge down | **+88.0** | −5.4 | −93 / **−996** / −57 |
| C | Left edge down | **−90.2** | +2.4 | 40 / **+1000** / −20 |
| D | Front up (USB near table) | −170.4 | **+84.0** | **+992** / 16 / 80 |
| E | Front down (USB up) | +1.9 | **−82.1** | **−989** / −3 / −160 |
| F | Top up, flat again | −0.1 | −0.8 | −13 / 1 / **−1020** |

## LEVEL_ATTITUDE = PASS

A and F: near-zero roll/pitch, AccZ ≈ −1 g, |X|,|Y| small. Matches FRD level
with board top-up after `ROTATION_ROLL_180` (WP2B-C expected AccZ ≈ −1 g).

## ROLL_DIRECTION = PASS

- Right bank → **positive** roll, AccY ≈ −1 g.
- Left bank → **negative** roll, AccY ≈ +1 g.
- Not swapped with pitch.

## PITCH_DIRECTION = PASS

- Front up → **positive** pitch, AccX ≈ +1 g.
- Front down → **negative** pitch, AccX ≈ −1 g.
- Not swapped with roll.

## GYRO_AXES / ACCEL_AXES = PASS

- Accel axes track gravity under the six poses with consistent body mapping.
- Gyro responds during transitions; `SCALED_IMU` Z-gyro is **not** dead
  (non-zero samples observed; earlier “Z=0” was RAW_IMU parse artifact).

## AHRS_STATUS = PASS_ATTITUDE_LIVE_EKF_FLAGS_NOISY

- Live `ATTITUDE` consistent with accelerometer poses (see table).
- `AHRS_ORIENTATION=0` (no extra board rotation beyond IMU hwdef rotation).
- `AHRS_EKF_TYPE=3`, `EK3_ENABLE=1`.
- `EKF_STATUS` variance fields often nonsensical on this USB-only bench; flags
  vary. Attitude still usable via AHRS output. Treat EKF variances as
  **not qualified** for navigation here.

## SENSOR_HEALTH = PASS_GYRO_ACCEL_ATTITUDE

| Sensor | Health |
| --- | --- |
| Gyro / Accel / Attitude / Logging | healthy |
| Mag | present/enabled, **unhealthy** (no usable heading) |
| Baro | **absent** (`HAL_BARO_ALLOW_INIT_NO_BARO`) |
| GPS / RC | absent |
| Battery | unhealthy (USB-only, `voltage_mV=1`) |

Yaw: relative only; **no absolute heading claim**.

## PREARM_STATUS = FAIL_FRAME_CLASS_ZERO (expected on bench)

Live params: `FRAME_CLASS=0`, `FRAME_TYPE=12`.  
Prior STATUSTEXT: `PreArm: Motors: Check frame class and type`.  
`PREARM` bit present but not enabled for arming path in sampled status.
**No arming attempted.**

## CONFIGURATION_FINDINGS

| Source | Finding |
| --- | --- |
| Measured | Roll/pitch directions match FRD with USB=aft |
| Measured | Level AccZ ≈ −1 g with top-up |
| Static hwdef | ICM path `ROTATION_ROLL_180` |
| Live param | `AHRS_ORIENTATION=0` |
| Live param | EKF3 enabled |
| Live param | `FRAME_CLASS=0` blocks sensible prearm |
| Static/live | No onboard baro; mag enabled but unhealthy |

## WP4_A_RESULT = PASS

ICM/accel/gyro and attitude display are qualitatively correct on USB bench for
the documented board reference. Remaining gaps are configuration/prearm and
absent/unhealthy aux sensors—not axis inversion of roll/pitch.

## NEXT_RECOMMENDED_STEP

1. **Read-only or authorized param set:** choose correct `FRAME_CLASS` /
   `FRAME_TYPE` for the intended airframe (fixes PreArm frame message).
2. Re-check prearm list on USB bench (still no LiPo/motors).
3. Later: external baro/compass if needed; do **not** calibrate or arm until
   explicitly authorized.

**HARDWARE_FLASH_ALLOWED = NO** remains in force.
