# PORT_STATUS — feature matrix

**Work package:** WP0 (no Halo firmware yet)  
**Date:** 2026-10-18  
**Base:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`

Status tags: SUPPORTED | NEEDS_CONFIG | NEEDS_DRIVER | HARDWARE_LIMITATION | UNKNOWN | TESTED

Nothing below is **TESTED** for Halo hardware.

| Feature | Status | Notes / evidence in tree |
|---------|--------|--------------------------|
| STM32H743 + ChibiOS | SUPPORTED | Many hwdefs, e.g. `TBS_LUCID_H7/hwdef.dat` L5 |
| MPU6000 driver | SUPPORTED | `IMU Invensense` — e.g. Lucid L209–210, MatekH743 L208 |
| ICM42688P driver | SUPPORTED | `IMU Invensensev3` — Lucid L207–208, TMotorH743 L149–153 |
| Four motor outputs | NEEDS_CONFIG | Pattern on GEPRC_TAKER_H743 L117–121, FoxeerH743v1 L128–131 |
| DShot300 / DShot600 | SUPPORTED | `AP_MotorsMulticopter` MOT_PWM_TYPE values 5/6 |
| Bidirectional DShot | NEEDS_CONFIG | Requires `BIDIR` + DMA; Lucid L145–154, MatekH743-bdshot L23–30; `HAL_WITH_BIDIR_DSHOT` via `chibios_hwdef.py` ~L2201 |
| ESC RPM (bdshot) | NEEDS_CONFIG | Same as bi-dir; hardware validation later |
| ESC UART telemetry | SUPPORTED / NEEDS_CONFIG | `SerialProtocol_ESCTelemetry` — Lucid L134–137 |
| CRSF / ELRS | SUPPORTED / NEEDS_CONFIG | `SerialProtocol_CRSF` / RCIN UART — `AP_RCProtocol_CRSF.cpp`; typical `SerialProtocol_RCIN` on RX UART |
| HDZero MSP DisplayPort | SUPPORTED / NEEDS_CONFIG | `SerialProtocol_MSP_DisplayPort` — Lucid L111–115; `AP_OSD_MSP_DisplayPort.cpp` |
| UART / SPI / I²C / ADC | NEEDS_CONFIG | Standard hwdef primitives; Halo pins UNKNOWN |
| Battery / current sense | NEEDS_CONFIG | `HAL_BATT_*` pattern — Lucid L68–81 |
| 16 MB SPI flash logging | SUPPORTED / NEEDS_CONFIG | `HAL_LOGGING_DATAFLASH_ENABLED` — SkystarsH7HD L28–29,62; FoxeerH743v1 L145–147; TMotorH743 L137–139 |
| Buzzer | NEEDS_CONFIG | GPIO buzzer — Lucid L161–163 |
| LED | NEEDS_CONFIG | GPIO notify — Lucid L89–96 |
| Switchable 9V | NEEDS_CONFIG | Lucid `VPWR` PC13 L178–183 / bootloader L51–52 |
| USB + MAVLink | SUPPORTED / NEEDS_CONFIG | OTG1 + serial order — Lucid L23–25,99 |
| Bootloader / safe recovery | NEEDS_CONFIG | `hwdef-bl.dat` patterns; Lucid BL enables DFU + SD flash L55–77 |
| External GPS | SUPPORTED / NEEDS_CONFIG | UART GPS protocol defaults — Lucid L106–109 |
| External compass | SUPPORTED / NEEDS_CONFIG | `AP_COMPASS_PROBING_ENABLED` — Lucid L201–205 |
| External / onboard baro | SUPPORTED / NEEDS_CONFIG | DPS310/BMP388 patterns — Lucid L218–219 |
| ArduCopter modes / failsafes | SUPPORTED | Unchanged vehicle code; not board-specific |
| Halo board hwdef | UNKNOWN | Not present; WP1+ |
| Halo on-hardware flight | UNKNOWN | No TESTED evidence |

## Summary for WP1

Almost all product goals map to **SUPPORTED** drivers plus **NEEDS_CONFIG**
hwdef work. No feature in this list currently requires a new sensor driver class
based solely on the stated goals. Pinout / BOM evidence is the blocking input.
