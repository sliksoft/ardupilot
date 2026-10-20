# WP3-E2: diagnostic bootloader safety correction

Date: 2026-10-20. Base HEAD: `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b`.
AI-assisted local implementation and software verification. No commit or push.

```text
WP3_E2_STATUS                         = PASS_SOFTWARE_ONLY
AUTONOMOUS_FLASH_ERASE_DISABLED        = YES
HOST_FLASH_WRITE_DISABLED              = YES
PRODUCTION_ECC_UNCHANGED               = YES
PE2_EXCLUSIVE_DIAGNOSTIC_CONTROL       = YES
USB_MARKER_4_SEMANTICS                 = CONFIGURATION_CALLBACK_REACHED_ONLY
HSI64_CLOCK                           = YES_STATIC_400MHZ_SYSCLK
HSE_DISABLED                          = YES
USB_HSI48                             = YES_STATIC
BUILDS_AND_TESTS                      = PASS
BINARY_SHA256                         = 31c0955898b63a563c8122a4f00d5a648413318fbe5776233ded8a9c514246a2
PRODUCTION_REGRESSION                  = PASS_HALO_BYTE_IDENTICAL_AND_TBS_BUILD
SAFE_FOR_CODEX_REVIEW                  = YES
HARDWARE_FLASH_ALLOWED                = NO
```

Runtime clock lock, electrical output levels, USB enumeration and Windows CDC
operation remain **UNKNOWN**. This report does not authorize a bench flash.

## Scope and evidence

Only the diagnostic safety correction is added to the existing WP3-C/WP3-E
working tree. WP3-C production hwdefs, clock overrides and shipped production
bootloader artifacts were not changed by WP3-E2. The original WP3-E artifacts
and Betaflight full-flash backup are preserved.

Evidence root, outside Git:

`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-e2-diag-bootloader/`

- `before/`: pre-E2 protocol, support, config and diagnostic bootloader hwdef.
- `after/`: diagnostic BIN, ELF, HEX, generated header, linker script and hashes.
- `verify/disassembly.txt`: complete disassembly of the archived ELF.
- `verify/symbols.txt`, `verify/segments.txt`: symbols and ELF load layout.
- `verify/artifact-audit.txt`: payload, vectors, clock, GPIO and preservation checks.
- `verify/production-regression.json`: production byte comparisons and ECC/LED symbols.
- `logs/`: configure/build logs, failing pre-fix probes and passing final tests.

## Autonomous and host flash mutation

`HDZeroHaloDiagBL/hwdef-bl.dat` explicitly sets
`AP_FLASH_ECC_CHECK_ENABLED 0` and `HAL_BOOTLOADER_READ_ONLY 1`.
The normal H7 ECC default in `Tools/AP_Bootloader/support.h` is untouched.
The new read-only mode defaults to zero. Compile-time checks reject read-only
mode with ECC recovery enabled, application jumping enabled, fastboot enabled
or a nonzero bootloader timeout.

The diagnostic protocol is compiled separately from the existing programming
protocol. It accepts only:

| Opcode | Operation |
| --- | --- |
| `0x21` | GET_SYNC, followed by EOC |
| `0x22` | GET_DEVICE scalar arguments 1, 2, 3, 4 and 6, followed by EOC |
| `0x2c` | GET_CHIP, followed by EOC |

Every other opcode returns `INSYNC/INVALID`. In particular erase, full erase,
program, CRC-with-flush, boot/finalize, boot-delay writes, external flash and
baud-changing commands are not compiled into the diagnostic handler. GET_DEVICE
vector-area reads, application reads and OTP reads are also unavailable. This
image is not an uploader target, despite retaining the existing board ID/VID/PID.

In the final ELF, `main` at `0x080004f4` calls only `flash_init`, `init_uarts`,
`bootloader(0)` and the no-op `jump_to_app` inside its main loop. `flash_init`
only computes the page layout; it does not program flash. The diagnostic handler
at `0x0800051c` is 176 bytes and dispatches only the three opcodes above.

The following are absent from the linked diagnostic machine code:

- `check_ecc_errors`, `check_ecc_flash_region`;
- `stm32_flash_erasepage`, `stm32_flash_write`, flash unlock/keep-unlocked,
  unprotect and option-byte setters;
