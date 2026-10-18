# PORT_STATUS — feature matrix

Status tags: SUPPORTED | NEEDS_CONFIG | NEEDS_DRIVER | HARDWARE_LIMITATION | UNKNOWN | TESTED

Nothing is **TESTED** on Halo hardware unless reproducible evidence is attached.

## WP2B-C update (2026-10-18)

Read-only MSP six-face Acc (`evidence/wp2b-c/`). MSP matches BF body
X-fwd/Y-left/Z-up; AP FRD map is `ROTATION_ROLL_180` (indicated). Hwdef still
`ROTATION_NONE` — incorrect for FRD; not edited this WP. See
`WP2B_C_FRAME_RECONCILIATION.md`. **HARDWARE_FLASH_ALLOWED = NO**.

## WP2B-B update (2026-10-18)

Live read-only CLI on `/dev/ttyACM0` (`0483:5740`). Unit is **HDZERO_HALO** on
**BF 2026.6.2** with **ICM42688P** @ PB4, W25Q128, CRSF UART1, MSP DP UART5,
vbat 110/10/1, ibata 100. PINIO/PE3 not mapped on this dump. Pinmap matches AP
hwdef; absolute IMU/HSE/9V/AP-DShot still open. **HARDWARE_FLASH_ALLOWED = NO**.
Detail: `WP2B_B_*.md`.

## WP2B-A update (2026-10-18)

Betaflight forensic research only (`WP2B_A_*.md`). Local BF 4.5.1 Halo build
reproduced with config `0096077` (OEM CLI). Software HSE8 confirmed; physical
crystal still unverified. Official Halo-named 4.5.1 hex not found for download;
OEM CLI zip found. No ArduPilot firmware changes. **HARDWARE_FLASH_ALLOWED = NO**.

## Codex review fix update (2026-10-18)

Current details and offline validation: `WP2A_REVIEW_FIX_REPORT.md`.
Normal BF builds use HSE8; physical source is still unverified. Buzzer polarity
is corrected in application and bootloader. MPU/ICM relative frames are aligned;
absolute mounting remains blocked. Normal barometer checks are retained and
external BMP280/MS5611/BMP388 probing defaults to mask1030. No-baro startup is
USB configuration-error recovery only. PA10 addressable LEDs are unsupported
with the retained NODMA allocation. PE3 LOW is requested after GPIO initialisation,
not guaranteed throughout reset. All hardware operation remains unverified.

---

## WP1A update (2026-10-18)

Pin-level evidence from official Betaflight `HDZERO_HALO` (`e0273b956485…`) and HDZero docs replaces WP0 “pins UNKNOWN” for most I/O. Oscillator and bootloader flash layout remain **UNKNOWN**.

| Feature | Status | WP1A notes |
| --------- | -------- | ------------ |
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
| Status LED PE2 | NEEDS_CONFIG | See current hwdef |
| LED strip PA10 | NEEDS_CONFIG | TIM1 CH3; prefer NODMA w/ bdshot |
| Switchable 9V PE3 | NEEDS_CONFIG | HDZ `PINIO 1 E03` |
| USB DFU / MAVLink | SUPPORTED / NEEDS_CONFIG | Vendor DFU procedure documented |
| Bootloader layout | UNKNOWN | 128 vs 384 KB |
| External GPS / mag / baro | NEEDS_CONFIG | Pads + I2C1 |
| ArduCopter modes / failsafes | SUPPORTED | Unchanged vehicle code |
| Halo hwdef in tree | NEEDS_CONFIG → **present** | `hwdef/HDZeroHalo/` (WP1B offline build PASS) |
| Prior ArduPilot Halo port | — | **None upstream**; unofficial [dogjutsu PR#2](https://github.com/dogjutsu/ardupilot/pull/2) only |
| Halo on-hardware flight | UNKNOWN | **HARDWARE_FLASH_ALLOWED = NO** |

Detail: `WP1A_*.md`, `WP1B_*.md` in this directory.

---

## WP1B update (2026-10-18)

Offline first board port. Oscillator and flash layout remain UNKNOWN.

| Feature | Status | WP1B notes |
| --------- | -------- | ------------ |
| Board `HDZeroHalo` | built offline | configure + copter PASS |
| Bootloader | built offline | load @ 128 KB provisional |
| Dual IMU SKU probe | compiled | ICM+MPU on PB4 & PB3 |
| DShot300 default | configured | `MOT_PWM_TYPE 5`; TIM3 DMA |
| DShot600 / bdshot | path ready | `HAL_WITH_BIDIR_DSHOT`; not TESTED |
| ELRS / MSP DP / W25Q128 | configured | UART1 / UART5 / SPI2 |
| PE3 9V | GPIO LOW | no RELAY auto-on |
| Oscillator / flash-to-BF | UNKNOWN | **DO NOT FLASH** |

---

## WP2A update (2026-10-18)

Hardware preflight from public sources + local build artifacts. **No device connected.**  
Detail: `WP2A_*.md`.

| Feature | Status | WP2A notes |
| --------- | -------- | ------------ |
| HSE frequency | PHYSICAL UNKNOWN | Normal BF build uses HSE8 via Makefile/compiler defaults; earlier HSI conclusion incorrect |
| Flash layout vs BF | BF proven / AP provisional | BF app @ `0x08040000`; AP app @ `0x08020000` + 128 KB BL |
| DFU recovery to BF | SUPPORTED procedure | HDZ BOOT-button DFU; not exercised |
| TIM3 UP/CH shared DMA | PASS (code) | DMA1 Stream 0 + DMAMUX; bdshot Shared_DMA; not TESTED |
| PE3 9V polarity | ACTIVE_HIGH inferred | `pinio_config=1`; idle LOW; hold LOW in hwdef |
| IMU dual SKU | NEEDS_CONFIG / unprobed | MPU6000 + ICM42688P drivers; rotation UNKNOWN |
| VBAT scale | UNKNOWN | Placeholder 11.0; BF current scale 100 |
| Hardware connected | NO | No USB serial/DFU device in WSL |
| Flash allowed | NO | **HARDWARE_FLASH_ALLOWED = NO** |

---

## WP0 baseline (2026-10-18) — historical

**Base:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`  
WP0 treated Halo pins as UNKNOWN pending OEM docs. That assumption is **superseded** by WP1A for pinmap items above; oscillator/layout unknowns remain valid.

| Feature | WP0 status | Notes / evidence in tree |
| --------- | ------------ | -------------------------- |
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
