# PROJECT_SCOPE — HDZero Halo FC / ArduCopter

**Work package:** WP0 (foundation)  
**Date:** 2026-10-18  
**Base commit:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`  
**Branch:** `board/hdzero-halo`

## Mission

Produce an official, maintainable ArduCopter board port for the HDZero Halo FC
(STM32H743), following ArduPilot’s normal ChibiOS hwdef methodology and reusing
existing drivers. This is **not** a Betaflight clone, a new flight stack, or a
VliegAI-specific fork of vehicle control logic.

## In scope

- STM32H743 + ChibiOS HAL (`AP_HAL_ChibiOS`)
- Board hwdef / bootloader hwdef / defaults / board ID registration
- IMU support via existing Invensense / Invensensev3 drivers (MPU6000 and/or
  ICM42688P, depending on Halo hardware variant)
- Four motor outputs with DShot300 and DShot600
- Bidirectional DShot where pin/timer/DMA allow
- ESC RPM telemetry (bidir DShot and/or UART ESC telemetry)
- CRSF / onboard ELRS receiver wiring via existing RC protocols
- HDZero MSP DisplayPort OSD via existing `AP_MSP` / `AP_OSD_MSP_DisplayPort`
- UART, SPI, I²C, ADC as exposed by the Halo schematic
- Battery voltage/current sensing
- 16 MB SPI flash logging (`HAL_LOGGING_DATAFLASH_ENABLED`)
- Buzzer, LED, switchable 9V rail
- USB, bootloader, MAVLink
- External GPS, compass, barometer (probe / UART / I²C)
- Standard ArduCopter modes and failsafes (unchanged vehicle code)

## Out of scope (explicit non-goals)

- Rewriting or “improving” ArduCopter control algorithms for this board
- Porting Betaflight configs as a flight stack
- Flashing hardware, DFU writes, motor/ESC live tests during foundation WPs
  without a dedicated hardware validation plan
- VliegAI product-specific features unrelated to a standard board port
- Upstream PR until the port is reviewed and tested on hardware

## Status taxonomy

| Tag | Meaning |
|-----|---------|
| **SUPPORTED** | Confirmed present in existing ArduPilot code / drivers |
| **NEEDS_CONFIG** | Requires Halo hwdef / defaults / pin mapping only |
| **NEEDS_DRIVER** | Needs new or extended driver work beyond hwdef |
| **HARDWARE_LIMITATION** | Physical board constraint |
| **UNKNOWN** | Insufficient evidence (schematic / BOM / pinout) |
| **TESTED** | Validated with reproducible evidence (logs, photos, scripts) |

Nothing is marked **TESTED** without reproducible evidence.

## Methodology

1. Reuse closest supported H743 boards as templates (see
   `WP1_REFERENCE_INVENTORY.md`).
2. Add `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/` (name TBD in WP1) with
   `hwdef.dat`, `hwdef-bl.dat`, optional `defaults.parm`.
3. Register `APJ_BOARD_ID` in `Tools/AP_Bootloader/board_types.txt`.
4. Build bootloader + ArduCopter; validate on hardware in later WPs.

## WP0 boundary

WP0 covers environment, source checkout, toolchain, reference build, and
documentation only. **No Halo board definition is implemented in WP0.**
