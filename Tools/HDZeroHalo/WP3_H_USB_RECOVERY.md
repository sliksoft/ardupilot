# WP3-H: HDZero Halo USB-only boot recovery

Date: 2026-10-20. Base HEAD: `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b`.
AI-assisted local implementation and software verification. No commit, push, merge, erase, reset or hardware flash.

```text
STRLEN_ROOT_CAUSE          = GCC_-Os_LOOP_DISTRIBUTE_SELF_TAIL_CALL
STRLEN_FIXED               = YES
OTHER_LIBC_STUBS           = MEMCPY_MEMSET_STRNCMP_RETURN; STRCMP_DISCARDED
RESET_FLAGS_CAPTURE        = YES_RCC_RSR_BEFORE_CLOCK_INIT
LED_DIAGNOSTICS            = LONG_64MHZ_CAUSE_THEN_SHORT_MARKERS
USB_STARTUP_PATH           = STRLEN_RETURNS_MARKERS_1_TO_4_REACHABLE
BUILD_AND_TEST_STATUS      = PASS_SOFTWARE_ONLY
BINARY_SHA256              = c8dad3ee1abfe6a55b8197c83d3e6ad7a90d6d1bfdf02768ca5764cb35da8b0b
FLASH_SAFETY               = PRESERVED_NO_HARDWARE_FLASH
READY_FOR_REVIEW           = YES_SOFTWARE_ONLY
HARDWARE_FLASH_ALLOWED     = NO
```

This report does not authorize a bench flash. Runtime USB enumeration, reset-cause
LED timing on hardware, and the cause of the WP3-F fast-blink loop remain
**UNKNOWN** until one later, separately authorized USB-DFU test.

## Scope

Continue the isolated `HDZeroHaloDiagBL` image from WP3-E2:

1. Repair the proven `strlen()` self-branch that blocked `setup_usb_strings()`.
2. Read STM32H743 `RCC_RSR` immediately after GPIO init and show a long-pulse
   reset-cause pattern before the existing short progress markers.
3. Keep every existing diagnostic safety constraint.

Production `HDZeroHalo` hwdef, shipped `Tools/bootloaders/HDZeroHalo_bl.bin`,
WP3-A through WP3-F images and the original Betaflight full-flash backup were
not overwritten.

Evidence root, outside Git:

`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-h-usb-recovery/`

The earlier strlen-only archive remains at `evidence/wp3-h-strlen-fix/`.

## STRLEN_ROOT_CAUSE

The bootloader supplies its own libc stubs in `Tools/AP_Bootloader/support.cpp`.
The WP3-E2 ELF at `0x08000714` was four Thumb bytes `f7ff bffe` (`b.w strlen`):
an infinite self-tail-call. That is not a newlib/nosys unresolved stub.

GCC `-Os` enables `-ftree-loop-distribute-patterns`. The previous body

```c
while (*s1++) {
    ret++;
}
```

is recognized as `strlen` and rewritten to a call to `strlen`. In this
translation unit the call is the function itself.

Host GCC `-O2` of the same loop became `call strlen@PLT`. ARM GCC `-Os`
produced the exact self-branch seen in the E2 ELF.

## STRLEN_FIXED

The definition now counts with `s1[ret]` and is compiled with
`optimize("no-tree-loop-distribute-patterns")` only on this function.

New ELF `strlen` at `0x08000714` (14 bytes):

```text
08000714 <strlen>:
 8000714:  mov   r3, r0
 8000716:  movs  r0, #0
 8000718:  ldrsb r2, [r3, r0]
 800071a:  cbnz  r2, 800071e
 800071c:  bx    lr
 800071e:  adds  r0, #1
 8000720:  b.n   8000718
```

`setup_usb_string` at `0x080017f0` calls `0x08000714` and returns
(`pop {r4, r5, r6, pc}`). `setup_usb_strings` at `0x08001914` therefore
completes. USB initialisation is no longer blocked on this hang.

## OTHER_LIBC_STUBS