- `flash_write_buffer`, `flash_write_flush`;
- `do_jump`, the ordinary protocol LED timer and generic LED functions.

The remaining `stm32_flash_*` functions only return page size/count. The flash
controller base literal occurs in clock setup for FLASH_ACR, not erase/program
control. SD, CAN, network and custom board programming startup paths are not
enabled; HAL_FLASH_PROTECTION is zero and no NRST option-byte hook is configured.
USB CDC control requests retain ordinary line-coding/control behavior and do not
add a flash writer. Watchdog-reason bookkeeping is not application/parameter flash.

Consequently the compiled diagnostic program has no autonomous or host-accessible
program/erase route into `0x08020000` and above, including parameter sectors
14-15. This is static machine-code evidence; no hardware readback was performed.

## Exclusive PE2 control and marker interpretation

For diagnostic LED mode, generic `led_on`, `led_off` and `led_toggle` perform no
GPIO operation. The read-only protocol does not instantiate the ordinary blink
timer; the generic LED functions and timer are discarded from the final ELF.
For ordinary boards the existing LED implementation remains active.

All reachable GPIOE writes in this image are accounted for:

1. Early `gpio_init` at `0x08001558` programs the GPIOE defaults. It writes ODR
   before MODER. GPIO clocks were enabled first.
2. `halo_diag_led_marker.part.0` at `0x08001594` writes only PE2 BSRR set/reset
   masks `0x4` and `0x40000` for markers 1-3.
3. `halo_diag_led_marker` at `0x080015cc` writes `0x40000` for marker 4.

The only direct GPIOE base literals after initialization belong to those two
marker functions. `_pal_lld_init` at `0x08001ca4` is `bx lr`; no later PAL setup
overwrites the GPIO defaults. No generic LED routine is linked.

| Marker | Verified call site | Meaning |
| --- | --- | --- |
| 1 | `0x080016a2` | GPIO setup completed, before clock initialization |
| 2 | `0x080016ac` | `stm32_clock_init` returned |
| 3 | `0x0800074a` | HSI48 ready; USB initialization about to start |
| 4 | `0x08001850` | USB configuration callback reached |

Marker 1 uses flash constants, stack-local delay state and direct GPIO writes;
it does not depend on initialized BSS/data or an RTOS timer. Delay pulses remain
uncalibrated and shorter after the PLL switch.

**Marker 4 is a latched record that this callback was reached since startup.**
It precedes endpoint setup and the USB status transfer. It is not cleared on USB
suspend/unconfiguration and does not establish current host connectivity.
Successful Windows enumeration and any CDC exchange must be confirmed separately.
There is no claim of successful hardware USB operation.

## Clock, vectors and output safety

The complete 384-byte `stm32_clock_init` machine code is byte-identical to the
independently reviewed WP3-E function, relocated to `0x080028e8`:

- HSE is disabled, with no HSEON activation or HSERDY loop in the startup path.
- HSI64 is the PLL source: M1=4, N1=50, P1=2, nominal SYSCLK=400 MHz.
- HCLK=200 MHz, VOS1, LDO supply mode, FLASH_ACR latency=2 WS.
- HSI48 is enabled and HSI48RDY is awaited before USB initialization.
- USBSEL bits 21:20 are `11`, selecting HSI48.

The GPIO default table is also byte-identical to WP3-E. PA11/PA12 remain AF10;
PE2, PE3 VTX_PWR and PD12 BUZZER remain push-pull outputs initialized LOW. The
markers affect PE2 only. Physical reset/ROM-DFU output levels remain UNKNOWN.

`jump_to_app` at `0x08000518` is exactly `bx lr`. Fastboot is disabled, the
timeout is zero, and PROTO_BOOT is rejected. No alternate application entry
routine is linked.

Unbounded PWR/HSI/HSI48/PLL/clock-switch waits and free-running HSI48 without CRS
remain diagnostic limitations. Negative USB results cannot identify one unique
cause. These retained limitations are not presented as hardware successes.

## Builds and regression tests

All commands ran from the repository root using the existing `.venv/bin`
on PATH. The final diagnostic build used a new, empty output directory; no
original build or archived WP3-E artifact was cleaned or overwritten.

