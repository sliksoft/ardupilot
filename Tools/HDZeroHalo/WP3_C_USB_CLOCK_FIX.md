# WP3-C — HDZero Halo USB clock fix (offline)

**Date:** 2026-10-19  
**HARDWARE_FLASH_ALLOWED = NO**  
**Base HEAD:** `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b`

Evidence (outside Git):  
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-c-usb-clock-fix/`

## Research summary

| Stack | USB 48 MHz source | CRS |
| ----- | ----------------- | --- |
| Betaflight H7 (Halo) | `RCC_USBCLKSOURCE_HSI48` | Configured (SOF sync) |
| ArduPilot H743 default (`stm32h7_mcuconf.h`) | `STM32_USBSEL_PLL3_Q_CK` (from HSE tree) | None |
| ChibiOS H7 type1 | Supports `STM32_USBSEL_HSI48_CK`; enables `HSI48ON` | **No CRS driver in this tree** |
| ArduPilot H723/type2 / H7A3 | Already default to HSI48 USB | None |

HSI48 **selection and enable** are supported and used by other ArduPilot H7
variants. Full **HSI48 + CRS** like Betaflight is **not** available without new
HAL code. This WP selects HSI48 only (no invented CRS).

### HSE-before-USB ordering

`hal_lld.c` waits forever on `HSERDY` **before** starting HSI48. If HSE never
becomes ready, this USBSEL change never runs. The fix addresses wrong/skewed
HSE-derived 48 MHz after a successful HSE lock; it does **not** cure an HSE
start hang.

## Files changed

| File | Change | Why |
| ---- | ------ | --- |
| `libraries/AP_HAL_ChibiOS/hwdef/common/stm32h7_mcuconf.h` | Wrap default `STM32_USBSEL` in `#ifndef` | Allow board override (same pattern as `STM32_QSPISEL`); default remains PLL3Q |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat` | `define STM32_USBSEL STM32_USBSEL_HSI48_CK` | App USB clock = HSI48 |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef-bl.dat` | same | Bootloader USB clock = HSI48 |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/README.md` | Document USB clock row | Board docs |
| `Tools/autotest/unittest/hdzero_halo_unittest.py` | Assert HSI48 USBSEL | Regression |

**Unchanged:** `OSCILLATOR_HZ`, PLL1/2/3 dividers, flash layout, USB pins,
sensors, baro options.

## Builds

| Target | Result | SHA256 (bin) |
| ------ | ------ | ------------ |
| Bootloader | PASS, 18924 B | `37c43d81c4f32e759337cb4969674b7a69d63611b0c42fb41e4d6682826d91fd` |
| ArduCopter | PASS, 1240624 B | `e77572622045d06ede900bc9170c2f1bd9b23d5a92ec352257abfdd47cfdd456` |
| Unit tests | 13/13 PASS | — |

WP3-A images preserved under `evidence/wp3-c-usb-clock-fix/preserved-wp3a/`
(BL `a2efe9fe…`, app `c8d5b022…`, BF fullflash `4d551433…`).

## Status block

```text
HSI48_USB_SUPPORTED = YES_SELECTION_AND_ENABLE; CRS_NOT_IN_CHIBIOS_HAL
BOOTLOADER_CLOCK_FIX = PASS (STM32_USBSEL_HSI48_CK)
APPLICATION_CLOCK_FIX = PASS (STM32_USBSEL_HSI48_CK)
BUILDS_PASS = YES
HSE_DEPENDENCY_REMAINING = YES (SYSCLK/PLL still HSE; HSERDY before HSI48)
EXPECTED_USB_ENUMERATION = IMPROVED_IF_HSE_LOCKS; UNCHANGED_IF_HSE_HANGS
REMAINING_UNCERTAINTY = physical HSE; no CRS vs BF; runtime USB untested
NEXT_HARDWARE_TEST = DFU flash new BL+app only after review; expect 1209:5741; no flight
HARDWARE_FLASH_ALLOWED = NO
```
