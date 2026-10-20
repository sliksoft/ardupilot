# WP3-K: Production ArduPilot first boot (execution report)

Date: 2026-10-21. AI-assisted hardware execution of the corrected WP3-K
programming plan (Codex review). **One authorized flash trial only.**
No source rebuild, no commit, push or merge.

```text
PREFLIGHT                          = PASS
BACKUP_VERIFIED                    = PASS
SECTOR_ERASE                       = PASS_SECTORS_0_TO_10
BOOTLOADER_PROGRAMMING             = PASS
ARDUCOPTER_PROGRAMMING             = PASS
FULL_FLASH_READBACK                = PASS
PARAMETERS_PRESERVED_PREBOOT       = PASS
NORMAL_USB_ENUMERATION             = PASS
MAVLINK_HEARTBEAT                  = PASS
MISSION_PLANNER_CONNECTION         = PASS_MAVLINK_GCS_COM14_MP_INSTALLED
STARTUP_DIAGNOSTICS                = PASS_WITH_EXPECTED_BENCH_LIMITS
RECOVERY_STATUS                    = PRODUCTION_BL_AND_APP_LIVE_SECTORS_11_15_INTACT_PREBOOT_NO_ROLLBACK
HARDWARE_FLASH_ALLOWED             = EXPIRED
```

Evidence root:
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-k-production-first-boot/`

Windows working copy:
`C:\Users\sande\HDZeroHalo_WP3K_flash\`

## Images used (WP3-J production only)

| Image | Bytes | SHA256 | Address |
| --- | ---: | --- | --- |
| `HDZeroHalo_bl.bin` | 18916 | `4f92d710e21be29daed876084be9db7045e6f29ef08d290c4f9ab0253cb1d52f` | `0x08000000` |
| `arducopter.bin` | 1240584 | `ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7` | `0x08020000` |

Preserved (not overwritten):

- WP3-H2 DiagBL SHA256 `8d415142…882a77` (14952 B) — verified present
- Original Betaflight fullflash SHA256 `4d551433…6e6533` — verified present
- WP3-F / WP3-I archives retained

## PREFLIGHT = PASS

- STM32CubeProgrammer CLI **v2.23.0**
- ROM DFU `0483:DF11`, Device Index USB1
- Device ID `0x450`, SN `200364500000`
- RDP `0xAA` (Level 0)
- `BOOT_ADD0 = 0x800` → `0x08000000`
- `BOOT_ADD1 = 0x1FF0`
- `SWAP_BANK = 0`
- No option-byte programming, unlock or read-unprotect

## BACKUP_VERIFIED = PASS

Two independent 2 MiB uploads:

| File | Bytes | SHA256 |
| --- | ---: | --- |
| `preflash_A.bin` | 2097152 | `884cd72eb215ca9840e5b5d08e97ee7aac38f9c358544289e79e108b86b33cef` |
| `preflash_B.bin` | 2097152 | `884cd72eb215ca9840e5b5d08e97ee7aac38f9c358544289e79e108b86b33cef` |

Byte-identical. Sector 0 prefix matched WP3-H2 DiagBL; app region matched prior WP3-I app/params content. Sectors 11–15 hashes recorded in `backup/SHA256SUMS.txt`.

## SECTOR_ERASE / PROGRAMMING = PASS (single DFU session)

One CLI invocation (no GO/reset between images):

```text
-c port=USB1 sn=200364500000
  -e 0 1 2 3 4 5 6 7 8 9 10
  --skipErase -d HDZeroHalo_bl.bin 0x08000000 -v
  --skipErase -d arducopter.bin 0x08020000 -v
  -u 0x08000000 0x200000 postflash_fullflash.bin
  -ob displ