| Stub | Linked | Body |
| --- | --- | --- |
| `memcpy` `0x080006d8` | yes | byte loop, `pop {r4, pc}` |
| `strncmp` `0x080006ec` | yes | compare loop, returns |
| `memset` `0x08000724` | yes | store loop, `bx lr` |
| `strcmp` | no | discarded at map address `0x0` (unused) |

No other libc stub in this image is a self-branch.

## RESET_FLAGS_CAPTURE

STM32H743 reset flags live in `RCC_RSR` at `RCC + 0xD0` (`0x580244D0`), not
in F4-style `RCC_CSR` at `0x74`. Relevant bits:

| Bit | Flag | Meaning |
| --- | --- | --- |
| 26 | `IWDG1RSTF` | Independent watchdog |
| 28 | `WWDG1RSTF` | Window watchdog |
| 21 | `BORRSTF` | Brown-out |
| 23 | `PORRSTF` | Power-on |
| 22 | `PINRSTF` | NRST pin (also set with POR) |
| 24 | `SFTRSTF` | Software reset |
| 30 | `LPWRRSTF` | Illegal low-power entry |
| 16 | `RMVF` | Clear-all (never written) |

A typical power-on sets POR+PIN+BOR together. Isolated BOR is BOR without POR.

`__early_init` reads `RCC->RSR` after `stm32_gpio_init()` and before
`stm32_clock_init()`. ChibiOS `stm32_clock_init()` writes `RCC->CSR`, not
`RSR`, so the flags survive the 400 MHz switch. The diagnostic path does not
write `RMVF`. The bootloader build still skips `stm32_watchdog_clear_reason()`.

The read is a stack local. CRT0 has not cleared BSS yet; the value is not
stored in a global.

ELF proof: after the GPIO table walk, `r2 = 0x58024400` and

```text
80016aa:  ldr.w r3, [r2, #208]   @ 0xd0 = RSR
```

then bit tests that load pulse counts 3/4/5/6/2/1.

## LED_DIAGNOSTICS

Long pulses run only at the reset HSI 64 MHz clock, before marker 1. Each long
delay is three times the existing short marker delay (`3 × 400000` NOPs). Short
markers 1–4 are unchanged.

| Long pulses (64 MHz) | Cause |
| --- | --- |
| 1 | POR and/or PIN (normal power-on / NRST) |
| 2 | BOR without POR |
| 3 | IWDG |
| 4 | WWDG |
| 5 | Software reset |
| 6 | LPWR or unknown |

Then:

| Short marker | Clock | Meaning |
| --- | --- | --- |
| 1 | HSI 64 MHz | GPIO ready |
| 2 | after PLL 400 MHz | `stm32_clock_init()` returned |
| 3 | 400 MHz | `HSI48RDY` and `init_uarts()` |
| 4 | 400 MHz, stays on | USB `CONFIGURED` callback |

Long 64 MHz pulses and short marker 1 share the same clock and are therefore
distinguishable by width. Markers 2–4 are about 6.25× shorter after the PLL.
The LED path uses only `GPIOE->BSRR`; it does not erase or write flash.

## USB_STARTUP_PATH

```text
Reset_Handler
  __early_init
    gpio_init
    RCC_RSR long-pulse cause          (64 MHz)
    halo_diag_led_marker(1)           (64 MHz)
    stm32_clock_init                  (HSI64 PLL 400 MHz, HSE off, USB HSI48)
    halo_diag_led_marker(2)           (400 MHz)
  CRT0 BSS
  __late_init
    setup_usb_strings -> strlen       (now returns)
  main
    flash_init                        (page layout only)
    init_uarts
      wait HSI48RDY
      halo_diag_led_marker(3)
      sduStart / usbStart
    bootloader(0)                     (read-only identity opcodes)
    jump_to_app                       (bx lr, no application jump)
  usb_event(CONFIGURED)
    halo_diag_led_marker(4)           (LED stays on)
```

