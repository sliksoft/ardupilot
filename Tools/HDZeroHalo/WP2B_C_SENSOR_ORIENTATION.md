# WP2B_C_SENSOR_ORIENTATION — six-face MSP test (ICM42688P)

**Date:** 2026-10-18 (corrected same day — frame reconciliation)  
**Branch:** `board/hdzero-halo`  
**Unit:** UID `004000383533510f39303730`  
**Method:** read-only MSP `MSP_RAW_IMU` — no CLI `set`/`save`, no calibration  
**HARDWARE_FLASH_ALLOWED = NO**

Raw evidence: `evidence/wp2b-c/orientation/`  
Frame correction detail: `WP2B_C_FRAME_RECONCILIATION.md`

## Body convention used during the test

| Axis | Physical meaning |
| ---- | ---------------- |
| Forward | Opposite USB Type-C (USB = aft) |
| Right / Left | Board sides when looking forward |
| Up | Component side up |
| Acc rule | Axis pointing **up** reads ≈ **+1 g** |
| Scale | ≈ **2048 LSB/g** on BF 2026.6.2 MSP Acc |

## Results (mean of 50 samples)

| Face | Acc g≈ (X,Y,Z) | Dominant |
| ---- | -------------- | -------- |
| 1 flat top-up | (−0.05, +0.03, **+0.99**) | AccZ=+1 |
| 2 flat bottom-up | (~0, +0.06, **−1.01**) | AccZ=−1 |
| 3 right side down | (−0.09, **+1.03**, −0.05) | AccY=+1 |
| 4 left side down | (+0.03, **−0.96**, −0.02) | AccY=−1 |
| 5 nose down | (**−1.01**, +0.10, −0.03) | AccX=−1 |
| 6 nose up | (**+0.98**, +0.03, −0.02) | AccX=+1 |

## Correct frame interpretation (post-correction)

MSP Acc matches **Betaflight / MultiWii body**: **X forward, Y left, Z up** (all six faces).

The first WP2B-C write-up wrongly assumed Y-right and labelled Y “ambiguous.” That was an analysis error, not noisy data. See `WP2B_C_FRAME_RECONCILIATION.md`.

ArduPilot body is **X forward, Y right, Z down**. Mapping BF→AP:

```text
ROTATION_ROLL_180: (x, y, z) → (x, -y, -z)
```

## Comparison to hwdef at WP2B-C time (`ROTATION_NONE`)

> **Update:** WP2B-D applied ICM `ROTATION_ROLL_180` (and MPU `YAW_270`). The comparison below describes the pre-WP2B-D tree.

| Claim | Level |
| ----- | ----- |
| Live gyro ICM42688P @ PB4 | LIVE (WP2B-B) |
| BF CW0 / board align 0 | LIVE — MSP Acc = BF body |
| ICM register XYZ, no v3 remap | SOURCE (Invensensev3 FIFO `accel[0..2]`) |
| Six-face = BF Y-left Z-up | LIVE + math |
| `ROTATION_NONE` correct for AP FRD? | **NO** — leaves Y-left Z-up |
| `ROTATION_ROLL_180` indicated? | **YES** (Acc-based); **not applied** (no firmware change) |
| Gyro polarity proved? | **NO** — optional follow-up |

MPU `ROTATION_ROLL_180_YAW_90` still only matches ICM `NONE` at the raw-register frame (WP2A). Any future ICM→`ROLL_180` edit must update the MPU line in lockstep for the other SKU.

## Gyro

Static faces do not prove gyro signs. Acc six-face is sufficient to indicate ROLL_180 for the Acc axis map. Optional signed rate tests remain useful before flash.

## Verdict

```text
IMU_ORIENTATION_TEST = COMPLETE_SIX_FACE_ACC
MSP_FRAME = BF_X_FWD_Y_LEFT_Z_UP (MATCH)
AP_FRD_MAP = ROTATION_ROLL_180 (INDICATED)
AP_ICM_HWDEF = WP2B-C_SNAPSHOT_ROTATION_NONE; SUPERSEDED_BY_WP2B-D_ROLL_180
PRIOR_Y_AMBIGUOUS_CLAIM = RETRACTED
MPU6000_SKU = NOT_ON_THIS_UNIT
HARDWARE_FLASH_ALLOWED = NO
```
