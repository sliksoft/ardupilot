# WP3-H2: isolate successive reset causes

Date: 2026-10-20. Base HEAD: `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b` plus existing local WP3 changes.
AI-assisted local correction and software verification. No hardware access, flash,
erase, USB reset, commit, push or merge.

```text
RMVF_CLEAR             = PASS
RESET_SNAPSHOT         = PASS
STRLEN                 = PASS
FLASH_SAFETY           = PASS
BUILDS_AND_TESTS       = PASS_SOFTWARE_ONLY; 1_DIAGNOSTIC_BUILD; 28_TESTS
READY_FOR_FINAL_REVIEW = YES_SOFTWARE_ONLY
HARDWARE_FLASH_ALLOWED = NO
```

This report supersedes the reset-flag handling and artifact identity in
`WP3_H_USB_RECOVERY.md`. Earlier reports and images are retained unchanged.
Runtime USB enumeration and physical reset/LED behavior remain unverified.

## Correction and RM0433 contract

Only the diagnostic H7 path (`HAL_BOOTLOADER_DIAG_LED && defined(STM32H7)`)
captures and clears reset flags. At the start of `__early_init`, before GPIO
initialization, it saves all 32 bits of `RCC->RSR`, writes `RCC_RSR_RMVF`
(`0x00010000`) to RSR, then writes `0`. No read-modify-write is used, and
reserved bits are written as zero. Peripheral accesses are volatile and the
final ELF preserves their order.