| Check | Result |
| --- | --- |
| Clean HDZeroHaloDiagBL configure + bootloader build | PASS, `build/wp3-e2-diag-final/HDZeroHaloDiagBL` |
| Diagnostic generated configuration tests | 8/8 PASS |
| Native actual-function protocol/LED regression probes | 2/2 PASS |
| Existing production Halo configuration tests | 13/13 PASS |
| Modified/new Python files: flake8 | PASS |
| `git diff --check` | PASS |
| Clean normal HDZeroHalo bootloader build | PASS; BIN byte-identical to WP3-C |
| Clean normal HDZeroHalo ArduCopter build | PASS; BIN byte-identical to WP3-C |
| TBS_LUCID_H7 bootloader build | PASS |

The native protocol probe covers all 256 opcode values, all 256 GET_DEVICE
arguments, valid requests, malformed/truncated input and attempted erase/program/
boot sequences. No flash-mutation implementations are supplied to that harness.
The LED probe compiles the actual support/marker functions in both diagnostic
and production modes; it verifies marker patterns, 6,000 generic LED calls and
retention of production LED behavior. The diagnostic PE2 probe failed before
the fix; the old programming handler could not satisfy the read-only harness.
ECC tests check the generated diagnostic override and the unchanged actual H7
default from support.h. These are offline tests, not MCU execution.

Initial environment/build issues were corrected: system Python lacked empy;
the first production build exposed a missing explicit bootloader-config include.
Final builds use the project venv and include the config directly. The production
ECC macro test uses preprocessing, matching its `defined(...)` macro contract.

The normal bootloader retains ECC scan/erase, flash programming, `sys_tick_handler`
and `led_toggle`. Its BIN is 18,924 bytes with SHA256
`37c43d81c4f32e759337cb4969674b7a69d63611b0c42fb41e4d6682826d91fd`.
The normal ArduCopter BIN is 1,240,624 bytes with SHA256
`e77572622045d06ede900bc9170c2f1bd9b23d5a92ec352257abfdd47cfdd456`.
Both exactly match the pre-E2 WP3-C archives. No exhaustive all-board build
matrix was run; the zero-default guards and additional TBS build bound that claim.

GitNexus impact was queried before source edits; several startup/protocol callers
were unresolved and were checked in source. Index refresh completed with FTS and
flow-coverage warnings. Final detect_changes also returned mismatched display
names for symbol IDs, so its risk summary is not treated as proof of isolation.
Source comparison, native tests and the actual linked images are authoritative.

## Artifact integrity and preservation

| Artifact | Bytes | SHA256 |
| --- | --- | --- |
| HDZeroHaloDiagBL_bl.bin | 14808 | `31c0955898b63a563c8122a4f00d5a648413318fbe5776233ded8a9c514246a2` |
| HDZeroHaloDiagBL_bl.elf | 43792 | `f4042e3280f4e58183a7ff8c09d74e8b78d7a67e4bc8c77f85bccd9c6560f464` |
| HDZeroHaloDiagBL_bl.hex | 41705 | `0bdcd0f2cc1a2a0ef6fcdd3db23f89a2f51010dfeb846927990b09162a64902c` |

The BIN matches every file-backed ELF load segment. HEX was generated from BIN
with explicit base `0x08000000`; every HEX record checksum and every payload byte
matches, including the four BIN alignment bytes. Image span is
`0x08000000-0x080039d7`, leaving 116,264 bytes within the 128 KB reservation.
Stackpointer is `0x20000600`; resetvector and ELF entry are `0x080002e1`.
The linker flash origin and length remain `0x08000000`, 128K.

The fresh final build BIN and ELF match the archived E2 files byte-for-byte.
The original WP3-E BIN remains SHA256
`b4e74c03bcc62b09439cefe22d84ba5f37de36684789360c9b99f276b7fae4d3`.
The 2,097,152-byte Betaflight backup remains SHA256
`4d5514333931e47643688560ab32fc4793afd96589112e4617fda53ba06e6533`.
Both hashes were recomputed. WP3-A/WP3-C backups and shipped production artifacts
were retained. The existing application and parameter sectors were not accessed
on hardware by this work.

## Handoff

Ready for a new independent Codex review of the E2 source and exact archived
image. No hardware flash, erase, USB reset, option-byte change, commit, push or
merge was performed. **HARDWARE_FLASH_ALLOWED=NO**.
