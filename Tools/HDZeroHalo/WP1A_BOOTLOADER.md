# WP1A_BOOTLOADER — MCU clocks, flash layout, DFU, recovery

**Date:** 2026-10-18  
**Rule:** do **not** invent oscillator frequency or flash layout.

## MCU

| Item | Status | Notes |
|------|--------|-------|
| Family | STM32H743 | BF `FC_TARGET_MCU STM32H743`; HDZ “STM32H743 (480MHz)” |
| Exact orderable part / package | **UNKNOWN** | Verify marking / BOM |
| ArduPilot MCU token | `MCU STM32H7xx STM32H743xx` | All compared H743 boards |
| Core clock goal | 480 MHz | HDZ marketing; ArduPilot often sets `MCU_CLOCKRATE_MHZ 480` |

## Oscillator — UNKNOWN (blocking for correct flash)

| Source | Finding |
|--------|---------|
| HDZero docs | No crystal frequency published |
| Betaflight `HDZERO_HALO/config.h` | No `HSE_VALUE` / `SYSTEM_HSE_MHZ` override |
| Betaflight STM32H7 HAL default | `HSE_VALUE (25000000UL)` in `stm32h7xx_hal_conf.h` — **platform default, not board proof** |
| ArduPilot peer boards | Usually `OSCILLATOR_HZ 8000000`; **AnyleafH7 uses 16000000** (`common.inc` L8) |
| dogjutsu fork `HDZERO_HALO` | Sets 8 MHz claiming BF does — **incorrect claim**; ignore for HSE |

**Verification plan (required before trusting clocks on hardware):**

1. Read marking on the crystal can (optical / photo).
2. Or obtain official schematic / BOM from HDZero.
3. Or measure HSE with a known-good SWD dump / scope (hardware lab).
4. Set `OSCILLATOR_HZ` only after one of the above.

Until then WP1B may use a **provisional** value only for **compile experiments**, never for flight.

## Internal flash / parameter storage

| Item | Typical H743 ArduPilot | Halo |
|------|------------------------|------|
| `FLASH_SIZE_KB` | 2048 | **NEEDS_CONFIG** (assume 2048 pending package confirm) |
| `FLASH_RESERVE_START_KB` | **128** (Lucid/Matek/Anyleaf) or **384** (many FPV: GEPRC/Foxeer/TMotor) | **UNKNOWN** |
| `STORAGE_FLASH_PAGE` | 14 (with 128 KB BL) or 1 (with 384 KB BL patterns) | **UNKNOWN** — must match reserve |
| `HAL_STORAGE_SIZE` | 16384 or 32768 | **NEEDS_CONFIG** after layout choice |

**Verification plan:**

1. Inspect factory Betaflight partition / `bl` size used by HDZERO_HALO firmware builds.
2. Decide ArduPilot layout: native 128 KB BL (Anyleaf/Lucid style) vs 384 KB FPV-style.
3. Ensure parameter pages do not overlap app or BL.
4. Document chosen layout in WP1B hwdef with rationale.

## Board ID

| Item | Status |
|------|--------|
| Existing `AP_HW_*` for Halo | **None** in `Tools/AP_Bootloader/board_types.txt` |
| HDZero manufacturer reservation | **None** found |
| Action for WP1B | Open small PR / local reservation for a unique ID (porting guide Step 1); do not reuse another board’s ID |

## USB DFU

| Item | Evidence | Status |
|------|----------|--------|
| Type-C USB | HDZ product docs | SUPPORTED (hardware) |
| STM32 ROM DFU | HDZ `halo-firmware.md` BOOT-button DFU procedure | SUPPORTED |
| ArduPilot `ENABLE_DFU_BOOT` | Common in `hwdef-bl.dat` (e.g. Lucid BL L56) | NEEDS_CONFIG in Halo BL |
| OTG pins | Standard PA11/PA12 on H743 peers; **not listed in BF config.h** | **DER** — confirm on schematic |

## Safe return to Betaflight

| Path | Notes | Status |
|------|-------|--------|
| Hold **BF BOOT** + USB → STM32 DFU → flash BF `HDZERO_HALO` | Documented by HDZero (`halo-firmware.md`) | SUPPORTED procedure (vendor) |
| ELRS BOOT button | Separate ESP32 RX recovery; not MCU BL | HDZ docs |
| ArduPilot bootloader UART/USB | Will coexist once AP BL installed; keep DFU path documented | NEEDS_CONFIG |

**Risk:** wrong `FLASH_RESERVE_START_KB` / load address can brick until DFU reflash. Always keep DFU recovery steps in board README.

## Clock / ChibiOS timer notes

- Peer boards use `STM32_ST_USE_TIMER 12` + 16-bit resolution (Lucid L19–21, Anyleaf L11–13).
- Do not share the system timer with motor TIM3.

## Summary statuses

| Topic | Status |
|-------|--------|
| MCU family H743 | SUPPORTED (docs) |
| Oscillator Hz | **UNKNOWN** |
| Flash size 2 MB | NEEDS_CONFIG (high confidence DER) |
| BL / param layout | **UNKNOWN** |
| USB DFU recovery to BF | SUPPORTED (vendor procedure) |
| AP board ID | NEEDS_CONFIG (allocate) |
