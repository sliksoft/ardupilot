# WP4-C — HDZero Halo full USB/MAVLink inventory

**MODE:** READ-ONLY
**HARDWARE_FLASH_ALLOWED:** NO
**Date:** 2026-10-21
**Port:** Windows COM14 — USB `1209:5741` (ArduPilot / HDZeroHalo)
**Result:** COMPLETE — stop for overleg

---

## 1. Method

- Mission Planner was not holding COM14 (`COM14=FREE` preflight).
- Read-only MAVLink2 client: GCS heartbeats + `PARAM_REQUEST_LIST` / `PARAM_REQUEST_READ` + `MAV_CMD_REQUEST_MESSAGE` (info only) + `LOG_REQUEST_LIST`.
- **Not used:** `PARAM_SET`, arm/reboot/calibrate, `SET_MESSAGE_INTERVAL`, flash/erase.
- Raw frames: `raw/frames.hexl` (+ `frames2`, `frames3`); decoded: `raw/all_params.csv`, `raw/inventory.json`.

---

## 2. Measured on hardware (USB/MAVLink)

### Identity / firmware

| Field | Value |
|---|---|
| STATUSTEXT | `ArduCopter V4.8.0-dev (c1a1fc2d)` |
| ChibiOS | `9aebaf4a` |
| Board | `HDZeroHalo 00400038 3533510F 39303730` |
| AUTOPILOT_VERSION | flight 4.8.0.0; custom `c1a1fc2d`; `board_version>>16` = **1414** |
| HEARTBEAT | type=QUADROTOR (2), autopilot=ArduPilot (3), system_status=STANDBY (3), custom_mode=0 (Stabilize) |
| USB | `1209:5741` on COM14 |

### System health (`SYS_STATUS`)

| Sensor | Present | Enabled | Health |
|---|---|---|---|
| Gyro / Accel | yes | yes | **yes** |
| Mag | yes* | yes* | **no** |
| Baro | no | no | no |
| GPS / RC | no | no | no |
| Battery | no | no | no |
| AHRS / attitude stab. | yes | yes | yes |
| PreArm bit (health) | — | — | true (bit set; checks still failing — see STATUSTEXT) |

\*Mag marked present/enabled (compass feature on) but no device / unhealthy.

- CPU load: **139** (1.39%)
- `errors_comm` / `errors_count1..4`: **0**
- Battery telemetry without LiPo: ~**1 mV**, current ~10.63 A (ADC noise / open sense — not meaningful)

### PreArm / STATUSTEXT (unique)

1. `PreArm: RC not found`
2. `PreArm: Compass 1 not healthy`
3. `PreArm: Battery 1 low voltage failsafe`
4. `RCOut: DS300:1-4 PWM:5`
5. `IMU0: fast sampling 2.0kHz/2.0kHz`
6. `Frame: QUAD/X`

### IMU / AHRS / EKF (level, USB-powered bench)

| Signal | Summary |
|---|---|
| SCALED_IMU Acc | X≈0.12 g, Y≈0.06 g, Z≈−0.99 g (FRD level) |
| Gyro | near zero, low noise |
| IMU temperature | ≈ **28.7 °C** (msg units cdeg) |
| AHRS_ORIENTATION | **0** |
| AHRS_EKF_TYPE / EK3_ENABLE | **3** / **1** |
| EK3_IMU_MASK | **1** (IMU0 only) |
| EKF flags | 167 — attitude + horiz/vert velocity/pos modes active; compass variance 0 |

### Memory / scheduler / logs

| Item | Value |
|---|---|
| SCHED_LOOP_RATE | **400** Hz |
| MEMINFO freemem32 | **707248** bytes |
| LOG_BACKEND_TYPE | **4** |
| LOG_DISARMED | **0** |
| LOG_REQUEST_LIST | **num_logs = 0** (no stored logs) |

### RC / SERVO outputs (DISARMED, no ESCs)

| Output | SERVO*_FUNCTION | Runtime |
|---|---|---|
| 1–4 | 33–36 (Motor1–4) | `servo*_raw=1000`; DShot300 per STATUSTEXT |
| 5 | **0** (Disabled) | `servo5_raw=0`; pad is PWM per hwdef |
| 6–16 | 0 | idle |

RC: `chancount=0`, all channels 0, `rssi=255` (no receiver).

### Key parameters (live)

| Param | Live | Notes |
|---|---|---|
| FRAME_CLASS | **1** | Quad — matches user check |
| FRAME_TYPE | **1** | X — matches user check; **≠** hwdef default 12 |
| MOT_PWM_TYPE | **5** | DShot300 |
| SERVO1..4_FUNCTION | 33..36 | Motor1–4 |
| SERVO5_FUNCTION | 0 | Unused PWM |
| AHRS_ORIENTATION | 0 | Board rotation is hwdef `ROTATION_ROLL_180` |
| BATT_MONITOR | 4 | Analog voltage+current |
| BATT_VOLT_PIN / CURR_PIN | 10 / 12 | Match hwdef |
| BATT_VOLT_MULT / AMP_PERVLT | 11 / 100 | Match hwdef |
| COMPASS_ENABLE / USE | 1 / 1 | No `COMPASS_DEV_ID` (0) |
| SERIAL0_PROTOCOL | 2 | MAVLink2 USB |
| SERIAL1_PROTOCOL | 23 | RCIN (ELRS) |
| SERIAL2/3/6/7 | -1 | None |
| SERIAL4_PROTOCOL | 16 | ESC telemetry |
| SERIAL5_PROTOCOL | 42 | MSP DisplayPort |
| OSD_TYPE | 5 | MSP DP |
| BARO_PROBE_EXT | 1030 | Ext probe mask; no baro fitted |
| INS_USE | 1 | IMU0 used |
| FORMAT_VERSION | 120 | |

