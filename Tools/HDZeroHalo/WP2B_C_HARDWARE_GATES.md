# WP2B_C_HARDWARE_GATES — remaining conditions before first ArduPilot flash

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
**Policy:** documentation of gates only — this WP does not authorize flash, DFU, or config writes.

Evidence classes:

| Tag | Meaning |
| --- | ------- |
| PROVED_LIVE | Measured / read from this physical Halo |
| SOFTWARE_MATCH | BF source / AP hwdef / OEM text agree; not a physical proof |
| UNPROVED | Still needs hardware or human gate |

## Gate list for first ArduPilot flash

| # | Gate | Status | Notes |
| - | ---- | ------ | ----- |
| G1 | Human flash approval | **UNPROVED / REQUIRED** | Explicit operator authorization; `HARDWARE_FLASH_ALLOWED` must flip |
| G2 | Archive live BF config | **PARTIAL** | WP2B-B `diff all` / `dump all` archived under `evidence/wp2b-b/`; keep before any erase |
| G3 | Recovery path ready | **SOFTWARE_MATCH / UNTESTED** | OEM BOOT-button ROM DFU documented; AP `ENABLE_DFU_BOOT` in BL only; **not exercised** |
| G4 | Halo BF recovery image on hand | **PARTIAL** | Local WP2B-A reproduced 4.5.1 Halo hex exists; factory/cloud Halo hex SHA preferred; installed image is **2026.6.2** not 4.5.1 |
| G5 | Physical HSE = 8 MHz | **UNPROVED** | BF + AP compile HSE8 / 480 MHz; live `CLK=480MHz` is software report only; no crystal photo/scope |
| G6 | MCU identity for DFU notes | **PARTIAL** | Class STM32H743xx + UID live; package marking / ROM version / option bytes **UNPROVED** |
| G7 | IMU SKU + CS | **PROVED_LIVE** | ICM42688P on GYRO_1 PB4/PC13; MPU not populated |
| G8 | IMU absolute orientation | **PARTIAL — ROTATION INDICATED** | Six-face Acc matches BF X-fwd/Y-left/Z-up; AP FRD needs `ROTATION_ROLL_180` (documented, **hwdef still `NONE`**); optional silk photo + gyro signs; see `WP2B_C_FRAME_RECONCILIATION.md` |
| G9 | External barometer | **UNPROVED / REQUIRED for flight** | No onboard baro; AP expects external I²C baro or stays in USB config-error path |
| G10 | PE3 / 9V rail behaviour | **UNPROVED** | Live BF has no PINIO on PE3; AP holds PE3 LOW; electrical table across reset/DFU unknown |
| G11 | VBAT / current calibration | **UNPROVED** | Nominal scales match (110/10/1, ibata 100); no pack / DMM |
| G12 | DShot / TIM3 DMA / bdshot | **UNPROVED** | Pins match; AP path ≠ BF bitbang; needs ESC bench |
| G13 | ELRS / CRSF on UART1 | **SOFTWARE_MATCH** | Configured live; RF bind/failsafe not tested this WP |
| G14 | MSP DisplayPort UART5 | **SOFTWARE_MATCH** | Configured live; VTX canvas not tested |
| G15 | W25Q128 logging | **PROVED_LIVE part** | JEDEC W25Q128; endurance/throughput untested under AP |
| G16 | No accidental motor/GPIO power | **PROCESS** | First AP bring-up: props off, no PINIO switching, USB or safe bench PSU |

## Proven vs software vs hardware (summary)

### Proved on this Halo (live)

- USB MSP/CLI identity: HDZERO_HALO / HDZO / BF 2026.6.2 / MSP 1.48  
- MCU class STM32H743xx, UID recorded  
- ICM42688P @ PB4 / PC13; second gyro slot unused  
- SPI flash W25Q128 16 MiB  
- Pin roles for IMU/flash/UART1/UART5/ADC defaults match AP hwdef  
- Six-face accelerometer: MSP = BF X-fwd / Y-left / Z-up (USB aft, components up)  

### Software agreement only (not physical proof)

- HSE 8 MHz compile path (BF Makefile + AP `OSCILLATOR_HZ 8000000`)  
- SYSCLK 480 MHz reported by BF `status`  
- BF CW0 MSP body ↔ AP FRD via `ROTATION_ROLL_180` (indicated; hwdef not yet updated)  
- Prior relative ICM/`NONE` vs MPU/`ROLL_180_YAW_90` raw-register normalisation (WP2A) — not AP FRD  
- PE3 active-HIGH PINIO semantics in OEM/BF docs (not mapped on this dump)  
- Flash layout difference BF vs AP (known; dual-boot impossible)  
- OEM DFU procedure text  

### Still requires hardware / human action

- Crystal measurement or marking photo  
- Package / option bytes / ROM DFU round-trip  
- Human decision to apply ICM `ROTATION_ROLL_180` (and MPU composition) in hwdef  
- Optional silk photo + signed gyro rotations before trusting first AP attitude  
- External baro fit for any flight or baro-using modes  
- PE3/9V meter across power states  
- Battery ADC with LiPo + DMM  
- ESC DShot/eRPM on AP TIM3 DMA  
- Explicit flash authorization  

## Minimum set before *considering* a first AP flash (bench only)

Not an authorization — a checklist:

1. **G1** human approval recorded.  
2. **G2** BF dump archived (done for this unit in WP2B-B; re-diff if config changed).  
3. **G3–G4** operator can perform ROM DFU restore to a known Halo BF image.  
4. **G5** accept provisional HSE8 **or** obtain crystal evidence (risk acknowledgment if still unknown).  
5. **G7** already proved for this SKU; **G8** plan `ROTATION_ROLL_180` for ICM (docs indicate; hwdef still `NONE`) before trusting AP attitude.  
6. **G9** external baro available **or** accept USB config-error-only bring-up.  
7. **G16** props off; no VTX 9V experiments on first boot.  

**G10–G12, G13–G15** remain post-flash bench items; they do not block a carefully staged first USB boot, but they **do** block claiming flight readiness.

## Explicit non-goals of WP2B-C

- No ArduPilot flash  
- No DFU / bootloader activation  
- No BF configuration changes  
- No progression into WP3  
