# WP1A_HARDWARE_AUDIT — consolidated Halo hardware qualification

**Date:** 2026-10-18  
**WP0 correction:** WP0 marked most Halo pins UNKNOWN; WP1A replaces that with Betaflight + HDZero evidence. Prior WP0 docs remain historical; see updated `PORT_STATUS.md`.

## Primary sources

| Source | Ref | Role |
| -------- | ----- | ------ |
| Betaflight target | `betaflight/config` `configs/HDZO/HDZERO_HALO/config.h` @ commit `e0273b9564854e0ee1fbadd8200875b30bd35650` | Intended pinmap |
| HDZero docs | <https://docs.hd-zero.com/halo-introduction> | Product specs, UART roles, dual gyro SKUs |
| HDZero firmware doc | `hd-zero/hdzero-docs` `docs/halo-firmware.md` | DFU, ELRS target, **PE3 9V PINIO** |
| EmuFlight target | `emuflight/EmuFlight` `src/main/target/HDZERO_HALO/` | Cross-check (secondary) |
| ArduPilot tree | `afeb9c4941543d97f3e04fecf257b8f598f49a6a` | Drivers / peer hwdefs |
| Porting guide | <https://ardupilot.org/dev/docs/porting.html> | Oscillator must be measured, not guessed |

BF pinmap is strong **intent** evidence, not a substitute for electrical verification (crystal, scales, PE3 polarity).

## Confirmed checklist (user table)

| Hardware | Expected | WP1A result |
| ---------- | ---------- | ------------- |
| MCU | STM32H743 | **Confirmed** BF + HDZ |
| Motors | PC6–PC9 | **Confirmed** BF |
| Motor timer | TIM3 CH1–4 | **Confirmed** BF + STM32 AF |
| Gyro SPI | SPI1 | **Confirmed** BF |
| Gyro CS | PB4 and PB3 | **Confirmed** BF |
| Gyro EXTI | PC13 and PA15 | **Confirmed** BF |
| Flash | SPI2 CS PB12 W25Q128 | **Confirmed** BF + HDZ 16MB |
| ELRS | UART1 | **Confirmed** BF + HDZ |
| HDZero MSP | UART5 | **Confirmed** BF + HDZ |
| I²C | PB8/PB9 | **Confirmed** BF + HDZ |
| Accu ADC | PC0 / PC2 (+ RSSI PC1) | **Confirmed** BF |
| Buzzer | PD12 | **Confirmed** BF |
| LED strip | PA10 | **Confirmed** BF |
| VTX 9V | PE3 | **Confirmed** HDZ firmware CLI (not in BF `config.h` resources) |

## Feature audit summary

| Domain | Status | Detail doc |
| -------- | -------- | ------------ |
| Pinmap | Mostly BF/HDZ confirmed | `WP1A_PINMAP.md` |
| Oscillator / BL layout | UNKNOWN | `WP1A_BOOTLOADER.md` |
| DShot300/600/bdshot | NEEDS_CONFIG (SUPPORTED path; Anyleaf pin twin) | `WP1A_DSHOT_DMA.md` |
| Drivers | No new drivers required | `WP1A_DRIVER_COMPATIBILITY.md` |
| Prior AP port | **None found** | § below |
| Blockers | Oscillator, BL layout, Vbat scale, IMU rotation | `WP1A_BLOCKERS.md` |

## Existing ArduPilot Halo ports — search result

Searches performed (2026-10-18):

- `gh search code/prs/issues` for HDZERO_HALO / HDZero Halo on `ArduPilot/ardupilot`
- Local `git grep` under hwdef / Tools
- Web search for ArduPilot Halo board ports
- Follow-up: personal-fork / BF PR scan (2026-10-18)

| Finding | Status |
| --------- | -------- |
| Upstream `ArduPilot/ardupilot` | **No** hwdef / issue / PR |
| Unofficial fork | **Yes** — <https://github.com/dogjutsu/ardupilot/pull/2> (`hdzero_halo` branch), merged **only into that fork** (2026-02-27). Combat-robot/Rover oriented. |
| This workspace | Docs only; no `hwdef` yet |

**dogjutsu fork — use as optional reference only, not authority:**

- Review correction: normal BF builds do use HSE8 through Makefile/compiler defaults, despite no `SYSTEM_HSE_MHZ` in `config.h`. This supports the software setting, not physical oscillator proof; see `WP2A_HSE.md`.
- README IMU CS note disagrees with BF GYRO_1=PB4 (ICM) vs GYRO_2=PB3 (MPU) split from closed BF PR #835.
- Marks BIDIR on motors **and** LED/beeper PWM; APJ board ID `9300` is a local placeholder.
- Do **not** copy blindly into an upstream-quality Copter port.

Related (not a Halo FC port):

- ArduPilot wiki DisplayPort / HDZero VTX configuration (generic)
- Discourse threads on HDZero OSD with other FCs (e.g. KakuteH7)
- Betaflight / EmuFlight / BossHobby targets for Halo (non-ArduPilot)

## Gyro population model

HDZero: board sold as **MPU6000 version** or **ICM42688 version**.  
BF enables both drivers and two CS lines — standard multi-revision target pattern.  
**Interpretation:** one physical IMU per board; hwdef should probe both CS/types.

## Electrical items still requiring lab / OEM data

1. HSE crystal frequency  
2. Flash bootloader size used by factory BF image  
3. VBAT divider ratio  
4. IMU mechanical orientation  
5. PE3 active level for 9V BEC  
6. Published schematic (not found in public hdzero-docs tree during WP1A)

## WP0 → WP1A status migration

| WP0 claim | WP1A update |
| ----------- | ------------- |
| Most pins UNKNOWN | Replaced by BF/HDZ pinmap |
| SPI flash UNKNOWN | W25Q128 on SPI2 PB12 |
| ELRS/MSP UART UNKNOWN | UART1 / UART5 |
| 9V UNKNOWN pin | PE3 via HDZ docs |
| Oscillator UNKNOWN | **Still UNKNOWN** (correctly) |
