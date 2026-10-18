# WP1_REFERENCE_INVENTORY — H743 hwdef comparison (read-only)

**Work package:** WP0 (research only — no Halo hwdef written)  
**Date:** 2026-10-18  
**Tree SHA:** `afeb9c4941543d97f3e04fecf257b8f598f49a6a`

Primary references examined:

| Board | Path |
|-------|------|
| TBS Lucid H7 | `libraries/AP_HAL_ChibiOS/hwdef/TBS_LUCID_H7/` |
| Matek H743 | `libraries/AP_HAL_ChibiOS/hwdef/MatekH743/` |
| Matek H743 bdshot | `libraries/AP_HAL_ChibiOS/hwdef/MatekH743-bdshot/` |
| GEPRC Taker H743 | `libraries/AP_HAL_ChibiOS/hwdef/GEPRC_TAKER_H743/` |
| Foxeer H743 v1 | `libraries/AP_HAL_ChibiOS/hwdef/FoxeerH743v1/` |
| T-Motor H743 | `libraries/AP_HAL_ChibiOS/hwdef/TMotorH743/` |
| Skystars H7 HD | `libraries/AP_HAL_ChibiOS/hwdef/SkystarsH7HD/` |

---

## 1. Processor, oscillator, memory

| Board | MCU | OSC | MCU flash | BL reserve | Storage |
|-------|-----|-----|-----------|------------|---------|
| TBS_LUCID_H7 | STM32H743xx L5 | 8 MHz L11 | 2048 KB L13; 480 MHz L14 | 128 KB L17 | STORAGE_FLASH_PAGE 14 L192; HAL_STORAGE_SIZE 32768 L188 |
| MatekH743 | STM32H743xx L5 | 8 MHz L11 | 2048 KB L13 | 128 KB L16 | page 14 L180; 32768 L176 |
| GEPRC_TAKER_H743 | STM32H743xx L6 | 8 MHz L12; 480 MHz L13 | 2048 KB L15 | 384 KB L18 | page 1 L136; 16384 L135 |
| FoxeerH743v1 | STM32H743xx L6 | 8 MHz L13; 480 MHz L14 | 2048 KB L16 | 384 KB L19 | page 1 L22; 16384 L21 |
| TMotorH743 | STM32H743xx L6 | 8 MHz L13; 480 MHz L15 | 2048 KB L17 | 384 KB L20 | page 1 L23; 16384 L22 |
| SkystarsH7HD | STM32H743xx L5 | 8 MHz L11 | 2048 KB L13 | 128 KB L21 | page 14 L25; 32768 L26 |

**WP1 note:** Confirm Halo crystal and whether bootloader occupies 128 KB or 384 KB
before copying `FLASH_RESERVE_START_KB`. Lucid/Matek (128 KB) vs many FPV H7
boards (384 KB) is a common fork.

---

## 2. Gyro variants (MPU6000 / ICM42688P)

| Board | Devices | Lines |
|-------|---------|-------|
| TBS_LUCID_H7 | Dual ICM42688 (`Invensensev3`) + MPU6000 fallbacks on same CS | SPIDEV L195–198; IMU L207–210 |
| MatekH743 | ICM42688 + ICM42605 + ICM20602 + MPU6000 | SPIDEV L183–186; IMU L205–208 |
| GEPRC_TAKER_H743 | MPU6000 SPI1 + ICM42688 SPI2 | SPIDEV L139–140; IMU L145–146 |
| TMotorH743 | ICM42688 + BMI270 on SPI1 CS | SPIDEV L149–150; IMU L152–153 |
| FoxeerH743v1 | (see file after L159 — Invensense family) | dataflash L145–147 |

**WP1 note:** GEPRC_TAKER_H743 is a strong dual-IMU template (MPU6000 + ICM42688)
if Halo ships both variants on different SPI buses. Lucid shows probing multiple
IMU types on shared CS for board revisions.

---

## 3. Motor pins, TIM3, DMA

| Board | Motor TIM / BIDIR | DMA notes |
|-------|-------------------|-----------|
| TBS_LUCID_H7 | M1–2 TIM3 CH3/4 with BIDIR on M1; also TIM2/5/4 | L145–154; `DMA_NOSHARE` TIM3* TIM2* TIM5* TIM4* L186 |
| MatekH743 (std) | TIM8/TIM5/TIM4 — **no** BIDIR | L145–156 |
| MatekH743-bdshot | Remaps to TIM3/TIM2/TIM5/TIM4 with BIDIR | L23–30; DMA L44–45 |
| GEPRC_TAKER_H743 | TIM3 CH1–4 BIDIR on M1/M4; TIM4/TIM8 | L117–125; DMA L132–133 |
| FoxeerH743v1 | TIM3 BIDIR M1/M3; TIM4/TIM8 | L128–135 |
| TMotorH743 | TIM5 CH1–4 BIDIR M1/M3 | L121–124; DMA L155–156 |

