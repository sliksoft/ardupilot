# WP1A_DRIVER_COMPATIBILITY — existing ArduPilot drivers vs Halo

**Date:** 2026-10-18  
**Tree:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`

No **TESTED** rows — research only. No new drivers identified as mandatory for the stated Halo feature set.

## IMU — MPU6000 and ICM42688P

| Item | Finding | Status |
|------|---------|--------|
| MPU6000 driver | `IMU Invensense` | SUPPORTED |
| ICM42688P driver | `IMU Invensensev3` | SUPPORTED |
| Bus | SPI1 PA5/6/7 | NEEDS_CONFIG |
| CS pins | PB4 (gyro1), PB3 (gyro2) | NEEDS_CONFIG |
| EXTI | PC13 / PA15 | Optional; many boards omit DRDY; Invensensev3 has no DRDY path |
| SKU reality | HDZ: **either** MPU6000 **or** ICM42688, not both fitted | HARDWARE note |
| CS ↔ SKU (inference) | ICM→PB4/PC13; MPU→PB3/PA15 (closed BF PR #835) | DER — probe both |
| One hwdef for both SKUs | Yes — probe both CS with both driver types (Lucid/Matek multi-probe pattern) | NEEDS_CONFIG |
| Rotation | EmuFlight CW0°; ArduPilot `ROTATION_*` | **UNKNOWN** until bench |

Example probe strategy (conceptual — not implemented in WP1A):

```text
SPIDEV mpu6000_1  SPI1 DEVID1 GYRO1_CS MODE3 1*MHZ 8*MHZ
SPIDEV icm42688_1 SPI1 DEVID1 GYRO1_CS MODE3 2*MHZ 16*MHZ
SPIDEV mpu6000_2  SPI1 DEVID2 GYRO2_CS MODE3 1*MHZ 8*MHZ
SPIDEV icm42688_2 SPI1 DEVID2 GYRO2_CS MODE3 2*MHZ 16*MHZ
IMU Invensense   SPI:mpu6000_1 …
IMU Invensensev3 SPI:icm42688_1 …
IMU Invensense   SPI:mpu6000_2 …
IMU Invensensev3 SPI:icm42688_2 …
```

## SPI flash logging — W25Q128FV

| Item | Finding | Status |
|------|---------|--------|
| JEDEC ID W25Q128 | `0xEF4018` / `0xEF7018` in `AP_Logger_Flash_JEDEC.cpp` L56–57, L153–154 | SUPPORTED |
| Enable | `HAL_LOGGING_DATAFLASH_ENABLED` + `SPIDEV dataflash` | NEEDS_CONFIG |
| Bus | SPI2, CS PB12 | NEEDS_CONFIG |
| Peer boards | FoxeerH743v1 L145–147; TMotorH743 L137–139; AnyleafH7 L104, L122 (W25Q64 there) | — |
| Full / wear | Block logger erase/full behaviour existing | SUPPORTED (generic) |
| New driver needed | No | — |

## ELRS / CRSF (Gemini on UART1)

| Item | Finding | Status |
|------|---------|--------|
| Protocol | `SerialProtocol_CRSF` / RCIN + `AP_RCProtocol_CRSF` | SUPPORTED |
| Pins | USART1 PB6/PB7 | NEEDS_CONFIG |
| Onboard RX | ESP32 Gemini; disable switch on board (HDZ) | HARDWARE note |
| Telemetry / failsafe | Existing CRSF stack | SUPPORTED / needs vehicle params |
| Stick menus for HDZero | ArduPilot DisplayPort + HDZero stick cmds (wiki) | SUPPORTED (generic) |

## HDZero MSP DisplayPort

| Item | Finding | Status |
|------|---------|--------|
| Protocol 42 | `SerialProtocol_MSP_DisplayPort` | SUPPORTED |
| Backend | `AP_OSD_MSP_DisplayPort.cpp` | SUPPORTED |
| Default UART | UART5 PC12/PD2 | NEEDS_CONFIG |
| OSD_TYPE | 5 | NEEDS_CONFIG (`HAL_OSD_TYPE_DEFAULT 5` as Anyleaf L121) |
| Analog OSD | None on Halo | HARDWARE_LIMITATION (by design) |
| Stick menu | Community/wiki support for HDZero | SUPPORTED (generic); TESTED only later |

## Battery / current / RSSI ADC

| Item | Finding | Status |
|------|---------|--------|
| Pins | VBAT PC0, CURR PC2, RSSI PC1 | NEEDS_CONFIG |
| Current scale | BF default 100 | NEEDS_CONFIG (start from 100) |
| Voltage scale | Not in BF config.h | **UNKNOWN** — measure / docs |
| Monitor type | Analog V+I | NEEDS_CONFIG `HAL_BATT_MONITOR_DEFAULT 4` |

## Buzzer / LED / 9V

| Item | Finding | Status |
|------|---------|--------|
| Buzzer PD12 inverted | GPIO + `HAL_BUZZER_PIN`; note inversion | NEEDS_CONFIG |
| Status LED PE2 | GPIO notify | NEEDS_CONFIG |
| LED strip PA10 | TIM1 CH3 PWM / scripted LED | NEEDS_CONFIG |
| 9V PE3 | Relay/PINIO pattern (Lucid `VPWR`) | NEEDS_CONFIG; polarity **UNKNOWN** |

## USB / MAVLink / GPS / compass / baro

| Item | Finding | Status |
|------|---------|--------|
| USB MAVLink | OTG1 | NEEDS_CONFIG |
| External GPS | UART2/7/8 pads | NEEDS_CONFIG |
| External compass/baro | I2C1 PB8/9 + probing | SUPPORTED / NEEDS_CONFIG |
| Onboard baro | Not in BF target | Likely absent — HARDWARE_LIMITATION or UNK |
| ESC passthrough | DShot/serial passthrough via existing AP tools | NEEDS_CONFIG + TEST later |

## New drivers required?

**None** identified for the mandatory Halo feature list, assuming JEDEC flash ID matches W25Q128 and IMUs are standard Invensense parts.

## Concurrent-feature conflicts (logical)

| Combo | Risk | Mitigation |
|-------|------|------------|
| bdshot + SPI logging + MSP DMA | DMA pressure | `DMA_NOSHARE`; configure-time check |
| LED strip DMA + TIM3 bdshot | Timer/DMA contention | LED `NODMA` |
| CRSF + MSP + GPS all active | UART count OK | Assign protocols in defaults.parm |
| Bi-dir DShot + UART ESC telem | Redundant | Prefer one RPM source |
