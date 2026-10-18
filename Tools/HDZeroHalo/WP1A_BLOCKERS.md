# WP1A_BLOCKERS — what still blocks a correct Halo port

**Date:** 2026-10-18

## Severity legend

| Level | Meaning |
|-------|---------|
| **HARD** | Must resolve before flashing / flight trust |
| **SOFT** | Can provisional-default for first compile; fix before flight |
| **NONE** | Not blocking |

## Open items

| ID | Item | Level | Why | Resolution |
|----|------|-------|-----|------------|
| B1 | `OSCILLATOR_HZ` | **HARD** | Wrong HSE → wrong clocks, UART baud, timers | Crystal marking / schematic / measure |
| B2 | `FLASH_RESERVE_START_KB` + storage page | **HARD** | Wrong layout → brick until DFU; param loss | Inspect BF image layout; choose 128 vs 384 KB pattern |
| B3 | Unique `APJ_BOARD_ID` | SOFT | Needed for .apj / BL | Allocate in `board_types.txt` |
| B4 | VBAT scale | SOFT | Wrong voltage reading | Measure divider or OEM value |
| B5 | IMU `ROTATION_*` | SOFT | Attitude error if wrong | Level-bench calibration / visual |
| B6 | PE3 9V polarity | SOFT | VTX power stuck off/on | Scope / BF PINIO behaviour |
| B7 | Exact H743 package | SOFT | Flash size edge cases | Chip marking |
| B8 | DMA resolve at configure | SOFT | Build may fail if over-constrained | Iterate `DMA_NOSHARE` in WP1B |
| B9 | Physical DShot/bdshot | NONE for WP1A | Validation only | Hardware WP later |
| B10 | Prior AP port gaps | NONE | Greenfield port | Expected |

## Not blockers (clarified in WP1A)

- Pinmap for motors, SPI, UART, I2C, ADC, buzzer, LED strip — **available via BF+HDZ**
- Need for new IMU/flash/CRSF/MSP drivers — **not required**
- BF DShot bitbang default — **irrelevant** to ArduPilot timer DMA path
- Absence of analog OSD — **by design**

## Gate for WP1B (first firmware **build**)

Allowed to start WP1B **compile** with:

- Provisional `OSCILLATOR_HZ` clearly marked TODO (do not flash until B1 closed)
- Provisional flash layout matching a chosen peer (document assumption)
- Full pinmap from `WP1A_PINMAP.md`
- Dual IMU probe + W25Q128 dataflash + UART defaults

**Do not flash or motor-test** until B1 and B2 are closed (and DFU recovery verified).