Generated `hwdef.h`: `STM32_HSECLK 0U`, `STM32_USBSEL_HSI48_CK`,
`HAL_BOOTLOADER_NO_APP_JUMP 1`, `HAL_BOOTLOADER_READ_ONLY 1`,
`HAL_BOOTLOADER_DIAG_LED 1`, `AP_FLASH_ECC_CHECK_ENABLED 0`,
`HAL_BOOTLOADER_TIMEOUT 0`, `AP_FASTBOOT_ENABLED 0`.
`HAL_FLASH_SET_NRST_MODE` is not defined.

## BUILD_AND_TEST_STATUS

- Host tests: 26 passed (`hdzero_halo_diagbl_safety_unittest.py`,
  `hdzero_halo_diagbl_unittest.py`, `hdzero_halo_unittest.py`).
- `flake8` clean on the safety unittest.
- Isolated diagnostic configure/build:
  `./waf configure --board HDZeroHaloDiagBL --bootloader --out=build/wp3-h-usb-recovery`
  then `./waf bootloader`.
- Vectors: SP `0x20000600`, Reset `0x080002e1`.
- Flash span `0x08000000`–`0x08003a47` (14920 bytes) inside the 128 KB
  bootloader window; 116152 bytes free.
- HEX matches BIN. ELF flash LOAD prefix matches BIN.

Shipped production `Tools/bootloaders/HDZeroHalo_bl.bin` remains
`37c43d81…` (18924 bytes, WP3-C). An isolated production rebuild from this
tree is `366463e8…` (18932 bytes) because the shared `strlen` fix is in
`support.cpp`. That rebuild was not copied into `Tools/bootloaders`.
Production hwdef is still HSE 8 MHz, no diagnostic flags. Production
ArduCopter was not rebuilt. `HDZeroHaloDiagBL_bl.bin` was not written into
`Tools/bootloaders`.

## BINARY_SHA256

| Artifact | Bytes | SHA256 |
| --- | --- | --- |
| `HDZeroHaloDiagBL_bl.bin` | 14920 | `c8dad3ee1abfe6a55b8197c83d3e6ad7a90d6d1bfdf02768ca5764cb35da8b0b` |
| `HDZeroHaloDiagBL_bl.hex` | 41064 | `af5f18118732ef14ef79d67862f8514f8e6a70eb76cdd9634b7e158e7c3d313c` |
| `HDZeroHaloDiagBL_bl.elf` | 43844 | `9bd9189d7c948198b5fa6bfa92eb8a8c8368c508c8e197024afdcaa6cd933de9` |

Previous diagnostic BINs (preserved, not overwritten):

| Image | SHA256 |
| --- | --- |
| WP3-E2 | `31c0955898b63a563c8122a4f00d5a648413318fbe5776233ded8a9c514246a2` |
| WP3-H strlen-only | `bf70fab3fdf554cb94fb0e3fc3215775f4d502836bc42e9247edbf7e9d284f6c` |

Original Betaflight backup still
`4d5514333931e47643688560ab32fc4793afd96589112e4617fda53ba06e6533`.

## FLASH_SAFETY

Still compiled out or discarded (map address `0`):

- `flash_write_buffer`, `flash_write_flush`, `flash_func_erase_pages`
- `stm32_flash_erasepage`, `stm32_flash_write`, unlock/keep-unlocked
- `check_ecc_errors`
- option-byte / NRST programmers
- host erase/program/boot opcodes (`HAL_BOOTLOADER_READ_ONLY`)
- `jump_to_app` is two bytes `bx lr` at `0x08000518`

GPIO defaults: PE3 `VTX_PWR` ODR LOW, PD12 buzzer ODR LOW, PE2 LED
active-low. HSE remains disabled on this image; PLL source is HSI64; USB is
HSI48.

`HARDWARE_FLASH_ALLOWED = NO`. No DFU, erase, write, reset or CubeProgrammer
invocation was performed.

## READY_FOR_REVIEW

Software review of this diagnostic image may proceed. A new USB-DFU test is
**not** authorized by this report.

Expected first-look LED sequence if the image stays up after the 400 MHz
switch: long reset-cause pulses, then short marker 1, then faster markers 2
and 3, then marker 4 solid. If the WP3-F fast-blink loop remains, each
re-entry should now start with the long-pulse cause (IWDG=3, BOR=2, POR/PIN=1).
