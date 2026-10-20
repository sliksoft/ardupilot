# WP3-E — HDZero Halo USB-only diagnostic bootloader

> Historical WP3-E evidence, superseded by `WP3_E2_DIAG_BOOTLOADER.md`.
> The original image has two confirmed defects: startup ECC recovery can erase
> application/parameter pages without a host upload, and the ordinary bootloader
> blink timer overwrites marker 4. Its original status claims below are not a
> release approval. The original artifacts remain preserved unchanged.
> Marker 4 means the firmware reached the configuration callback; it does not
> prove completion on Windows or working CDC traffic.

**Date:** 2026-10-20
**HARDWARE_FLASH_ALLOWED = NO**
**Base HEAD:** `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b`
**SAFE_FOR_CODEX_REVIEW = YES**

Evidence (outside Git):
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-e-diag-bootloader/`

This image is isolated from WP3-A and WP3-C. Production
`Tools/bootloaders/HDZeroHalo_bl.*` was not overwritten.

## Status block

```text
HSI64_SYSTEM_CLOCK          = YES (OSCILLATOR_HZ 0 → STM32_HSECLK 0U)
HSE_DISABLED                = YES (STM32_HSE_ENABLED FALSE; no HSEON wait)
USB_HSI48                   = YES (STM32_USBSEL_HSI48_CK; HSI48RDY wait before usbStart)
PLL_CONFIGURATION           = HSI/64 ÷4 ×50 ÷2 = 400 MHz SYSCLK; PLLSRC=HSI
DIAGNOSTIC_LED_MARKERS      = YES (PE2 after GPIO init; stages 1–4 in machine code)
APPLICATION_JUMP_DISABLED   = YES (jump_to_app is bx lr; do_jump absent)
BUILD_STATUS                = PASS
BINARY_SHA256               = b4e74c03bcc62b09439cefe22d84ba5f37de36684789360c9b99f276b7fae4d3
USB_TEST_EXPECTATION        = stay in BL; enumerate 1209:5741 if USB clock path works
KNOWN_LIMITATIONS           = see below
RECOVERY_PROCEDURE          = ROM DFU via physical BOOT; restore WP3-A/C or BF backup
SAFE_FOR_CODEX_REVIEW       = YES
HARDWARE_FLASH_ALLOWED      = NO
```

## Why this variant exists

WP3-A: flashed AP bootloader + ArduCopter; USB enumeration failed; ROM DFU works.
WP3-C: HSI48 USBSEL on the production HSE8 tree; not flashed.
WP3-D: option bytes normal; HSI64 route already present in pinned ChibiOS.

If the production image hangs in `stm32_clock_init()` on `HSERDY`, USB never
starts. This diagnostic bootloader removes that wait and never leaves the
bootloader, so a later hardware test can tell clock-init from USB-enum.

## OSCILLATOR_HZ 0

`chibios_hwdef.py` writes `#define STM32_HSECLK <OSCILLATOR_HZ>U`.
`stm32h7_mcuconf.h` already has a no-crystal branch for `STM32_HSECLK == 0U`:

| Define | Value |
| ------ | ----- |
| `STM32_HSE_ENABLED` | `FALSE` |
| `STM32_HSI_ENABLED` | `TRUE` |
| `STM32_HSIDIV` | `STM32_HSIDIV_DIV1` (64 MHz) |
| `STM32_PLLSRC` | `STM32_PLLSRC_HSI_CK` |
| `STM32_PLL1_DIVM/N/P` | 4 / 50 / 2 → 400 MHz |
| `STM32_HSI48_ENABLED` | `TRUE` |
| `STM32_USBSEL` | `STM32_USBSEL_HSI48_CK` (board override) |

`MCU_CLOCKRATE_MHZ 480` is **not** set. That custom rate is only defined for
HSE multiples of 8 MHz.

ChibiOS `stm32_clock_init()` enables HSE only when `STM32_HSE_ENABLED == TRUE`.
HSI48 is enabled and waited (`HSI48RDY`) inside the same function, before USB.

## Machine-code checks

| Check | Result |
| ----- | ------ |
| Vector SP | `0x20000600` (SRAM + `MAIN_STACK`) |
| Vector Reset | `0x080002e1` (matches ELF entry, Thumb) |
| ELF / ld flash | `0x08000000`, length 128K |
| Image size | 18476 B bin / 18380 text + 92 data |
| Free in 128 KB | 112596 B |
| `jump_to_app` | `bx lr` only; `do_jump` not linked |
| HSEON wait | not present on `RCC->CR` |
| HSI48ON + RDY | `RCC->CR \|= 0x1000`, wait bit 13 |
| PLLCKSELR | `0x00408040` → PLLSRC=00 (HSI), M1=4, M2=8, M3=4 |
| D2CCIP2R USBSEL | bits [21:20] = 11 (HSI48) |
| LED markers | `__early_init` calls marker(1) then clock then marker(2); `init_uarts` waits HSI48RDY then marker(3); `usb_event` CONFIGURED → marker(4) |

## LED markers (PE2, active-low)

GPIO clocks and `VAL_GPIOE_*` are programmed by `stm32_gpio_init()` **before**
`stm32_clock_init()`. A pre-clock marker is therefore safe.

| Stage | When | Pattern |
| ----- | ---- | ------- |
| 1 | after GPIO init, before PLL | 1 flash |
| 2 | after `stm32_clock_init()` | 2 flashes |
| 3 | HSI48 ready, USB start about to run | 3 flashes |
| 4 | host configured the device | solid ON |

Busy-wait length is calibrated for HSI 64 MHz; after the 400 MHz PLL, flashes
are shorter. That is accepted for diagnosis.

PE3 VTX_PWR and PD12 buzzer remain OUTPUT LOW. No motor/ESC/ARM pins.

