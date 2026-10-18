# HARDWARE_REQUIREMENTS — HDZero Halo FC

**Work package:** WP0  
**Date:** 2026-10-18  
**Evidence note (WP1A):** Official Betaflight target
`configs/HDZO/HDZERO_HALO/config.h` and HDZero product/firmware docs supply the
intended pinmap (see `WP1A_PINMAP.md`). No public schematic was found; crystal
frequency and bootloader flash layout remain **UNKNOWN**. ArduPilot support
status is tracked in `PORT_STATUS.md`.

## Target MCU

| Item | Requirement | Status |
|------|-------------|--------|
| MCU | STM32H743 | Goal; **UNKNOWN** until Halo docs confirm package/rev |
| HAL | ChibiOS / `AP_HAL_ChibiOS` | **SUPPORTED** in tree |
| Flash (MCU) | Typically 2048 KB on H743 targets | **SUPPORTED** pattern on peer boards |
| Oscillator | External crystal (peer boards use 8 MHz) | **UNKNOWN** for Halo |

## Sensors / peripherals (goals)

| Function | Target | ArduPilot path | Halo evidence |
|----------|--------|----------------|---------------|
| Gyro/Accel A | MPU6000 | `IMU Invensense` | **UNKNOWN** (variant-dependent) |
| Gyro/Accel B | ICM42688P | `IMU Invensensev3` | **UNKNOWN** (variant-dependent) |
| Motors | 4× PWM/DShot | TIM PWM + DShot | **UNKNOWN** pins |
| DShot rates | 300 and 600 | `AP_Motors` MOT_PWM_TYPE | **SUPPORTED** in code |
| Bi-dir DShot | Where TIM/DMA allow | `BIDIR` in hwdef | **UNKNOWN** for Halo pins |
| ESC RPM | Bi-dir and/or UART telem | bdshot / `SerialProtocol_ESCTelemetry` | **UNKNOWN** |
| RC | CRSF / ELRS | `AP_RCProtocol_CRSF` | **UNKNOWN** UART |
| OSD | HDZero MSP DisplayPort | `SerialProtocol_MSP_DisplayPort` | **UNKNOWN** UART |
| Logging | 16 MB SPI flash | `HAL_LOGGING_DATAFLASH_ENABLED` | **UNKNOWN** part/bus |
| Power sense | V/I ADC | `HAL_BATT_*` | **UNKNOWN** scales/pins |
| 9V switch | GPIO / relay | `PINIO` / `RELAY` / `VPWR` pattern | **UNKNOWN** |
| Buzzer / LED | GPIO or TIM | `HAL_BUZZER_PIN`, notify LEDs | **UNKNOWN** |
| USB / BL | OTG + AP bootloader | `hwdef-bl.dat` | **UNKNOWN** DFU details |
| Ext GPS / mag / baro | UART + I²C probe | existing drivers | **UNKNOWN** connectors |

## Evidence still required before WP1 pin mapping

1. Official Halo schematic or annotated pinout (MCU pins for motors, SPI, UART).
2. BOM or silkscreen confirming IMU variant(s) and flash part.
3. Crystal frequency and any HSE/HSI constraints.
4. ELRS module interface (UART number, inverted TX/RX, pad names).
5. HDZero VTX / MSP DisplayPort UART assignment.
6. Battery sense divider and current shunt scale.
7. Bootloader / DFU / button recovery procedure from HDZero docs.

Until those exist, treat all Halo pin assignments as **UNKNOWN**. Do not invent
mappings from Betaflight targets without citing a primary source.
