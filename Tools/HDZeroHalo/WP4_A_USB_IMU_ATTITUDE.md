# WP4-A: USB IMU & attitude qualification

Date: 2026-10-21. Read-only hardware test after WP3-K. No flash, ARM, motors,
calibration, or parameter writes.

Full report (in-repo copy): `evidence/wp4-a/WP4_A_REPORT.md`  
External original (unmodified):
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp4-a-usb-imu-attitude/WP4_A_REPORT.md`  
Hash index: `evidence/EXTERNAL_EVIDENCE.md`

```text
WP4_A_RESULT          = PASS
ROLL_DIRECTION        = PASS
PITCH_DIRECTION       = PASS
LEVEL_ATTITUDE        = PASS
PREARM_STATUS         = FAIL_FRAME_CLASS_ZERO
HARDWARE_FLASH_ALLOWED = NO
```

USB=aft reference redo: flat AccZ≈−1 g; right/left roll ±90° with AccY sign
flip; nose up/down pitch ±80° with AccX sign flip. Gyro/accel healthy. Mag
unhealthy; no baro. Next: set `FRAME_CLASS` (authorized param change), then
re-check prearm on USB bench.
