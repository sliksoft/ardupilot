# WP2B_A_INDEPENDENT_REVIEW — read-only gate

**Date:** 2026-10-18  
**Scope:** Verify key WP2B-A claims against on-disk sources. No edits, no flash.

## Per-claim verdict

| Claim | Verdict | Evidence checked |
| ----- | ------- | ---------------- |
| 1. HSE8 software chain; not physical proof | **PASS** | `Makefile:128` `HSE_VALUE ?= 8000000`; Halo `config.h` has no `SYSTEM_HSE_MHZ`; `system_stm32h7xx.c` selects `RCC_PLLSOURCE_HSE` when `HSE_VALUE` defined; verbose compile contains `-DHSE_VALUE=8000000`. Physical crystal still open. |
| 2. IMU dual drivers/CS/EXTI; CW0; absolute mount unknown | **PASS** | Config enables MPU6000+ICM42688P; PB4/PC13 and PB3/PA15; `gyrodev.c` defaults `CW0_DEG`; PR835 unmerged CS split treated as INFERRED only. |
| 3. PE3 PINIO active-HIGH software; not in config/CLI zip | **PASS** | No PE3 in `config.h` or OEM CLI; HDZero docs PINIO CLI; `pinio.c` non-inverted → idle LOW, on→HIGH. Electrical FET HARDWARE_REQUIRED. |
| 4. BF flash 128/128/1792; ELF confirms; AP differs | **PASS** | `stm32_flash_h743_2m.ld` origins; ELF `.isr_vector@0x08000000`, `.text@0x08040000`; AP `FLASH_RESERVE_START_KB 128` / app `@0x08020000`. |
| 5. TIM3 motors; bitbang ON; bidir default OFF; ≠ AP DMA | **PASS** | Halo `DEFAULT_DSHOT_BITBANG ON`; PC6–9 TIM3; `DEFAULT_DSHOT_TELEMETRY OFF`; `PWM_TYPE_DSHOT600` default. AP path separate. |
| OEM CLI = 4.5.1 / 77d01ba / 0096077 | **PASS** | CLI header lines; config git short SHA `0096077`. |
| No Halo-named official 4.5.1 hex obtained | **PASS** | Only generic release hex + local reproduction in evidence. |
| VBAT 110/10/1 → AP 11.0; ibata 100 → AP 100 A/V | **PASS** | `voltage.c` defaults; OEM CLI `ibata_scale=100`; conversion formulas documented as uncalibrated. |

## Overclaim / underclaim risks

| Risk | Disposition |
| ---- | ----------- |
| Presenting HSE8 as measured | Avoided — labelled SOFTWARE / HARDWARE_REQUIRED |
| Treating first BF 128K as replaceable bootloader | Avoided — vectors/startup region |
| Treating PR835 as OEM schematic | Avoided — INFERRED |
| Treating local hex as factory image | Avoided — not bit-identical; factory hex missing |
| Claiming AP DShot proved by BF | Avoided |

## HARDWARE_REQUIRED items agreed unresolved

Physical HSE; MCU package/ROM/option bytes; factory image bytes; absolute IMU mount both SKUs; live CS/WHO_AM_I; PE3/9V electrical across reset/DFU; ADC calibration; AP TIM3 DMA/bdshot on ESC; RC/OSD/logger/DFU round-trip.

## Overall

```text
INDEPENDENT_GATE = PASS_FOR_DOCUMENTATION_CLAIMS
WP2B_A_STATUS_RECOMMENDATION = PARTIAL
HARDWARE_FLASH_ALLOWED = NO
```

Research agent cross-check may append notes below without changing these dispositions unless a factual error is found.

## Agent appendix

Parallel read-only gate ([Independent WP2B-A review](7a6258f8-d6e9-49d4-861b-a62ce7d9b6b2)) rechecked the same five claims plus OEM CLI / hex / scale cross-checks against `evidence/wp2b-a/` and the ArduPilot hwdef. Verdict: all claims **PASS**; overall **WP2B_A_STATUS = PARTIAL**; **HARDWARE_FLASH_ALLOWED = NO**.

Additional notes retained from that review (no disposition change):

| Note | Action |
| ---- | ------ |
| Do not treat closed unmerged PR#835 CS map as factory fact without WHOAMI | Already INFERRED in `WP2B_A_IMU_ANALYSIS.md` |
| OEM CLI omits PINIO while docs require it — dump may be incomplete vs live board | Already noted in `WP2B_A_POWER_ADC.md` |
| Community `2026.6.2` Halo hex ≠ official 4.5.1 cloud | Separated in `WP2B_A_BETAFLIGHT_SOURCES.md` |
| AP app `@0x08020000` overlaps BF CONFIG region — flash hazard | Already in `WP2B_A_BOOTLOADER_RECOVERY.md` |

Agreed HARDWARE_REQUIRED set unchanged: physical HSE, absolute IMU + CS/WHOAMI, PE3/9V electrical, ADC calibration, AP TIM3 bdshot, factory flash/DFU identity.
