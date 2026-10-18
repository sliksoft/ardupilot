# WP1A_FINAL_REPORT — HDZero Halo hardware qualification

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**WP0 HEAD:** `0ed78da72db61bad1f95b91d34348bcaa7512f1b`  
**Upstream base:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`

## Executive result

```text
WP1A_STATUS = PARTIAL

HALO_PINMAP = CONFIRMED (Betaflight HDZERO_HALO + HDZero docs; not electrically signed-off)
MCU = STM32H743 (exact package UNKNOWN)
OSCILLATOR = UNKNOWN (must measure; do not guess)
GYRO_MPU6000 = SUPPORTED driver / NEEDS_CONFIG (SKU; CS PB3/EXTI PA15 per BF PR#835)
GYRO_ICM42688 = SUPPORTED driver / NEEDS_CONFIG (SKU; CS PB4/EXTI PC13 per BF PR#835)
DSHOT300 = NEEDS_CONFIG (ArduPilot timer-DMA SUPPORTED; AnyleafH7 PC6-9 TIM3 twin)
DSHOT600 = NEEDS_CONFIG (same path; not TESTED)
BIDIR_DSHOT = NEEDS_CONFIG (BIDIR+DMA_NOSHARE; Anyleaf precedent; not TESTED)
DMA_CONFLICTS = MANAGEABLE (H7 DMAMUX; protect TIM3*/SPI1*/SPI2*; LED prefer NODMA)
ELRS_CRSF = NEEDS_CONFIG (UART1 PB6/PB7; driver SUPPORTED)
HDZERO_OSD = NEEDS_CONFIG (UART5 MSP DisplayPort; driver SUPPORTED; no analog OSD)
SPI_FLASH = NEEDS_CONFIG (W25Q128 SPI2 PB12; JEDEC driver SUPPORTED)
BATTERY_ADC = NEEDS_CONFIG (PC0/PC2; current scale 100 from BF; VBAT scale UNKNOWN)
VTX_9V = NEEDS_CONFIG (PE3 per HDZero firmware doc)
USB_DFU = SUPPORTED (vendor BOOT-button DFU procedure)
BOOTLOADER_LAYOUT = UNKNOWN (128 vs 384 KB reserve)
RECOVERY_PATH = SUPPORTED (STM32 DFU → reflash Betaflight HDZERO_HALO)

EXISTING_PORT_FOUND = NO upstream; unofficial dogjutsu/ardupilot PR#2 only (not authoritative)
NEW_DRIVERS_REQUIRED = NO
HARDWARE_LIMITATIONS = no analog OSD; UART3/UART4 TX absent (RX-only); single IMU per SKU
UNRESOLVED_QUESTIONS = HSE Hz; BL flash reserve; VBAT scale; IMU rotation; PE3 polarity; H743 package
```

**Addendum:** BF config blob `df3ee99d…`; content introduced `d3abecf9…` (#670); path regroup `e0273b95…`. Gyro CS SKU split from closed BF PR #835 (ICM→PB4/PC13, MPU→PB3/PA15). Reject dogjutsu 8 MHz HSE rationale.

## Documents produced

| File | Content |
|------|---------|
| `WP1A_HARDWARE_AUDIT.md` | Sources, checklist, prior-port search |
| `WP1A_PINMAP.md` | Full pin inventory + evidence tags |
| `WP1A_DSHOT_DMA.md` | DShot300/600/bdshot + DMA plan |
| `WP1A_BOOTLOADER.md` | Clocks, layout, DFU, board ID |
| `WP1A_DRIVER_COMPATIBILITY.md` | Driver vs feature matrix |
| `WP1A_BLOCKERS.md` | HARD/SOFT gates |
| `PORT_STATUS.md` | Updated with WP1A deltas (WP0 history kept) |

## 1. Works with existing ArduPilot code (after hwdef)

- STM32H743 ChibiOS HAL  
- MPU6000 (`Invensense`) and ICM42688P (`Invensensev3`)  
- DShot300/600 + bidirectional DShot (timer DMA)  
- CRSF/ELRS on UART  
- MSP DisplayPort OSD (HDZero)  
- W25Q128 JEDEC dataflash logging  
- ADC batt/current, GPIO buzzer/LED/relay, USB MAVLink  
- External GPS / compass / baro probing  
- Standard Copter modes/failsafes (unchanged)

## 2. Hardware definition work required (WP1B+)

- New `libraries/AP_HAL_ChibiOS/hwdef/<HaloBoard>/` (`hwdef.dat`, `hwdef-bl.dat`, defaults)
- `APJ_BOARD_ID` in `board_types.txt`
- SERIAL_ORDER + protocol defaults (RCIN/CRSF, MSP DP, ESC telem RX4)
- TIM3 motor PWM + BIDIR + DMA_NOSHARE
- Dual-SKU IMU probe on PB4/PB3
- SPI2 dataflash
- PE3 9V relay
- Bootloader with DFU enable

## 3. True blockers before flash/flight

1. **Oscillator frequency** (HARD)  
2. **Bootloader / parameter flash layout** (HARD)  
3. Soft: VBAT scale, IMU rotation, PE3 polarity  

## 4. WP1B readiness

**Yes — safe to start WP1B first firmware *build*** using the pinmap and AnyleafH7/Lucid/Foxeer patterns, with provisional HSE/layout clearly marked and **no flashing** until HARD blockers close.

## 5. Requires physical Halo FC

- Crystal / HSE confirmation  
- Flash layout / DFU round-trip  
- IMU detect + rotation  
- DShot300/600/bdshot + AM32 eRPM  
- CRSF link, MSP OSD, logging download  
- Battery scales, 9V switch, buzzer/LED  
- Full Copter arming/flight tests  

**WP1A stops here. Do not start WP1B automatically.**
