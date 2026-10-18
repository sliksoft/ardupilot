# WP2A_HSE — clock-source review correction

**Date:** 2026-10-18  
**Review basis:** `9e8f166ecd17c418d4070d4b6f4b92e7fee6bf8d`
**HARDWARE_FLASH_ALLOWED = NO**

## Corrected conclusion

The earlier claim that omitting `SYSTEM_HSE_MHZ` selects HSI in the normal
Halo Betaflight build was incorrect. It ignored the Makefile default and
compiler definitions. Keep ArduPilot `OSCILLATOR_HZ 8000000` as the provisional
build configuration; the physical clock source on our board remains unverified.

## Betaflight 4.5.1 build chain

Pinned source: tag 4.5.1, commit
`77d01ba3b76a22909d5f09cb0628820141f95eaa`. The official HDZero firmware guide
identifies 4.5.1 as the factory version; this does not identify the exact image
or build overrides installed on a particular board.

| Source | Behaviour |
| -------- | ----------- |
| Halo config at config commit `e0273b9564854e0ee1fbadd8200875b30bd35650` | No `SYSTEM_HSE_MHZ` override |
| `mk/config.mk:30-32` | Sets `HSE_VALUE` when the board supplies that override |
| `Makefile:128` | Otherwise `HSE_VALUE ?= 8000000` |
| `Makefile:195-196`, `mk/mcu/STM32H7.mk:288` | Pass `-DHSE_VALUE=8000000` in an ordinary build |
| `src/main/startup/system_stm32h7xx.c:85-90` | Defined `HSE_VALUE` selects `RCC_PLLSOURCE_HSE` |

The unselected `#if !defined(HSE_VALUE)` branch is an HSI64 fallback, not proof
that the ordinary Halo build takes it. Defaults in `common_post.h` do not undo a
compiler definition. A command-line or OEM build override must be evaluated
separately. ELRS TCXO specifications do not identify the MCU clock source.

## ArduPilot configuration retained

Application: HSE8, CPU 480 MHz; bootloader: HSE8, default H743 CPU 400 MHz.
The bootloader and application initialise their own clock trees. Different CPU
frequencies are supported; they must agree about the physical oscillator.

For the application, `stm32h7_mcuconf.h` gives PLL1P 480 MHz, PLL1Q 80 MHz
for SPI1/2/3, PLL2Q 100 MHz for UARTs/SPI4/5, PLL3Q 48 MHz for USB and PLL3R
32 MHz for I2C. Timers derive their clocks from the configured bus tree.
The bootloader HSE8 path also supplies nominal USB 48 MHz. Build assertions
are retained. These are configured frequencies, not measured board behaviour.

If HSE does not start, ChibiOS waits for HSERDY in `hal_lld.c:293-301`; an
absent or different physical source can prevent boot or invalidate timing.
Ordinary BF source defaults support HSE8 but do not establish the physical part,
RCC state, tolerance or factory-image provenance.

## HSI-only alternative: not implemented

`stm32h7_mcuconf.h:113-122,176-190` already supports `STM32_HSECLK=0`:

- HSI64, PLL1P = `64/4*50/2 = 400 MHz`.
- PLL3Q = `64/4*15/5 = 48 MHz`, selected for USB.
- PLL2Q = `64/8*45/5 = 72 MHz`.

Merely changing `OSCILLATOR_HZ` to zero is not sufficient. The current explicit
480 MHz CPU expectation would fail `system.cpp:47-48`. Even after reconciling
CPU frequency, `STM32H743xx.py:63-68` emits an SPI4/5 expectation of 100 MHz,
which conflicts with 72 MHz and is checked at `system.cpp:76-77`.

A future implementation must reconcile CPU, SPI, UART, timer, USB and generated
clock expectations, build both images, and qualify oscillator accuracy. The
HSI-derived nominal USB clock is not evidence of CRS calibration: enabling
HSI48 does not select it for USB. Do not remove assertions to conceal mismatch.
No hardware modification is intrinsically required by the MCU/HAL HSI path,
but no ready-to-use Halo HSI configuration has been validated here.

## Remaining evidence

Obtain OEM clock information, actual BF RCC/PLL state plus image/build identity,
or a suitable physical inspection/measurement. Clock stability and USB/UART/
DShot timing still require qualification. No such measurement ran in this WP.

## Sources

- [BF 4.5.1 Makefile](https://github.com/betaflight/betaflight/blob/77d01ba3b76a22909d5f09cb0628820141f95eaa/Makefile#L128)
- [BF H7 compiler flags](https://github.com/betaflight/betaflight/blob/77d01ba3b76a22909d5f09cb0628820141f95eaa/mk/mcu/STM32H7.mk#L288)
- [BF PLL source](https://github.com/betaflight/betaflight/blob/77d01ba3b76a22909d5f09cb0628820141f95eaa/src/main/startup/system_stm32h7xx.c#L85)
- [Official Halo config](https://github.com/betaflight/config/blob/e0273b9564854e0ee1fbadd8200875b30bd35650/configs/HDZO/HDZERO_HALO/config.h)
- Local `libraries/AP_HAL_ChibiOS/hwdef/common/stm32h7_mcuconf.h`,
  `hwdef/scripts/STM32H743xx.py`, `system.cpp`, Halo `hwdef*.dat`.
