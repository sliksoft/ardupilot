# WP1A_PINMAP — HDZero Halo pin inventory

**Date:** 2026-10-18  
**ArduPilot tree:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a` (upstream base)  
**Betaflight config commit (path history):** `e0273b9564854e0ee1fbadd8200875b30bd35650`  
**Source:** [betaflight/config `configs/HDZO/HDZERO_HALO/config.h`](https://github.com/betaflight/config/blob/master/configs/HDZO/HDZERO_HALO/config.h)

Evidence classes:

| Tag | Meaning |
|-----|---------|
| **BF** | Official Betaflight target `config.h` |
| **HDZ** | Official HDZero documentation (`docs.hd-zero.com` / `hd-zero/hdzero-docs`) |
| **AF** | STM32H743 alternate-function table in ArduPilot (`STM32H743xx.py`) |
| **DER** | Derived / inferred (not primary evidence) |
| **UNK** | Not established |

## MCU / identity

| Item | Value | Evidence |
|------|-------|----------|
| Target MCU | `STM32H743` | BF L27; HDZ intro “STM32H743 (480MHz)” |
| Exact package / marking | UNKNOWN | Need BOM/schematic or chip marking photo |
| Internal flash | 2048 KB assumed for H743xx class | DER from ArduPilot H743 boards; ST H743 typically 2 MB — confirm package |
| Board name (BF) | `HDZERO_HALO` / `HDZO` | BF L29–30 |

## Motors / timers

| Function | Pin | Timer (BF) | AF (ArduPilot) | Evidence |
|----------|-----|------------|----------------|----------|
| MOTOR1 | PC6 | TIM3 CH1 | `PC6:TIM3_CH1` AF2 | BF L51, L87; AF |
| MOTOR2 | PC7 | TIM3 CH2 | `PC7:TIM3_CH2` | BF L52, L88; AF |
| MOTOR3 | PC8 | TIM3 CH3 | `PC8:TIM3_CH3` | BF L53, L89; AF |
| MOTOR4 | PC9 | TIM3 CH4 | `PC9:TIM3_CH4` | BF L54, L90; AF |
| TIM3 UP DMA opt | — | `TIMUP3_DMA_OPT 5` | — | BF L94 |
| Default DShot path (BF) | — | **bitbang ON** | N/A for AP | BF L102 `DEFAULT_DSHOT_BITBANG` |

ArduPilot reference with **identical** motor pins + TIM3 + `BIDIR`:  
`libraries/AP_HAL_ChibiOS/hwdef/AnyleafH7/hwdef.dat` L86–89.

## IMU / SPI1

| Function | Pin | Notes | Evidence |
|----------|-----|-------|----------|
| SPI1 SCK/MISO/MOSI | PA5 / PA6 / PA7 | Gyro bus | BF L71–76 |
| GYRO_1 CS | PB4 | Primary CS | BF L82 |
| GYRO_1 EXTI | PC13 | DRDY | BF L81 |
| GYRO_2 CS | PB3 | Second CS on same SPI1 | BF L84 |
| GYRO_2 EXTI | PA15 | DRDY | BF L83 |
| Drivers enabled | MPU6000 + ICM42688P | Both compiled in BF | BF L32–37 |
| Population | **One gyro per SKU** | “two versions, MPU6000 or ICM42688” | HDZ introduction |
| Orientation | CW0° in EmuFlight target | Not HDZero primary | DER / UNK for ArduPilot `ROTATION_*` |

Do **not** assume two physical gyros are fitted because two CS/EXTI pairs exist.

## SPI flash

| Function | Pin / bus | Evidence |
|----------|-----------|----------|
| Flash CS | PB12 | BF L80 |
| SPI2 SCK/MISO/MOSI | PB13 / PB14 / PB15 | BF L72–77 |
| Part | W25Q128FV (16 MB) | BF L38–39 `USE_FLASH_W25Q128FV`; HDZ “16MB Flash” |
| Instance | SPI2 | BF L115 |

## UARTs

| UART | TX | RX | Default role (docs/BF) | Evidence |
|------|----|----|------------------------|----------|
| USART1 | PB6 | PB7 | ELRS / SerialRX | BF L55,61; HDZ “FC UART TX1/RX1”; BF L105 `SERIALRX_UART` |
| USART2 | PA2 | PA3 | Free pads | BF L56,62; HDZ UART pads |
| USART3 | *(none)* | PB11 | DJI HDL (RX only) | BF L63; HDZ “DJI HDL RX3” |
| UART4 | *(none)* | PA1 | ESC telemetry RX | BF L64; HDZ “ESC Telemetry RX4” |
| UART5 | PC12 | PD2 | HDZero MSP DisplayPort | BF L57,65; L106; HDZ “VTX MSP UART TX5/RX5” |
| UART7 | PE8 | PE7 | Free pads | BF L58,66 |
| UART8 | PE1 | PE0 | Free pads | BF L59,67 |
| USB | Type-C | — | VCP / DFU | HDZ |

## I²C / ADC / GPIO

| Function | Pin | Evidence |
|----------|-----|----------|
| I2C1 SCL/SDA | PB8 / PB9 | BF L68–69; HDZ I2C pads |
| VBAT ADC | PC0 | BF L78 |
| RSSI ADC | PC1 | BF L79 |
| CURR ADC | PC2 | BF L80; BF scale 100 L112 |
| Buzzer | PD12 inverted | BF L50, L113 `BEEPER_INVERTED` |
| Status LED0 | PE2 | BF L70 |
| LED strip | PA10 → TIM1 CH3 | BF L54, L91 |
| VTX 9V enable | **PE3** (PINIO) | HDZ firmware doc CLI `resource PINIO 1 E03` |

## VTX connector (HDZ docs)

VTX connector signals (product docs): RX3, GND, RX5, TX5, GND, 9V — aligns with UART3 RX + UART5 + switched 9V.

## Pin conflict notes (for hwdef)

1. **PC6–PC9** must be TIM3 PWM motors — not USART6 / SDMMC.
2. **PA10** LED strip vs USART1_RX AF — USART1 uses PB7; OK.
3. **PB3/PB4** used as **GPIO CS**, not SPI1 AF (SPI1 uses PA5–7).
4. **PD12** buzzer: prefer GPIO (not TIM4) in ArduPilot to free DMA, matching Lucid-style boards.
5. **PE3** GPIO relay/PINIO for 9V — confirm active level on hardware (**UNK** polarity beyond BF `pinio_config = 1`).

## Still UNKNOWN (need hardware)

- HSE crystal frequency (see `WP1A_BOOTLOADER.md`)
- Exact STM32H743 package / flash size marking
- IMU mounting rotation for ArduPilot
- VBAT divider scale (BF does not publish voltage scale in `config.h`)
- 9V PE3 active-high/low under ArduPilot relay semantics
- Full schematic / net names
