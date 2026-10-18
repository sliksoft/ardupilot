# WP2B_B_FINAL_REPORT — physical Halo identity via WSL2

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Method:** read-only Betaflight CLI on `/dev/ttyACM0` (usbipd → WSL2)  
**Policy:** no flash, DFU, `set`, `save`, `defaults`, GPIO/PINIO switching, motors, or LiPo

Evidence: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-b/`  
Detail: `WP2B_B_CONNECTION.md`, `WP2B_B_CLI_IDENTITY.md`, `WP2B_B_HARDWARE_COMPARE.md`

## Main conclusion

**This Halo is a live STM32H743 HDZERO_HALO running Betaflight 2026.6.2 with an ICM42688P on GYRO_1 (PB4/PC13), W25Q128 SPI flash, CRSF on UART1, MSP DisplayPort on UART5, and battery scales 110/10/1 + ibata 100 — all matching our ArduPilot pinmap and nominal ADC settings.**

**It is not a virgin factory 4.5.1 image; PE3/PINIO is not configured on this dump; absolute IMU mounting, physical HSE crystal, 9V rail behaviour, and ArduPilot DShot-on-hardware remain unproved. Flash is still forbidden.**

## Status block

```text
WP2B_B_STATUS = PASS_IDENTITY_PARTIAL_HARDWARE

CONNECTION = PASS (/dev/ttyACM0 0483:5740 dialout)
READ_ONLY = YES
FIRMWARE_FLASHED = NO
CONFIG_CHANGED = NO

MCU = STM32H743xx
MCU_ID = 004000383533510f39303730
BF_VERSION = 2026.6.2 (e0b7bb01b) MSP 1.48
BF_TARGET = HDZERO_HALO / HDZO
BF_CONFIG_REV = 3a406c5
FACTORY_4_5_1 = NO (upgraded + personalised config)

IMU = ICM42688P (gyro_1 ON @ CS PB4 / EXTI PC13)
IMU_GYRO2 = DISABLED (CS PB3 present)
IMU_ALIGNMENT_BOARD = 0,0,0
IMU_ABSOLUTE_MOUNT = UNKNOWN

CLK_REPORTED = 480MHz (software SystemCoreClock; not crystal proof)
VREF = 3.29V
SPI_FLASH = JEDEC 0xEF4018 16MiB W25Q128
I2C_DEVICES = 0

UART1 = CRSF SerialRX
UART5 = MSP DisplayPort
PINIO = NONE (PE3 not assigned; pinio_box 255)
VBAT = scale110 divider10 mult1
IBATA = scale100 offset0
DSHOT = bitbang ON, bidir ON, protocol DSHOT300

AP_PINMAP_MATCH = YES
AP_IMU_PROBE_OK_FOR_THIS_SKU = YES (ICM on PB4 first)
AP_DIFFERENCES =
  installed BF 2026.6.2 vs WP2B-A factory 4.5.1 research baseline
  PE3 not PINIO in live BF; AP holds PE3 LOW as GPIO
  BF bitbang DShot vs AP TIM3 DMA/bdshot
  no external baro on I2C (AP requires external baro)

SOFTWARE_QUESTIONS_CLOSED_BY_LIVE_BOARD =
  target name HDZERO_HALO
  this unit IMU = ICM42688P @ PB4
  flash part W25Q128
  UART roles CRSF + MSP DP
  battery nominal scales present on device
  MCU UID recorded

HARDWARE_QUESTIONS_REMAINING =
  physical HSE crystal frequency
  absolute IMU mounting (six-face / photo)
  PE3/9V electrical (PINIO not even mapped now)
  VBAT/current DMM calibration with pack
  AP TIM3 DMA/bdshot with ESC
  option bytes / ROM DFU round-trip
  MPU6000 SKU (different board)

HARDWARE_FLASH_ALLOWED = NO

HEAD_SHA = (set at commit)
PUSH_STATUS = (set at push)
NEXT_ACTION =
  Optional: photograph crystal/IMU; keep BF dump archived before any future AP flash approval;
  do not flash without human gate
```

## Safety compliance

- Only read CLI commands executed  
- Port closed cleanly; no `save`/`set`/`defaults`/`bl`/`dfu` sent  
- No motor, ESC, LiPo, or PINIO switching  
- No ArduPilot hwdef edits  

## Documents

| File | Topic |
| ---- | ----- |
| `WP2B_B_CONNECTION.md` | Port / permissions |
| `WP2B_B_CLI_IDENTITY.md` | Full identity extract |
| `WP2B_B_HARDWARE_COMPARE.md` | vs `hwdef/HDZeroHalo` |
| `WP2B_B_FINAL_REPORT.md` | This status block |
