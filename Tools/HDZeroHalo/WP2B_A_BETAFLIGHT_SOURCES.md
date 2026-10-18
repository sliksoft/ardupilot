# WP2B_A_BETAFLIGHT_SOURCES — official Halo Betaflight provenance

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**ArduPilot HEAD at research start:** `eef7aa1c0be92665828586fe0ae13113067f3de0`  
**HARDWARE_FLASH_ALLOWED = NO**

Evidence outside Git: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-a/`

## Artifact classes (keep separate)

| Class | What | Identity |
| ----- | ---- | -------- |
| **OEM** | HDZero user manual PDF + Flight Configurator CLI zip | Downloaded from hd-zero.com |
| **Official BF release** | Generic MCU hex from GitHub release assets | `betaflight_4.5.1_STM32H743.hex` (not Halo-specific) |
| **Official BF config** | `betaflight/config` Halo target | Pinned + later revisions |
| **Official BF source** | Tag `4.5.1` | `77d01ba3b76a22909d5f09cb0628820141f95eaa` |
| **Self-reproduced** | Local `make CONFIG=HDZERO_HALO` with SDK GCC 10.3.1 | Hex/ELF/MAP under `evidence/wp2b-a/firmware/reproduced/` |
| **Community / other** | Existing local `2026.6.2` Halo build | Not factory; later release |

A source reproduction is **not** automatically identical to a factory-installed image.

## Betaflight release pin

| Item | Value | Evidence |
| ---- | ----- | -------- |
| Factory version (OEM) | 4.5.1 \[27-Jun-2024\] | HDZero `halo-firmware.md`; User Manual v1.5 |
| BF git tag | `4.5.1` | GitHub releases |
| BF commit | `77d01ba3b76a22909d5f09cb0628820141f95eaa` | Tag object; OEM CLI header `(77d01ba3b)` |
| MSP API | 1.46 | OEM CLI header |

OEM CLI dump timestamp is `Dec 18 2024 / 00:54:02` — later than the “27-Jun-2024” factory note. Treat 27-Jun-2024 as OEM factory guidance, and the CLI header as the dump’s own build identity.

## Config revisions

| Config SHA | Date | Notes | Evidence class |
| ---------- | ---- | ----- | -------------- |
| `009607753079525bbdec1395a1773b79127990ab` (`0096077`) | 2024-12-17 | Rename + gyro defines; **OEM CLI `config rev: 0096077`** | **OEM_CONFIRMED** (CLI) + SOURCE |
| `d3abecf9f2e15716a72f6fc2d775a8b73e2e7129` | 2025-01-17 | Manufacturer-requested defaults: OSD HD, LED strip, MSP DisplayPort UART5, `DEFAULT_CURRENT_METER_SCALE 100` | SOURCE_CONFIRMED |
| `e0273b9564854e0ee1fbadd8200875b30bd35650` | later | Manufacturer grouping path `configs/HDZO/HDZERO_HALO/` | SOURCE_CONFIRMED |
| master `0b73c1f2…` (research clone) | 2026-10-15 tip | Same functional Halo pinmap as e0273b95 content hash | SOURCE_CONFIRMED |

Pinned copies: `evidence/wp2b-a/sources/halo-config-pinned/`.

### Pinmap present in all examined Halo configs (SOURCE_CONFIRMED)

- MCU `STM32H743`, board `HDZERO_HALO`, manufacturer `HDZO`
- Motors PC6–PC9 TIM3 CH1–4; LED strip PA10 TIM1 CH3; beeper PD12
- SPI1 gyros PA5/6/7; GYRO_1 CS PB4 / EXTI PC13; GYRO_2 CS PB3 / EXTI PA15
- SPI2 flash PB12–15; `USE_FLASH_W25Q128FV`
- ADC VBAT PC0, RSSI PC1, CURR PC2
- UART1 ELRS; UART5 MSP path (explicit in later config); UART4 RX ESC telem; UART3 RX DJI
- `DEFAULT_DSHOT_BITBANG DSHOT_BITBANG_ON`
- No `SYSTEM_HSE_MHZ` in any Halo revision examined

## OEM downloads (SHA256)

| File | SHA256 | Source URL |
| ---- | ------ | ---------- |
| `HDZero_Halo_User_Manual_v1.5.pdf` | `c4569e86efaa4e6c0a642e7f8b1a6fbe5e1b206f43219e3072e0e67698c004a9` | `https://www.hd-zero.com/_files/ugd/967e02_35ac483fa49245cab517c7dc65f9e352.pdf` |
| `HDZEROHALO_Rev20250205.zip` | `b2fdd5ddcf52aa67099e0aa2adceb7f18380e5e0bbd681bad3b37a863e70720a` | Flight Configurator tab on hd-zero.com/document |
| `HDZERO_HALO.txt` (inside zip) | `14258ecf83220a4d5e7bd82d7cf3dd471b6257e7db84130b3b2a8ae1abd6831a` | Extracted CLI |

### OEM CLI contents (OEM_CONFIRMED)

Header:

```text
# Betaflight / STM32H743 (SH74) 4.5.1 Dec 18 2024 / 00:54:02 (77d01ba3b) MSP API: 1.46
# config rev: 0096077
```

Notable lines: `resource LED 2 C14`, features TELEMETRY/LED_STRIP/OSD, `serial 4 131073 …` (MSP DisplayPort on UART5), HDZero VTX table, `set ibata_scale = 100`.  
**Absent from this CLI file:** PINIO/PE3, voltage scale overrides, gyro alignment overrides, DShot rate overrides.

## Official Halo-specific firmware hex

| Item | Result |
| ---- | ------ |
| GitHub 4.5.1 release Halo-named asset | **Not published** (only generic `STM32H743.hex`) |
| `build.betaflight.com` target list | `HDZERO_HALO` present for later releases; **4.5.1 not listed** in current API target releases |
| Direct CDN guesses for Halo 4.5.1 hex | HTTP 404 |
| Generic official hex downloaded | `betaflight_4.5.1_STM32H743.hex` SHA256 `38569624d5722ae6f7522ec44a89db34f03b90c1c33418eab890d5a87285f2ae` |

**OFFICIAL_FIRMWARE_FOUND (Halo-named binary):** NO for a downloadable 4.5.1 `HDZERO_HALO` hex.  
OEM directs users to Configurator “Load Firmware \[Online\]” cloud builds — those artifacts were not retrievable as a static file in this WP.

## HDZero documentation

| Doc | Content used |
| --- | ------------ |
| `hd-zero/hdzero-docs` `halo-introduction.md` | STM32H743 480 MHz; MPU6000 **or** ICM42688; 16 MB flash; ELRS Gemini; no analog OSD |
| `halo-firmware.md` | Factory BF 4.5.1; DFU BOOT procedure; CLI zip; PINIO PE3 9V; ELRS 3.5.1 target |
| User Manual v1.5 | Same firmware/DFU/PINIO; ESC AM32/BLHeli32; ESC current scale 170 (ESC-side, not FC ADC) |

Docs clone SHA (research): `7469cf7fc51ba6c8a627de161667dd490a8dca73`.

## Closed / field evidence (not master config)

| Item | Status | Use |
| ---- | ------ | --- |
| config PR #835 (split ICM / MPU6000 targets) | Closed, **unmerged** | ICM on PB4/PC13 as GYRO_1; MPU on PB3/PA15 as GYRO_1 — **INFERRED** CS mapping |
| betaflight issue #14536 | Closed; reports Halo **MPU6000** hardware | Confirms MPU SKU exists in the field |

## Hashes index

Full list: `evidence/wp2b-a/hashes/artifacts.sha256`.
