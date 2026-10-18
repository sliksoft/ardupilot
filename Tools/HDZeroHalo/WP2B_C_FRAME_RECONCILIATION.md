# WP2B_C_FRAME_RECONCILIATION — BF vs AP axes (correction)

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**HARDWARE_FLASH_ALLOWED = NO**  
**No hwdef / firmware edits in this correction.**

Uses existing six-face Acc data under `evidence/wp2b-c/orientation/` plus BF 4.5.1
and ArduPilot sources. Independent math review agreed with the conclusions below.

## 1. Coordinate conventions

| System | X | Y | Z | Level Acc (specific force / “up” rule) |
| ------ | - | - | - | -------------------------------------- |
| Betaflight / MultiWii body | forward | **left** | **up** | ≈ (0, 0, **+1 g**) |
| ArduPilot body (NED / FRD) | forward | **right** | **down** | ≈ (0, 0, **−1 g**) |

Original WP2B-C incorrectly analysed MSP data as if Y were **right**. That made
faces 3–4 look “ambiguous.” Under Y-**left**, all six faces **MATCH**.

Map BF body → AP body (proper rotation, det = +1):

```text
ROLL_180:  (x, y, z)_BF  →  (x, -y, -z)_AP
```

## 2. What Betaflight applies before `MSP_RAW_IMU`

From BF 4.5.1 `sensors/acceleration.c` and `msp/msp.c`:

1. Driver fills `ADCRaw[X,Y,Z]` from ICM `ACCEL_DATA_X1`… (register XYZ order).  
2. `alignSensorViaRotation(..., accAlign)` — Halo live align **CW0** / board 0,0,0 → **identity**.  
3. Optional calibration trims / LPF.  
4. `MSP_RAW_IMU` writes `acc.accADC[0..2]` then gyro dps then mag.

So on this Halo, **MSP Acc ≈ BF body Acc** (CW0). Gyro path is analogous
(`alignSensorViaRotation` on `gyroADC` before use; MSP reports `gyroRateDps(i)`).

## 3. ICM42688P register / FIFO XYZ order

| Path | Order |
| ---- | ----- |
| BF ICM driver | `ACCEL_DATA_X1` @ 0x1F → `ADCRaw[X], [Y], [Z]` |
| AP Invensensev3 FIFO | `FIFOData.accel[0..2]` / `gyro[0..2]` as Vector3f X,Y,Z — **no** `(y,x,-z)` remap |

Unlike classic `Invensense` (MPU), v3 keeps register XYZ. Relative ICM↔MPU
normalisation (WP2A) still only aligns to a **common raw-register frame**, not
to AP FRD.

## 4. `AP_InertialSensor_Invensensev3`

After scale, samples go through `_rotate_and_correct_accel/gyro` with the
hwdef `Rotation`. Halo currently:

```text
IMU Invensensev3 … ROTATION_NONE   # WP2B-C-time snapshot; WP2B-D uses ROLL_180
```

`ROTATION_NONE` leaves the raw-register / BF-body (CW0) frame unchanged.
Interpreted as AP FRD, that is **Y-left Z-up** — incorrect for ArduPilot.

`ROTATION_ROLL_180` implements `(x,y,z)→(x,-y,-z)` (`AP_Math/vector3.cpp`).

Note: `convert_betaflight_unified.py` maps BF `CW0` → `ROTATION_YAW_270` and
calls BF alignment a “mysterious art.” That table is **not** authoritative for
this Invensensev3 + six-face evidence; do not use it to waive ROLL_180.

## 5. Six-face data vs frames

Operator poses (USB = aft, components = up). Rule: axis pointing up ≈ +1 g.

| Face | Measured dominant | BF Y-left Z-up | Old WP2B-C Y-right Z-up | After ROLL_180 → AP FRD |
| ---- | ----------------- | -------------- | ----------------------- | ------------------------ |
| Top-up | AccZ=+0.99 | MATCH | MATCH | AccZ=−1 MATCH |
| Bottom-up | AccZ=−1.01 | MATCH | MATCH | AccZ=+1 MATCH |
| Right down | AccY=+1.03 | MATCH | **FAIL** (wanted −1) | AccY=−1 MATCH |
| Left down | AccY=−0.96 | MATCH | **FAIL** (wanted +1) | AccY=+1 MATCH |
| Nose down | AccX=−1.01 | MATCH | MATCH | AccX=−1 MATCH |
| Nose up | AccX=+0.98 | MATCH | MATCH | AccX=+1 MATCH |

**Correction:** Y was not ambiguous; the analysis used the wrong lateral sense.

## 6. Rotation assessment (ICM on this unit)

| Option | Verdict |
| ------ | ------- |
| Keep `ROTATION_NONE` | **Incorrect** for AP FRD if MSP/CW0 Acc ≡ chip raw ≡ BF body |
| Prefer `ROTATION_ROLL_180` | **Indicated** by frame math + six-face Acc (ICM SKU) |
| Change hwdef now | **Not done** — documentation-only WP; human gate before edit |

MPU6000 path (`ROTATION_ROLL_180_YAW_90`) still only cancels the MPU driver remap
to the same raw-register frame as ICM `NONE`. If ICM moves to `ROLL_180`, the
MPU SKU needs a composed rotation to the same AP FRD — **not on this board**
(ICM only).

## 7. Are gyro measurements required?

| Question | Acc six-face enough? |
| -------- | -------------------- |
| Static Acc axis map BF body ↔ named board faces | **Yes** |
| Choose ROLL_180 vs NONE for Acc FRD | **Yes** (with BF Y-left / AP FRD premises) |
| Gyro rate polarity / Acc–Gyro co-alignment | **No** — still open |

Optional before flash (still read-only MSP): slow signed rotations about X/Y/Z
and check `Gyr*` signs against BF/AP expectations. Not required to justify the
Acc-based ROLL_180 indication.

## 8. Residual uncertainties

1. Forward = USB-aft was an operator convention; silk arrow photo would lock it.  
2. Acc magnitudes ~1–3% off 1.00 (bias/level/trim) — does not flip signs.  
3. No gyro polarity proof yet.  
4. First AP boot AHRS/level check still required after any hwdef rotation edit.  
5. MPU SKU absolute rotation still untested.  
6. Index note: GitNexus ardupilot index was stale during this review; conclusions
   are from direct source reads + measured JSON, not from the graph alone.

## Verdict

```text
BF_BODY = X_FWD_Y_LEFT_Z_UP (MultiWii; MATCHES six-face MSP)
AP_BODY = X_FWD_Y_RIGHT_Z_DOWN
MSP_RAW_IMU_ON_HALO = BF_BODY_AFTER_CW0
ICM_REGISTER_XYZ = NO_DRIVER_REMAP (Invensensev3)
FRAME_MAP_BF_TO_AP = ROTATION_ROLL_180
PRIOR_WP2B_C_Y_AMBIGUOUS = CORRECTED (was wrong Y-right assumption)
ROTATION_NONE = NOT_CORRECT_FOR_AP_FRD
ROTATION_ROLL_180 = INDICATED_AT_WP2B-C; APPLIED_IN_WP2B-D (see WP2B_D_IMU_ROTATION_FIX.md)
GYRO_SIGN_PROOF = STILL_OPTIONAL_OPEN
HARDWARE_FLASH_ALLOWED = NO
```