Full dump: `raw/all_params.csv` (1195 params).

---

## 3. Firmware / hwdef / ELF comparison

Artifacts (WP3-K flash source):

| Artifact | SHA256 |
|---|---|
| `evidence/wp3-k-…/staging/arducopter.bin` | `ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7` |
| `build/wp3-j-app/HDZeroHalo/bin/arducopter.bin` | same |
| `evidence/wp3-j-…/after/arducopter.elf` | `5d9af4f77d2fc621b31efeef5d4cffccff1895adff5dbfdca007fe7573acef62` |

ELF/strings match live STATUSTEXT: `ArduCopter V4.8.0-dev (c1a1fc2d)`, `HDZeroHalo`, ChibiOS `9aebaf4a`.
Generated `hwdef.h`: `HAL_USB_VENDOR_ID 0x1209`, `HAL_USB_PRODUCT_ID 0x5741`, `CHIBIOS_BOARD_NAME "HDZeroHalo"`.
`board_types.txt`: `AP_HW_HDZERO_HALO = 1414` — matches AUTOPILOT_VERSION.

| Check | Live | Source expectation | Verdict |
|---|---|---|---|
| ICM42688P + ROLL_180 | IMU0 2 kHz; FRD AccZ≈−1g; AHRS_ORIENTATION=0 | hwdef `IMU Invensensev3 SPI:icm42688_1 ROTATION_ROLL_180` | **PASS** |
| FRAME_CLASS=1 | 1 | User expect 1; code default 0 | **PASS** (runtime) |
| FRAME_TYPE=1 | 1 | User expect 1; **hwdef default 12** | **PASS user / DIFF hwdef** |
| DShot300 on 1–4 | MOT_PWM_TYPE=5; DS300:1–4 | `defaults.parm` + TIM3 PWM1–4 | **PASS** |
| PWM out 5 | SERVO5_FUNCTION=0; PWM:5 in RCOut | hwdef `PA10 … PWM(5) NODMA` | **PASS** (unused) |
| UART/SPI/I2C/USB | SERIAL* as above; USB OK | hwdef SERIAL_ORDER / SPI1 IMU / SPI2 flash / I2C1 | **PASS** (logical) |
| Battery cfg | monitor 4, pins 10/12, scales 11/100 | hwdef HAL_BATT_* | **PASS** cfg |
| Compass | enabled, no device, unhealthy | probe-only, no onboard mag | **PASS** expected |
| Internal faults | errors_*=0 | — | **none reported** |

Detail matrix: `compare/hwdef_vs_live.json`.

### Note vs WP4-A

WP4-A saw `FRAME_CLASS=0`, `FRAME_TYPE=12` and PreArm `FRAME_CLASS`. Live now is **1 / 1** and `Frame: QUAD/X` with no FRAME PreArm. Parameters changed on the vehicle after WP4-A (not by this WP4-C session). Hwdef still defaults `HAL_FRAME_TYPE_DEFAULT 12`.

---

## 4. Cannot test without external hardware

| Item | Why blocked |
|---|---|
| ESC / DShot bidirectional / motor spin | No ESCs or motors |
| RC link / failsafe / modes via stick | No receiver |
| Battery voltage/current calibration | No LiPo on sense |
| Compass heading / cal | No external mag on I2C1 |
| Baro altitude | No baro on board or I2C |
| GPS / position modes | No GPS |
| VTX 9V rail (PE3) | Electrical unverified; not exercised |
| Dataflash write endurance / log download of flights | `num_logs=0`, LOG_DISARMED=0 |
| ARM / flight PreArm clearance | Would require suppressing checks or fitting hardware — **forbidden** here |

---

## 5. Evidence layout

```
evidence/wp4-c-fc-usb-inventory/
  STATUS.txt
  report/WP4_C_REPORT.md
  raw/frames.hexl frames2.hexl frames3.hexl
  raw/all_params.csv all_params.json inventory.json
  raw/statustexts.json msg_type_counts.json
  compare/hwdef_vs_live.json firmware_artifacts.json
  logs/com_preflight.txt capture_meta*.txt
```

Windows staging mirror: `C:\Users\sande\HDZeroHalo_WP4C\raw\`

---

## 6. Verdict

Live Halo on COM14 matches the WP3-J/K HDZeroHalo image (`c1a1fc2d`, board 1414): ICM path healthy, DShot300 on motors 1–4, PWM5 present unused, UART/USB/batt **configuration** aligned with hwdef.
`FRAME_CLASS=1` / `FRAME_TYPE=1` match the requested check (and differ from hwdef’s default FRAME_TYPE 12).
Open PreArms are exactly those expected with no RC, mag, or pack. No MAVLink error counters.

**HARDWARE_FLASH_ALLOWED remains NO. Stop for overleg.**