**WP1 note:** If Halo motors are on TIM3 (common on FPV H743), prefer
`MatekH743-bdshot` / `GEPRC_TAKER_H743` / Lucid TIM3 patterns and reserve DMA
with `DMA_NOSHARE TIM3* …`.

---

## 4. DShot300 / DShot600

- Protocol selection is vehicle-side (`MOT_PWM_TYPE` DShot300/600) —
  `libraries/AP_Motors/AP_MotorsMulticopter.cpp` (~L99).
- Board responsibility: correct PWM timer channels, DMA, optional `BIDIR`.
- No separate hwdef “DShot300 only” flag required on these H743 boards.

---

## 5. Flash storage (SPI dataflash)

| Board | Bus / CS | Enable |
|-------|----------|--------|
| SkystarsH7HD | SPI3 W25Q128, `FLASH_CS` PA15 | L28–29, L58–62, L77 |
| FoxeerH743v1 | SPI3 `FLASH1_CS` PA15 @ 104 MHz | L145–147 |
| TMotorH743 | SPI3 `FLASH1_CS` PA15 @ 104 MHz | L137–139 |
| TBS_LUCID_H7 | **microSD** SDMMC1 (not SPI flash) | L165–171; `HAL_OS_FATFS_IO` L221 |
| MatekH743 | microSD SDMMC1 | L162–168 |
| GEPRC_TAKER_H743 | SPI SD card (`sdcard` SPI3) | L53–57, L141; FATFS L160 |

**WP1 note:** For Halo’s stated **16 MB SPI flash logging**, prefer
FoxeerH743v1 / TMotorH743 / SkystarsH7HD patterns
(`SPIDEV dataflash` + `HAL_LOGGING_DATAFLASH_ENABLED`), not Lucid’s SDMMC path.

---

## 6. ELRS / CRSF and HDZero MSP DisplayPort

| Concern | In-tree support | Example |
|---------|-----------------|---------|
| CRSF / ELRS | `SerialProtocol_CRSF` / RCIN UART | `AP_RCProtocol_CRSF.cpp`; Lucid USART6 RCIN L122–125 |
| MSP DisplayPort | `SerialProtocol_MSP_DisplayPort` + `AP_MSP_VIDEOTX_ENABLED` | Lucid USART3 L111–115; GEPRC USART1 L82–86; TMotor UART7 DJI_FPV L84–88 |
| OSD MSP backend | `AP_OSD_MSP_DisplayPort.cpp` | init ~L37–53 |

**WP1 note:** Wire Halo’s ELRS UART as `SerialProtocol_RCIN` or CRSF; wire HDZero
MSP UART as `SerialProtocol_MSP_DisplayPort`. Exact UART numbers need Halo docs
(**UNKNOWN**).

---

## 7. Bootloader and safe recovery

| Board | BL highlights |
|-------|---------------|
| TBS_LUCID_H7 | `hwdef-bl.dat`: load @ 128 KB L20; USB+UART7 L23; CS held high L39–44; `VPWR`/relays safe L46–52; `ENABLE_DFU_BOOT 1` L56; SD flash-from-BL L77 |
| MatekH743 / others | Separate `hwdef-bl.dat` with matching `APJ_BOARD_ID` |

**WP1 note:** Register a unique `APJ_BOARD_ID` in
`Tools/AP_Bootloader/board_types.txt`. Keep IMU/flash CS high in the bootloader.
Document DFU vs UART vs SD recovery for Halo once hardware docs exist. Do not
flash during WP0/WP1 planning.

---

## Recommended starting templates for WP1 (pending Halo pinout)

1. **Closest FPV feature mix (SPI flash + bdshot + MSP):** start from
   `FoxeerH743v1` or `TMotorH743` for flash/IMU/DShot shape; borrow MSP
   DisplayPort default from `TBS_LUCID_H7` L111–115 or `GEPRC_TAKER_H743` L82–86.
2. **Dual IMU MPU6000 + ICM42688:** `GEPRC_TAKER_H743` L41–51, L139–146.
3. **TIM3 bdshot + DMA discipline:** `MatekH743-bdshot` L23–45 or Lucid L145–186.
4. **9V / PINIO style rail:** Lucid `VPWR` L178–183 and BL L51–52.
5. **Avoid** copying Lucid’s SDMMC logging if Halo only has SPI NOR flash.

Final template choice must wait on Halo schematic evidence — do not invent pins.
