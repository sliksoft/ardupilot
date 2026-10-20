# WP3-K: Production ArduPilot first boot

Date: 2026-10-21. AI-assisted execution of the corrected single-session ROM-DFU
plan. **One hardware flash trial.** No rebuild, commit, push or merge.

Full report (in-repo copy): `evidence/wp3-k/WP3_K_REPORT.md`  
External original (unmodified):
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-k-production-first-boot/WP3_K_REPORT.md`  
Hash index: `evidence/EXTERNAL_EVIDENCE.md`

```text
PREFLIGHT                          = PASS
BACKUP_VERIFIED                    = PASS
SECTOR_ERASE                       = PASS_SECTORS_0_TO_10
BOOTLOADER_PROGRAMMING             = PASS
ARDUCOPTER_PROGRAMMING             = PASS
FULL_FLASH_READBACK                = PASS
PARAMETERS_PRESERVED_PREBOOT       = PASS
NORMAL_USB_ENUMERATION             = PASS_1209_5741_COM14_HDZeroHalo
MAVLINK_HEARTBEAT                  = PASS_QUADROTOR_ARDUPILOTMEGA
MISSION_PLANNER_CONNECTION         = PASS_MAVLINK_GCS_COM14_MP_INSTALLED
STARTUP_DIAGNOSTICS                = PASS_WITH_EXPECTED_BENCH_LIMITS
RECOVERY_STATUS                    = PRODUCTION_LIVE_NO_ROLLBACK
HARDWARE_FLASH_ALLOWED             = EXPIRED
```

## What was programmed

WP3-J images only, same uninterrupted ROM-DFU session:

- BL `4f92d710…` @ `0x08000000` (sector 0)
- App `ec4e56ca…` @ `0x08020000` (sectors 1–10 erased first)
- Sectors 11–15 preserved (byte-verified preboot)

## First cold boot

USB product `HDZeroHalo` on COM14. MAVLink2 HEARTBEAT ~1 Hz, vehicle
QUADROTOR / ArduPilot, STABILIZE, STANDBY. Gyro/accel healthy on USB bench;
mag/battery unhealthy; no baro present (expected). No arm/motor/flight tests.

## ECC caveat

Production bootloader ECC recovery may later erase flash sectors. Preboot
parameter preservation does not survive such a recovery event.
