# WP2B_C_FINAL_REPORT — sensor orientation & hardware flash gates

**Date:** 2026-10-18 (frame correction appended same day)  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `bb0662895b1095453d881484fbef7f2222bd17be`  
**Method:** read-only MSP; source review BF 4.5.1 + AP Invensensev3; independent math check  
**Policy:** no flash, DFU, CLI writes, calibration, GPIO/PINIO, motors, or ArduPilot firmware edits  

Evidence: `evidence/wp2b-c/`  
Detail: `WP2B_C_SENSOR_ORIENTATION.md`, `WP2B_C_FRAME_RECONCILIATION.md`, `WP2B_C_HARDWARE_GATES.md`

## Main conclusion

**Six-face MSP Acc on this ICM42688P Halo matches Betaflight body X-forward / Y-left / Z-up (CW0). ArduPilot FRD is X-forward / Y-right / Z-down. The proper map is `ROTATION_ROLL_180`.**

> **Historical note (WP2B-C as executed):** this work package documented the finding only and did **not** edit firmware.  
> **Superseded by WP2B-D:** hwdef now uses ICM `ROTATION_ROLL_180` and MPU `ROTATION_YAW_270`. Treat status lines below that still say `ROTATION_NONE` as the WP2B-C-time snapshot, not current tree state.

**Correction:** the first WP2B-C text that called Y “ambiguous” used a mistaken Y-right assumption; the measurements are consistent with Y-left.

## Status block

```text
WP2B_C_STATUS = PASS_ORIENTATION_FRAME_CORRECTED

CONNECTION = PASS (/dev/ttyACM0 0483:5740 HDZERO_HALO)
READ_ONLY = YES
FIRMWARE_FLASHED = NO
CONFIG_CHANGED = NO
HWDEF_CHANGED = NO
MSP_USED = YES (API 1.48; RAW_IMU + identity GETs)

MCU = STM32H743xx
MCU_ID = 004000383533510f39303730
BF_VERSION = 2026.6.2 MSP 1.48
IMU = ICM42688P

SIX_FACE_ACC = COMPLETE
  MSP_FRAME = BF_X_FWD_Y_LEFT_Z_UP (MATCH 6/6)
  AP_FRD_MAP = ROTATION_ROLL_180 (INDICATED)
  AP_ICM_HWDEF = ROTATION_NONE (WP2B-C SNAPSHOT; SUPERSEDED_BY_WP2B-D_ROLL_180)
  PRIOR_Y_AMBIGUOUS = RETRACTED

HSE_PHYSICAL = STILL_UNPROVED
DFU_RECOVERY = DOCUMENTED_UNTESTED
PE3_9V = STILL_UNPROVED
VBAT_IBATA_CAL = STILL_UNPROVED
AP_DSHOT_HW = STILL_UNPROVED
EXTERNAL_BARO = REQUIRED_FOR_FLIGHT_NOT_FITTED
GYRO_SIGN_PROOF = OPEN (optional)

HARDWARE_FLASH_ALLOWED = NO

HEAD_SHA = ee31671c3bc652d5d32a18d26a356ec61b6eab51
PUSH_STATUS = PUSHED_origin_board_hdzero-halo
NEXT_ACTION =
  Human decision whether to edit hwdef ICM (and MPU composition) to ROLL_180
  before any flash; optional gyro sign MSP test; crystal/DFU gates unchanged;
  do not start WP3 automatically
```

## What this WP closed / corrected

| Item | Result |
| ---- | ------ |
| MSP identity | PASS (same UID as WP2B-B) |
| Live Acc/Gyro stream | PASS |
| Absolute Acc vs BF body | MATCH Y-left Z-up |
| BF↔AP frame map | `ROLL_180` indicated |
| `ROTATION_NONE` for AP FRD | **Incorrect** at WP2B-C; **fixed in WP2B-D** (`ROLL_180`) |
| Y-ambiguous claim | **Retracted** |
| Pre-flash gate list | Updated in `WP2B_C_HARDWARE_GATES.md` |

## HSE / MCU / recovery (unchanged)

No new physical HSE, option-byte, or DFU evidence. UID/board identity reconfirmed via MSP.

## Safety compliance

- MSP read allowlist only  
- No CLI config mutation; no DFU/flash  
- No ArduPilot source/hwdef edits in this correction  
- `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.serena/` unstaged  

## Documents

| File | Topic |
| ---- | ----- |
| `WP2B_C_SENSOR_ORIENTATION.md` | Six-face table + corrected verdict |
| `WP2B_C_FRAME_RECONCILIATION.md` | BF vs AP axes, MSP path, ROLL_180 |
| `WP2B_C_HARDWARE_GATES.md` | Remaining flash conditions |
| `WP2B_C_FINAL_REPORT.md` | This status block |
