# WP4-C: Full FC USB/MAVLink inventory

Date: 2026-10-21. Read-only MAVLink2 inventory after WP4-B. No flash, ARM,
motors, calibration, or parameter writes in this session.

Full report and param dump:
`evidence/wp4-c/WP4_C_REPORT.md`, `evidence/wp4-c/all_params.csv` (1195 params).

External original (unmodified):
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp4-c-fc-usb-inventory/`

```text
WP4_C_RESULT                   = COMPLETE
PARAMS_RECEIVED                = 1195/1195
FIRMWARE                       = ArduCopter V4.8.0-dev (c1a1fc2d)
BOARD                          = HDZeroHalo board_id=1414
FRAME                          = QUAD/X (FRAME_CLASS=1 FRAME_TYPE=1)
MOTORS                         = DShot300 on outputs 1-4 (MOT_PWM_TYPE=5)
INTERNAL_ERRORS                = NONE (errors_comm/count*=0)
HARDWARE_FLASH_ALLOWED         = NO
```

## Highlights

- USB `1209:5741` COM14; HEARTBEAT QUADROTOR / ArduPilot STANDBY
- Gyro/accel healthy; ICM fast sampling 2 kHz; mag/baro/RC/pack absent as expected
- PreArms: RC not found, Compass 1 not healthy, Battery low voltage failsafe
- Firmware SHA256 of flashed app: `ec4e56ca…` (WP3-K staging)

See `evidence/EXTERNAL_EVIDENCE.md` for the full hash index and exclusions.
