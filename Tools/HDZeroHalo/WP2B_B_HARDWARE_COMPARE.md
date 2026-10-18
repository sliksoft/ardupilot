# WP2B_B_HARDWARE_COMPARE — live Halo vs ArduPilot `HDZeroHalo`

**Date:** 2026-10-18  
**AP path:** `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/`  
**No hwdef changes in this WP.**

Evidence classes used below:

| Tag | Meaning |
| --- | ------- |
| LIVE | Read from this FC via CLI |
| BF_CFG | Installed Betaflight configuration |
| AP | Current ArduPilot board definition |
| INFERRED | Logical conclusion, not measured |
| UNPROVED | Still needs physical / other test |

## 1. MCU identification

| | Live FC | AP hwdef |
| - | ------- | -------- |
| Class | STM32H743xx LIVE | `MCU STM32H7xx STM32H743xx` |
| UID | `004000383533510f39303730` LIVE | n/a |
| Package marking | UNPROVED | — |
| Flash size class | BF config 128 KiB sector; SPI flash separate | `FLASH_SIZE_KB 2048` |

**Match:** MCU class. Package still unproved.

## 2. Betaflight version / target

| | Live |
| - | ---- |
| Target | HDZERO_HALO / HDZO |
| Version | **2026.6.2** (not factory 4.5.1) |
| Config rev | 3a406c5 |

AP port assumed OEM/BF pinmap from 4.5.1-era target — **pins still match**; installed firmware generation differs.

## 3. IMU SKU

| | Live | AP |
| - | ---- | -- |
| Detected | **ICM42688P** on GYRO_1 | Probes ICM+MPU on both CS |
| Active CS | **PB4** (+ EXTI PC13) | GYRO1_CS=PB4, GYRO2_CS=PB3 |
| GYRO_2 | Present in resources, **disabled** | Dual probe OK |

**Match:** ICM SKU on PB4 aligns with closed PR#835 inference and AP `icm42688_1` first probe. MPU6000 not present on this unit.

## 4. Sensor orientation

| | Live BF_CFG | AP |
| - | ----------- | -- |
| Board align | roll/pitch/yaw = 0 | ICM `ROTATION_NONE`; MPU `ROLL_180_YAW_90` (relative cancel) |
| Absolute mount | UNPROVED | UNPROVED |

BF board align 0 does **not** prove PCB package orientation. No six-face test performed (USB-powered FC only).

## 5. Clock information

| | Live | AP |
| - | ---- | -- |
| Reported SYSCLK | 480 MHz | `MCU_CLOCKRATE_MHZ 480` |
| Oscillator Hz | Not measured; BF assumes HSE8 in build | `OSCILLATOR_HZ 8000000` provisional |
| Vref | 3.29 V LIVE | — |

**Software consistency** with HSE8/480 path; **physical crystal still UNPROVED**.

## 6. Flash / storage

| | Live | AP |
| - | ---- | -- |
| SPI flash | W25Q128 JEDEC `0xEF4018` 16 MiB | `SPIDEV dataflash` SPI2 PB12 |
| Internal BF config | 4487 / 131072 B used | Different layout (AP params pages 14/15) |

**Match** for external flash part family and CS.

## 7. UARTs / MSP DisplayPort

| Role | Live | AP |
| ---- | ---- | -- |
| CRSF / ELRS | UART1 CRSF | SERIAL1 RCIN |
| MSP DP | UART5 function 131073; OSD MSP | SERIAL5 MSP DisplayPort, OSD_TYPE 5 |
| ESC telem HW | UART4 RX A01 mapped; function 0 | SERIAL4 ESCTelemetry |
| Free UARTs | 2,7,8 | Same pins |

**Match** for primary FPV roles. Live UART4 protocol not enabled (no ESC).

## 8. PE3 / PINIO

| | Live | AP |
| - | ---- | -- |
| PINIO resource | **NONE** (not E03) | `PE3 VTX_PWR OUTPUT LOW` |
| pinio_box | 255 (disabled) | No RELAY auto-on |

**Difference:** AP reserves PE3 as GPIO held LOW; this BF config does **not** currently map PINIO to PE3. OEM docs still describe enabling it. Electrical 9V behaviour UNPROVED.

## 9. Battery ADC

| | Live BF_CFG | AP |
| - | ----------- | -- |
| Pins | C00/C01/C02 | PC0/PC1/PC2 |
| VBAT | 110 / 10 / 1 | `HAL_BATT_VOLT_SCALE 11.0` |
| Current | ibata 100, offset 0 | `HAL_BATT_CURR_SCALE 100.0` |
| Calibration | UNPROVED (no LiPo) | UNPROVED |

**Nominal match.** Not a DMM calibration.

## 10. DShot / motors

| | Live BF_CFG | AP |
| - | ----------- | -- |
| Pins / TIM3 | C06–C09 CH1–4 | Same + BIDIR on CH1/CH3 |
| Path | Bitbang ON | Timer DMA / bdshot |
| Protocol | DSHOT300 | defaults.parm DShot300 |
| Bidir | ON | `HAL_WITH_BIDIR_DSHOT` path |

**Pin match.** Mechanism still different; no ESC connected → AP path untested; BF bidir flagged `DSHOT_TELEM` without ESCs.

## 11. Other

| Item | Live | AP |
| ---- | ---- | -- |
| Buzzer | D12 | PD12 inverted/active-high |
| Status LED | E02 | PE2 |
| LED strip | A10 | PA10 NODMA unsupported |
| I2C pads | B08/B09, 0 devices | External baro required |
| Name / rates / PID | Personalised “racer 5” | n/a |

## Summary matrix

| Topic | Verdict |
| ----- | ------- |
| MCU class / target name | MATCH |
| Pinmap vs hwdef | MATCH |
| IMU this unit | ICM42688P @ PB4 — supported by AP probe order |
| Installed BF version | NEWER than WP2B-A factory 4.5.1 baseline |
| PE3 PINIO | LIVE not configured; AP holds GPIO LOW |
| VBAT/current nominals | MATCH formulas |
| Absolute IMU / HSE crystal / 9V rail / ADC cal / AP DShot | STILL OPEN |
