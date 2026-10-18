# PORT_STATUS — feature matrix

Status tags: SUPPORTED | NEEDS_CONFIG | NEEDS_DRIVER | HARDWARE_LIMITATION | UNKNOWN | TESTED

Nothing is **TESTED** on Halo hardware unless reproducible evidence is attached.

---

## WP1A update (2026-10-18)

Pin-level evidence from official Betaflight `HDZERO_HALO` (`e0273b956485…`) and HDZero docs replaces WP0 “pins UNKNOWN” for most I/O. Oscillator and bootloader flash layout remain **UNKNOWN**.

| Feature | Status | WP1A notes |
|---------|--------|------------|
| STM32H743 + ChibiOS | SUPPORTED | BF + HDZ; package marking still UNKNOWN |
| Oscillator Hz | UNKNOWN | Must measure; see `WP1A_BOOTLOADER.md` |
| MPU6000 (SKU) | SUPPORTED / NEEDS_CONFIG | SPI1 CS PB4/PB3; Invensense |
| ICM42688P (SKU) | SUPPORTED / NEEDS_CONFIG | Alternate SKU; Invensensev3; not dual-fitted |
| Four motors PC6–9 TIM3 | NEEDS_CONFIG | BF L51–54; AnyleafH7 L86–89 twin |
| DShot300 | NEEDS_CONFIG | AP timer-DMA (not BF bitbang) |
| DShot600 | NEEDS_CONFIG | Same path |
| Bidirectional DShot | NEEDS_CONFIG | BIDIR + DMA_NOSHARE TIM3* |
| ESC RPM (bdshot) | NEEDS_CONFIG | Plus UART4 RX PA1 ESC telem |
| CRSF / ELRS UART1 | NEEDS_CONFIG | PB6/PB7; Gemini onboard |
| HDZero MSP DisplayPort UART5 | NEEDS_CONFIG | PC12/PD2; OSD_TYPE 5 |
| Analog OSD | HARDWARE_LIMITATION | None by design |
| SPI flash W25Q128 | NEEDS_CONFIG | SPI2 PB12; JEDEC SUPPORTED |
| Battery ADC PC0/PC2 | NEEDS_CONFIG | CURR scale 100 (BF); VBAT scale UNKNOWN |
| RSSI ADC PC1 | NEEDS_CONFIG | Optional |
| Buzzer PD12 | NEEDS_CONFIG | Inverted (BF) |
| Status LED PE2 | NEEDS_CONFIG | |
| LED strip PA10 | NEEDS_CONFIG | TIM1 CH3; prefer NODMA w/ bdshot |
| Switchable 9V PE3 | NEEDS_CONFIG | HDZ `PINIO 1 E03` |
| USB DFU / MAVLink | SUPPORTED / NEEDS_CONFIG | Vendor DFU procedure documented |
| Bootloader layout | UNKNOWN | 128 vs 384 KB |
| External GPS / mag / baro | NEEDS_CONFIG | Pads + I2C1 |
| ArduCopter modes / failsafes | SUPPORTED | Unchanged vehicle code |
| Halo hwdef in tree | UNKNOWN | Not implemented (WP1B+) |
| Prior ArduPilot Halo port | — | **None found** |

Detail: `WP1A_*.md` in this directory.

---

## WP0 baseline (2026-10-18) — historical

**Base:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`  
WP0 treated Halo pins as UNKNOWN pending OEM docs. That assumption is **superseded** by WP1A for pinmap items above; oscillator/layout unknowns remain valid.

| Feature | WP0 status | Notes / evidence in tree |
|---------|------------|--------------------------|
| STM32H743 + ChibiOS | SUPPORTED | e.g. `TBS_LUCID_H7/hwdef.dat` L5 |
| MPU6000 driver | SUPPORTED | `IMU Invensense` |
| ICM42688P driver | SUPPORTED | `IMU Invensensev3` |
| Four motor outputs | NEEDS_CONFIG | GEPRC / Foxeer patterns |
| DShot300 / DShot600 | SUPPORTED | MOT_PWM_TYPE 5/6 |
| Bidirectional DShot | NEEDS_CONFIG | BIDIR + DMA |
| ESC UART telemetry | SUPPORTED / NEEDS_CONFIG | SerialProtocol_ESCTelemetry |
| CRSF / ELRS | SUPPORTED / NEEDS_CONFIG | AP_RCProtocol_CRSF |
| HDZero MSP DisplayPort | SUPPORTED / NEEDS_CONFIG | AP_OSD_MSP_DisplayPort |
| UART / SPI / I²C / ADC | NEEDS_CONFIG | WP0: pins UNKNOWN → see WP1A |
| Battery / current sense | NEEDS_CONFIG | HAL_BATT_* |
| 16 MB SPI flash logging | SUPPORTED / NEEDS_CONFIG | HAL_LOGGING_DATAFLASH_ENABLED |
| Buzzer / LED / 9V | NEEDS_CONFIG | WP0 pin UNKNOWN → WP1A PD12/PE2/PE3 |
| USB + MAVLink | SUPPORTED / NEEDS_CONFIG | OTG1 |
| Bootloader / recovery | NEEDS_CONFIG | Layout UNKNOWN |
| External GPS / compass / baro | SUPPORTED / NEEDS_CONFIG | Probing |
| ArduCopter modes / failsafes | SUPPORTED | Not board-specific |
| Halo board hwdef | UNKNOWN | WP1B+ |
| Halo on-hardware flight | UNKNOWN | No TESTED evidence |

### WP0 summary

Almost all product goals map to SUPPORTED drivers plus NEEDS_CONFIG hwdef work. WP1A supplies the pinmap that WP0 lacked.
