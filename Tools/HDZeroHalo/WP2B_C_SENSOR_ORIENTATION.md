# WP2B_C_SENSOR_ORIENTATION — six-face MSP test (ICM42688P)

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Unit:** same Halo as WP2B-B (UID `004000383533510f39303730`)  
**Method:** read-only MSP `MSP_RAW_IMU` (102) on `/dev/ttyACM0` — no CLI `set`/`save`, no calibration  
**HARDWARE_FLASH_ALLOWED = NO**

Raw evidence (outside Git):  
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-c/orientation/`

## Body convention used with the operator

| Axis | Physical meaning |
| ---- | ---------------- |
| Forward (X+) | Opposite USB Type-C (USB = aft) |
| Right (Y+) | Board right when looking forward |
| Up (Z+) | Component side up |
| Acc rule | Axis pointing **up** reads ≈ **+1 g** |
| Scale | ≈ **2048 LSB/g** on this BF 2026.6.2 MSP stream |

## Results (mean of 50 samples after settle)

| Face | Acc g≈ (X,Y,Z) | Dominant | Expected if Xfwd/Yright/Zup |
| ---- | -------------- | -------- | --------------------------- |
| 1 flat top-up | (−0.05, +0.03, **+0.99**) | AccZ=+1 | AccZ=+1 **MATCH** |
| 2 flat bottom-up | (~0, +0.06, **−1.01**) | AccZ=−1 | AccZ=−1 **MATCH** |
| 3 right side down | (−0.09, **+1.03**, −0.05) | AccY=+1 | AccY=−1 **DIFF** |
| 4 left side down | (+0.03, **−0.96**, −0.02) | AccY=−1 | AccY=+1 **DIFF** |
| 5 nose down | (**−1.01**, +0.10, −0.03) | AccX=−1 | AccX=−1 **MATCH** |
| 6 nose up | (**+0.98**, +0.03, −0.02) | AccX=+1 | AccX=+1 **MATCH** |

Gyro means stayed near zero on quiet faces; face 3 showed higher residual motion (USB cable / hand) but AccY dominance remained clear.

## Comparison to ArduPilot ICM `ROTATION_NONE`

Current `hwdef.dat`:

```text
IMU Invensensev3 SPI:icm42688_1 ROTATION_NONE
```

| Claim | Level |
| ----- | ----- |
| Live gyro is ICM42688P @ PB4 | LIVE (WP2B-B) |
| BF board/gyro align 0 / CW0 | LIVE_CFG (WP2B-B) |
| MSP raw X = forward (USB aft) | LIVE six-face **MATCH** |
| MSP raw Z = up (components up) | LIVE six-face **MATCH** |
| MSP raw Y = board right | **AMBIGUOUS** (measured opposite to assumed right) |
| Need to change ICM rotation | **NOT PROVED** — do not edit hwdef |

### Y-axis ambiguity

Under the stated USB=aft convention, right-down should yield AccY≈−1 and left-down AccY≈+1. Measured signs are reversed, while X/Z match. A single-axis sign flip is **not** a proper rotation (would break right-handedness). Most plausible explanations:

1. Operator left/right vs silkscreen / USB-aft forward disagreed; or  
2. Board “right” silk vs assumed forward needs a photo confirmation.

Until L/R is photo-confirmed, **retain `ROTATION_NONE`**. Changing rotation on Y ambiguity alone would risk breaking the proved X/Z mapping.

### BF ↔ AP frame note

MSP data are the BF body/sensor stream with CW0. AP Invensensev3 + `ROTATION_NONE` keeps the ICM register XYZ identity (same relative strategy as WP2A/WP2B-A). Absolute agreement with vehicle silk after first AP boot still needs AHRS/level checks on hardware — **not** done here (no AP flash).

## Gyro sign (not exercised)

Static faces do not prove gyro polarity. Optional later (still read-only MSP): slow signed rotations about each body axis while watching `GyrX/Y/Z`. Not required to close this WP’s “no confident orientation bug” verdict for retaining `ROTATION_NONE`.

## Verdict

```text
IMU_ORIENTATION_TEST = COMPLETE_SIX_FACE_ACC
X_FORWARD = MATCH (USB aft)
Z_UP = MATCH (component side)
Y_RIGHT = AMBIGUOUS (measured opposite; confirm silk/photo)
AP_ICM_ROTATION = RETAIN_ROTATION_NONE
ORIENTATION_BUG_REQUIRING_HWDEF_CHANGE = NOT_SHOWN
MPU6000_SKU = NOT_ON_THIS_UNIT
```
