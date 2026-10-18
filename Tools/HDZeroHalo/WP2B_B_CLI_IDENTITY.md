# WP2B_B_CLI_IDENTITY — live Betaflight readout

**Date:** 2026-10-18  
**Evidence:** `evidence/wp2b-b/cli/` (`01_version.txt`, `02_status.txt`, `23_resource.txt`, `27_diff_all.txt`, `28_dump_all.txt`, …)

## Firmware / board (LIVE / BINARY via CLI)

| Field | Value | Level |
| ----- | ----- | ----- |
| Target | `HDZERO_HALO` / manufacturer `HDZO` | LIVE_CONFIRMED |
| BF version | **2026.6.2** `e0b7bb01b` MSP API **1.48** | LIVE_CONFIRMED |
| Config rev | `3a406c5` | LIVE_CONFIRMED |
| Build time | Oct 18 2026 / 15:24:23 | LIVE_CONFIRMED |
| BUILD KEY | `a81aedd32ca521c92bb20e188e9a8181` | LIVE_CONFIRMED |
| MCU | `STM32H743xx` | LIVE_CONFIRMED |
| MCU unique ID | `004000383533510f39303730` | LIVE_CONFIRMED |
| Reported CLK | 480 MHz | LIVE software report† |
| Vref | 3.29 V | LIVE (Vrefint-based) |
| Core temp | 40 °C | LIVE |
| Craft / pilot | `racer 5` / `slikfpv` | LIVE config |

† `status` CLK uses compile-time `HSE_VALUE` in the SystemCoreClock math — **not** a crystal frequency measurement. See WP2B-A clock analysis.

**Important:** This unit is **not** running factory OEM 4.5.1. It has been upgraded to 2026.6.2 and carries a personalised racing config. WP2B-A factory-software conclusions remain valid as *source* evidence; this board’s *installed* image differs.

## Sensors / storage (LIVE)

| Item | Value | Level |
| ---- | ----- | ----- |
| Gyro / Acc | **ICM42688P** on gyro instance (1) | LIVE_CONFIRMED |
| gyro_1_enabled | ON | LIVE |
| gyro_2_enabled | OFF | LIVE |
| GYRO_CS 1 / EXTI 1 | **B04 / C13** | LIVE resource map |
| GYRO_CS 2 / EXTI 2 | B03 / A15 (present, unused) | LIVE |
| SPI devices detected | 1 | LIVE |
| I2C devices | 0 | LIVE (no external baro/mag fitted) |
| Flash JEDEC | `0x00EF4018` 16 MiB | LIVE (= Winbond W25Q128 family) |
| FlashFS | 16 MiB, used 0 | LIVE |
| OSD | MSP 53×20 | LIVE |

## Orientation (config, not physical)

| Parameter | Value | Level |
| --------- | ----- | ----- |
| `align_board_roll/pitch/yaw` | 0 / 0 / 0 | LIVE config |
| Per-gyro align CLI names (`gyro_1_sensor_align`, …) | Invalid on 2026.6.2 | N/A |
| Absolute PCB mounting | Unknown | HARDWARE_REQUIRED (motion/photo) |
| `acc_calibration` | `27,-73,52,1` | LIVE offsets only |

## Power / ADC / PINIO (LIVE config)

| Parameter | Value | Notes |
| --------- | ----- | ----- |
| ADC_BATT / RSSI / CURR | C00 / C01 / C02 | Matches target |
| `vbat_scale` / divider / multiplier | **110 / 10 / 1** | Matches WP2B-A nominal → AP 11.0 |
| `ibata_scale` / offset | **100 / 0** | Matches OEM CLI / AP 100 A/V |
| Battery present | NO (0.00 V) | USB-only session |
| `resource PINIO 1` | **NONE** | PE3 **not** assigned |
| `pinio_config` | `1,1,1,1` | Defaults; unused without resource |
| `pinio_box` | `255,255,255,255` | Disabled |

OEM docs still describe PINIO on E03 for 9V; **this installed config does not enable it**.

## Motors / DShot (LIVE config)

| Parameter | Value |
| --------- | ----- |
| Motors | C06–C09 → TIM3 CH1–4 |
| `dshot_bitbang` | ON |
| `dshot_bidir` | **ON** (user config; BF default OFF) |
| `motor_pwm_protocol` | **DSHOT300** (default would be DSHOT600) |
| `yaw_motors_reversed` | ON |
| Arming note | `DSHOT_TELEM` disable flag present (no ESC connected) |

## UARTs / RC / MSP (LIVE)

| Port | Function (function bits) | Pins |
| ---- | ------------------------ | ---- |
| UART1 | Serial RX (64) CRSF | B06/B07 |
| UART5 | MSP DisplayPort (131073) | C12/D02 |
| UART2/3/4/7/8 | unused (0) | as target |
| `serialrx_provider` | CRSF | — |

UART4 RX A01 remains mapped for ESC telemetry hardware but serial function is 0 (ESC sensor feature off).

## Resource map vs official target

Pin resources match official `HDZERO_HALO` `config.h` (beeper D12, motors C06–9, SPI1/2, ADC C00–2, gyro CS B04/B03, flash B12, UARTs). Differences from OEM CLI zip: no `LED 2 C14`; no PINIO.

## Commands unsupported on this build

Invalid `get` names included: `gyro_1_sensor_align`, `gyro_2_sensor_align`, `gyro_to_use`, `gyro_1_align`, `voltage_meter_source`, `current_meter_source`, `name`. Used `mcu_id`, `status`, `dump all` instead.