## Application jump disabled

- `AP_FASTBOOT_ENABLED 0` — no RTC/fastboot path
- `HAL_BOOTLOADER_TIMEOUT 0` — `bootloader()` never times out
- `HAL_BOOTLOADER_NO_APP_JUMP 1` — `jump_to_app()` returns immediately

Host `PROTO_BOOT`, CAN, and network callers all hit the empty `jump_to_app`.
This image cannot start ArduCopter.

## Files changed

| File | Role |
| ---- | ---- |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHaloDiagBL/hwdef-bl.dat` | isolated diagnostic BL |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHaloDiagBL/hwdef.dat` | configure stub only (no motors) |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHaloDiagBL/README.md` | board note |
| `Tools/AP_Bootloader/AP_Bootloader_config.h` | default `NO_APP_JUMP` / `DIAG_LED` = 0 |
| `Tools/AP_Bootloader/bl_protocol.cpp` | guarded empty `jump_to_app` |
| `Tools/AP_Bootloader/support.cpp` | HSI48RDY + marker 3 before USB |
| `libraries/AP_HAL_ChibiOS/hwdef/common/board.h` | `halo_diag_led_marker` prototype |
| `libraries/AP_HAL_ChibiOS/hwdef/common/board.c` | early LED + markers 1–2 |
| `libraries/AP_HAL_ChibiOS/hwdef/common/usbcfg.c` | marker 4 on `USB_EVENT_CONFIGURED` |
| `Tools/autotest/unittest/hdzero_halo_diagbl_unittest.py` | generator/config tests |
| `Tools/HDZeroHalo/PORT_STATUS.md` | WP3-E pointer |
| `Tools/HDZeroHalo/WP3_E_DIAG_BOOTLOADER.md` | this report |

Production `HDZeroHalo/hwdef*.dat` was not edited in this WP.

Guarded shared-code changes compile out unless `HAL_BOOTLOADER_DIAG_LED` /
`HAL_BOOTLOADER_NO_APP_JUMP` are set. GitNexus `impact` on `jump_to_app`,
`__early_init`, and `usb_event` returned **UNKNOWN** (startup / function-
pointer callers). Text search confirmed: `jump_to_app` from `AP_Bootloader.cpp`,
`can.cpp`, `network.cpp`, and `PROTO_BOOT`; `__early_init` from ChibiOS
`crt0_v7m.S`; `usb_event` via `usbcfg`. `init_uarts` impact was LOW.

## Builds and tests

| Target | Result |
| ------ | ------ |
| `./waf configure --board HDZeroHaloDiagBL --bootloader` | PASS |
| `./waf bootloader` | PASS, 18472 B flash used |
| `hdzero_halo_diagbl_unittest.py` | 6/6 PASS |
| `hdzero_halo_unittest.py` (production) | 13/13 PASS |

No copter image was built. No flash, USB reset, erase, or option-byte change.

## Firmware locations

Build output:

- `build/HDZeroHaloDiagBL/bin/AP_Bootloader.bin`
- `build/HDZeroHaloDiagBL/bootloader/AP_Bootloader` (ELF)

Archived (do not mix with WP3-A / WP3-C):

- `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-e-diag-bootloader/after/HDZeroHaloDiagBL_bl.bin`
- `.../HDZeroHaloDiagBL_bl.elf`
- `.../HDZeroHaloDiagBL_bl.hex` (load address `0x08000000`)

| Artifact | Bytes | SHA256 |
| -------- | ----- | ------ |
| `.bin` | 18476 | `b4e74c03bcc62b09439cefe22d84ba5f37de36684789360c9b99f276b7fae4d3` |
| `.elf` | 52096 | `b64bee32b1154cb5a6738b190cb9d02dc6518c5d803610fd731542be1cea63ef` |
| `.hex` | — | `2b0d3b19f082ff8da106c5fd78fc3d99ecba074151d4355a2e8bc12ab9a612e8` |

WP3-C BL remains `Tools/bootloaders/HDZeroHalo_bl.bin` (18924 B).

## USB_TEST_EXPECTATION

After a future reviewed DFU write of **only** this 128 KB bootloader (app and
parameter sectors left alone):

1. Board must remain in the bootloader (no ArduCopter).
2. If the HSI64+HSI48 path works: USB `1209:5741`, PE2 reaches solid ON (stage 4).
3. If it hangs in clock init: at most one flash (stage 1).
4. If clock works but USB does not enumerate: two or three flashes, never solid.

This WP did **not** perform that test.

## KNOWN_LIMITATIONS

- No CRS (same ChibiOS HAL limit as WP3-C). HSI48 is free-running.
- LED busy-wait is not a calibrated timer; post-PLL flashes are shorter.
- Diagnostic image refuses every application jump, including host `PROTO_BOOT`.
- Runtime USB and PE2 observation are untested.
- Does not by itself prove whether the physical HSE crystal exists.
- Shared `board.c` / `usbcfg.c` / `bl_protocol.cpp` hooks exist but are
  compile-time dead on every other board.

## RECOVERY_PROCEDURE

Unchanged from WP2B-H / WP3-A:

1. Hold the physical BOOT button at USB power-on → STM32 ROM DFU (`0483:df11`).
2. Restore the WP3-A or WP3-C ArduPilot bootloader, or the archived Betaflight
   full-flash backup under `evidence/wp3-a-first-usb-boot/backup/`.
3. Do not change option bytes (already verified normal in WP3-D).
4. This diagnostic BL does not erase or program the application/parameter
   sectors unless a host later sends an explicit upload (and even then it will
   not jump to that image).

## SAFE_FOR_CODEX_REVIEW

Yes. Offline source + binary only. No hardware flash. No commit/push/merge.
Ready for independent Codex review before any DFU write.
