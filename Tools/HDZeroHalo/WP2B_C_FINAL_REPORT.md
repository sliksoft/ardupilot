# WP2B_C_FINAL_REPORT — sensor orientation & hardware flash gates

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `bb0662895b1095453d881484fbef7f2222bd17be`  
**Method:** read-only MSP on live Halo (`/dev/ttyACM0` via usbipd→WSL2); prior WP2A / WP2B-A / WP2B-B docs  
**Policy:** no flash, DFU, CLI `set`/`save`, calibration, GPIO/PINIO, motors, or ArduPilot source edits  

Evidence: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-c/`  
Detail: `WP2B_C_SENSOR_ORIENTATION.md`, `WP2B_C_HARDWARE_GATES.md`

## Main conclusion

**On this ICM42688P Halo, six-face MSP accelerometer data prove MSP X = forward (USB aft) and Z = up (component side). Y versus board-right is ambiguous (measured opposite to the assumed right). That is not enough evidence to change ArduPilot’s ICM `ROTATION_NONE`. Physical HSE, package/option bytes, PE3/9V, ADC calibration, AP DShot, and DFU recovery remain unproved. First ArduPilot flash is still forbidden.**

## Status block

```text
WP2B_C_STATUS = PASS_ORIENTATION_PARTIAL_GATES

CONNECTION = PASS (/dev/ttyACM0 0483:5740 HDZERO_HALO)
READ_ONLY = YES
FIRMWARE_FLASHED = NO
CONFIG_CHANGED = NO
MSP_USED = YES (API 1.48; RAW_IMU only + identity GETs)

MCU = STM32H743xx
MCU_ID = 004000383533510f39303730
BF_VERSION = 2026.6.2 (e0b7bb0) MSP 1.48
BF_TARGET = HDZERO_HALO / HDZO
IMU = ICM42688P (unchanged from WP2B-B)

SIX_FACE_ACC = COMPLETE
  X_FORWARD_USB_AFT = MATCH
  Z_UP_COMPONENTS = MATCH
  Y_BOARD_RIGHT = AMBIGUOUS
AP_ICM_ROTATION = RETAIN_ROTATION_NONE
ORIENTATION_HWDEF_CHANGE = NOT_INDICATED

HSE_PHYSICAL = STILL_UNPROVED (CLK=480MHz software-reported only)
MCU_PACKAGE_OPTBYTES_ROM = STILL_UNPROVED
DFU_RECOVERY = DOCUMENTED_UNTESTED
PE3_9V = STILL_UNPROVED
VBAT_IBATA_CAL = STILL_UNPROVED
AP_DSHOT_HW = STILL_UNPROVED
EXTERNAL_BARO = REQUIRED_FOR_FLIGHT_NOT_FITTED

HARDWARE_FLASH_ALLOWED = NO

HEAD_SHA = ca619b8175d2b682ed2d34ba0c44d48d80978b36
PUSH_STATUS = PUSHED_origin_board_hdzero-halo
NEXT_ACTION =
  Optional: photo IMU/silk for Y confirmation; crystal photo/scope;
  keep BF archive; human gate before any flash — do not start WP3 automatically
```

## What this WP closed

| Item | Result |
| ---- | ------ |
| MSP identity without config change | PASS — same UID/target as WP2B-B |
| Live Acc/Gyro stream | PASS — AccZ≈+1 g at rest top-up; gyro quiet |
| Absolute Acc axes (X,Z) | MATCH USB-aft / components-up |
| Absolute Acc Y vs silk right | AMBIGUOUS |
| ICM `ROTATION_NONE` change needed? | **No confident bug shown** |
| Concrete pre-flash gate list | `WP2B_C_HARDWARE_GATES.md` |

## HSE / MCU / recovery (read-only follow-up)

| Topic | Update in WP2B-C |
| ----- | ---------------- |
| HSE | No new physical proof. Live BF still reports 480 MHz SYSCLK; USB uses BF HSI48 path so enumeration ≠ crystal proof (WP2B-A). AP remains more HSE-sensitive for USB. |
| MCU | UID + STM32H743 / HDZERO_HALO / HDZO reconfirmed via MSP board info. Package marking, flash option bytes, ROM bootloader version still unread. |
| Recovery | No DFU attempted. OEM BOOT procedure and AP/BF layout conflict unchanged; BF 2026.6.2 dump already archived in WP2B-B. |

## Safety compliance

- Only MSP read allowlist (identity + `MSP_RAW_IMU`)  
- No CLI `#` session for config; no `set`/`save`/`defaults`/`bl`/`dfu`  
- No motor, ESC, LiPo, or PINIO switching  
- No ArduPilot hwdef / driver edits  
- Local `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.serena/` left unstaged  

## Documents

| File | Topic |
| ---- | ----- |
| `WP2B_C_SENSOR_ORIENTATION.md` | Six-face data vs `ROTATION_NONE` |
| `WP2B_C_HARDWARE_GATES.md` | Remaining flash conditions |
| `WP2B_C_FINAL_REPORT.md` | This status block |