[STM32H743 RM0433 Rev 8, section 8.7.39, pp. 449-450](https://www.st.com/content/ccc/resource/technical/document/reference_manual/group0/c9/a3/76/fa/55/46/45/fa/DM00314099/files/DM00314099.pdf/jcr%3Acontent/translations/en.DM00314099.pdf)
places RSR at offset `0xD0` and RMVF at bit 16. RMVF is set and reset by
software: 1 resets the flags; 0 releases that reset. Both writes are required
by this implementation so subsequent hardware reset causes can be recorded.

LED interpretation reads only the saved snapshot. Its existing priority is
unchanged: IWDG, WWDG, software, LPWR, BOR without POR, POR/PIN, unknown.
The late watchdog reset-reason cache also uses the snapshot in this diagnostic
build; production still reads its original hardware status register.

## Startup and final ELF evidence

Evidence root: `../evidence/wp3-h2-rmvf/` relative to the repository.

- `crt0_v7m.S` calls `__early_init` before stack filling, DATA copying, BSS
  clearing and `__init_ram_areas`; `__late_init` follows those operations.
  The actual `_crt0_entry` has the same order: early call `0x08000350`, DATA
  loop `0x0800037a`, BSS loop `0x0800038e`, RAM initialization call
  `0x08000398`, late call `0x0800039c`.
- `halo_diag_reset_flags` is four bytes at `0x20004298` in `.ram0`
  (`NOBITS`, `NOLOAD`). `common.ld` places `.ram0.*` at or after
  `__ram0_noinit__`, outside DATA and BSS. BSS ends at `0x20004298`
  (exclusive), and the heap begins at `0x200042a0`.
- The linked RAM initialization boundaries `__ram0_init__`,
  `__ram0_clear__` and `__ram0_noinit__` are all `0x20004298`.
  `crt1.c` initializes only addresses before the no-init boundary. The
  final `__init_ram_areas` likewise copies/clears zero bytes there.
- `__early_init`: `0x08001618` reads RSR; `0x08001620` stores the snapshot;
  `0x08001626` writes `0x10000` to RSR; `0x0800162c` writes zero. GPIO
  register setup follows. `0x080016cc` reloads the snapshot for LED decoding.
- `halo_diag_get_reset_flags` at `0x08001604` loads `0x20004298`.
  `stm32_watchdog_save_reason` calls it at `0x08001c08`, after CRT0.
  It does not reread the cleared RSR.
- `strlen` at `0x08000714` retains the same 14-byte counting loop and
  `bx lr`. `setup_usb_string` still calls it and returns; USB setup and
  diagnostic progress markers 1-4 remain present.

See `verify/disassembly.txt`, `verify/symbols.txt`,
`verify/sections-segments.txt`, `after/Linker.map` and
`verify/artifact-audit.txt` for the captured evidence.

## Builds and regression tests

Only `HDZeroHaloDiagBL` was configured/built, with a new output directory:

```sh
PATH="$PWD/.venv/bin:$PATH" ./waf configure --board HDZeroHaloDiagBL --bootloader --out=build/wp3-h2-rmvf
PATH="$PWD/.venv/bin:$PATH" ./waf bootloader
.venv/bin/python -m unittest Tools.autotest.unittest.hdzero_halo_diagbl_safety_unittest Tools.autotest.unittest.hdzero_halo_diagbl_unittest Tools.autotest.unittest.hdzero_halo_unittest
python3 -m flake8 Tools/autotest/unittest/hdzero_halo_diagbl_safety_unittest.py
git diff --check
```

Build passed without compiler warnings/errors. All 28 tests passed; flake8 and
diff whitespace checks passed. Flake8 is available in system Python, not the
project venv. Logs are in `logs/`.

The new regression first failed against WP3-H because early capture was absent
(`logs/regression-before.log`). It now compiles the actual capture, getter,
LED decoder and watchdog-cache function bodies against a register model.
It verifies one RSR read, snapshot storage before clearing, exact writes
`[RMVF, 0]`, release of RMVF, and no later hardware reads.
POR/PIN/BOR -> BOR/PIN gives pulses 1 -> 2; IWDG/PIN -> software/PIN gives
3 -> 5. Twelve representative cause combinations are exercised in all 144
ordered pairs, including unknown/zero, WWDG, LPWR and mixed causes; additional
CPU/domain flags verify preservation of the complete snapshot.
A separate test verifies unchanged production watchdog-cache behavior.
The register model is software evidence; startup retention is additionally
verified against the real linker layout and machine code above.
An in-memory mutation that removes only the two RMVF writes also fails the
new test at the exact-write assertion (`logs/regression-clear-mutation.log`).
No repository source was changed for that mutation check.

Existing regressions retain `strlen`, USB descriptor initialization, LED
ownership, read-only protocol rejection and diagnostic configuration coverage.

GitNexus impact for the specific startup hook returns `UNKNOWN` because it
does not resolve the assembly caller; the watchdog function was not resolved.
These are coverage limitations, not evidence of unused code. The actual
startup call and late watchdog consumer were verified directly above.
The graph refresh also reports an unavailable full-text index. Raw final
graph-change output is retained in `verify/gitnexus-detect-changes.txt`;
graph results do not replace the source, regression or ELF checks.

## Flash safety, isolation and preservation

The generated diagnostic hwdef is byte-identical to WP3-H: no app jump,
read-only protocol, ECC recovery disabled, no fastboot, timeout zero, HSE off,
USB HSI48, PE3 VTX and PD12 buzzer LOW. Linked code contains only the
identity/synchronization protocol path. `jump_to_app` at `0x08000518` is
still `bx lr`. Flash write/erase/unlock and ECC-recovery symbols are absent.
The 14952-byte BIN fits within the reserved 128 KiB window and exactly matches
the ELF flash LOAD contents with `FF` gap fill.

No production image was rebuilt or replaced. The shipped production ELF
`Tools/bootloaders/HDZeroHalo_bl.elf` still has the OLD four-byte self-branch:
`0x080010bc: f7ff bffe; b.w 0x080010bc <strlen>`. Its BIN remains
`37c43d81c4f32e759337cb4969674b7a69d63611b0c42fb41e4d6682826d91fd`.
The earlier isolated WP3-H production rebuild also remains unchanged.
This correction does not qualify the shipped production image.

The preservation manifest covers 43 existing archived BIN/ELF/HEX files,
including WP3-E2, WP3-H, WP3-F backups and the original Betaflight full-flash
backup (`4d5514333931e47643688560ab32fc4793afd96589112e4617fda53ba06e6533`).
All hashes were rechecked. Production artifacts have a separate before/after
manifest. No submodule sources or production hwdefs were edited.

## New artifacts

| Artifact in `../evidence/wp3-h2-rmvf/after/` | Bytes | SHA256 |
| --- | --- | --- |
| `HDZeroHaloDiagBL_bl.bin` | 14952 | `8d415142b5a2f2ee60782559683b80dea49e7925942525969a29704a38828a77` |
| `HDZeroHaloDiagBL_bl.elf` | 43972 | `d91b9a6a9863738121d24f981a28fefd91d28438546e222f54ac6413895c8d71` |

`READY_FOR_FINAL_REVIEW=YES_SOFTWARE_ONLY` is not hardware authorization.
`HARDWARE_FLASH_ALLOWED=NO` remains in force.