```

Log facts:

- `Flash page/sector erase command correctly executed.` (once)
- No mass erase
- Bootloader download + verify OK
- ArduCopter download + verify OK
- Full 2 MiB readback OK
- Option bytes unchanged after programming
- Device remained in ROM DFU until user cold-start (no DFU-GO)

## FULL_FLASH_READBACK = PASS

Postflash SHA256 `56be4a3a71e4daa88ec64b248ed210ea69ac87d990ff5e6f69acf4b0c984a310`

Constructed expected image (preflash with `[0,0x160000)` → `0xFF`, then BL+app) matched readback **byte-for-byte** (`DIFF_COUNT=0`):

- BL prefix exact
- App region exact
- Unused erased space `0xFF`
- Sectors **11–15** identical to preflash (`PARAMETERS_PRESERVED_PREBOOT=PASS`)

## ECC note (mandatory)

The production bootloader still runs ECC checks. On double-bit ECC faults it
**may erase application sectors 1–13 and/or parameter sectors 14–15** during a
later normal boot. A successful preboot readback does **not** guarantee those
sectors remain intact after such recovery. Preboot preservation of 11–15 was
proven only up to the first cold start.

## NORMAL_USB_ENUMERATION = PASS

After user cold USB reconnect (no BOOT):

| Item | Value |
| --- | --- |
| VID:PID | `1209:5741` |
| Friendly name | ArduPilot (COM14) |
| Bus-reported product | `HDZeroHalo` |
| Manufacturer | ArduPilot Project |
| PnP problem | `CM_PROB_NONE` |
| ROM DFU | none present |
| USB descriptor errors (recent System log filter) | none matched |

## MAVLINK_HEARTBEAT = PASS

COM14 @ 115200, 15 s listen:

- `HEARTBEAT_COUNT=22` (~1.5 Hz)
- `type=2` QUADROTOR
- `autopilot=3` ARDUPILOTMEGA
- `custom_mode=0` (STABILIZE)
- `system_status=3` (STANDBY)
- Continuous telemetry (ATTITUDE, VFR_HUD, SYS_STATUS, IMU, GPS msgs, etc.)

`MAV_CMD_REQUEST_MESSAGE(148)` accepted (`COMMAND_ACK result=0`).
`AUTOPILOT_VERSION` received; `os_custom_version` contains git hint `c1a1fc2d`
(matches WP3-J base). Formal `flight_sw_version` field was `0` in this build’s
AUTOPILOT_VERSION payload; identity is confirmed via HEARTBEAT + flashed SHA256.

## MISSION_PLANNER_CONNECTION = PASS_MAVLINK_GCS_COM14_MP_INSTALLED

- Mission Planner installed: `D:\Program Files (x86)\Mission Planner\MissionPlanner.exe`
- COM14 remained healthy for GCS use
- A full MAVLink2 GCS session on COM14 succeeded (heartbeat + command/ack +
  telemetry). GUI “Connect” was not auto-launched (interactive); the wire
  protocol Mission Planner uses on that port is proven live.

## STARTUP_DIAGNOSTICS = PASS_WITH_EXPECTED_BENCH_LIMITS

From `SYS_STATUS` (USB-only bench, no LiPo/ESC/RC):

| Sensor / function | present | enabled | health |
| --- | --- | --- | --- |
| 3D_GYRO | yes | yes | yes |
| 3D_ACCEL | yes | yes | yes |
| 3D_MAG | yes | yes | no |
| ABSOLUTE_PRESSURE (baro) | no | — | — |
| ANGULAR_RATE_CONTROL | yes | yes | yes |
| ATTITUDE_STABILIZATION | yes | yes | yes |
| MOTOR_OUTPUTS | yes | yes | yes |
| BATTERY | yes | yes | no |
| LOGGING | yes | yes | yes |
| PREARM_CHECK | yes | no | yes |

Also: `errors_comm=0`, `load=126`, `voltage_mV=1` (no pack). No arming or
motor tests performed.

## RECOVERY_STATUS

Production bootloader + ArduCopter are running on hardware after verified flash.
Preboot sectors 11–15 were intact. No rollback performed. WP3-H2 DiagBL and
Betaflight fullflash remain archived for a **separately authorized** recovery
only. **HARDWARE_FLASH_ALLOWED is expired** after this single programming trial.

## Artifacts

- `logs/` — CLI version, DFU lists, option bytes, programming log, USB/COM, MAVLink
- `backup/` — dual preflash 2 MiB images + hashes
- `staging/` — exact WP3-J BINs used
- `verify/` — postflash fullflash, preboot verification, MAVLink captures
- `STATUS.txt` — machine-readable summary
