# WP3-J: HDZero Halo production USB boot recovery

Date: 2026-10-20. Base HEAD: `c1a1fc2d9e4ac6b877081c4586ef0a31eff7d97b` plus prior
local WP3 changes. AI-assisted software implementation and offline verification.
**No hardware flash, erase, USB takeover, option-byte change, commit, push or merge.**

```text
PRODUCTION_BOOTLOADER_BUILD     = PASS_SOFTWARE_ONLY
PRODUCTION_STRLEN_FIXED         = PASS_ELF_VERIFIED
BOOTLOADER_HSI64                = PASS_SOFTWARE_ONLY
BOOTLOADER_USB_HSI48            = PASS_SOFTWARE_ONLY
NORMAL_APP_JUMP                 = PASS_SOURCE_AND_ELF
ARDUCOPTER_BUILD                = PASS_SOFTWARE_ONLY
ARDUCOPTER_CLOCK_CONFIGURATION  = PASS_HSI64_400MHZ_SOFTWARE_ONLY
ARDUCOPTER_LIBC_AUDIT           = PASS_NO_SELF_BRANCH
MAVLINK_USB_CONFIGURATION       = PASS_SOFTWARE_DEFAULTS
IMU_CONFIGURATION               = PASS_UNCHANGED
FLASH_LAYOUT                    = PASS_SOFTWARE_ONLY
FLASH_SAFETY                    = PASS_SOFTWARE_ONLY
PRODUCTION_REGRESSION           = PASS_29_TESTS
NEW_BOOTLOADER_SHA256           = 4f92d710e21be29daed876084be9db7045e6f29ef08d290c4f9ab0253cb1d52f
NEW_ARDUCOPTER_SHA256           = ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7
REMAINING_RISKS                 = SEE_BELOW
READY_FOR_INDEPENDENT_REVIEW    = YES_SOFTWARE_ONLY
RECOMMENDED_FIRST_HARDWARE_TEST = SEE_BELOW
HARDWARE_FLASH_ALLOWED          = NO
```

Evidence root (outside Git):
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp3-j-production-usb-boot/`

## Goal and scope

Bring the normal `HDZeroHalo` production bootloader and ArduCopter application onto
the same HSI64 SYSCLK + HSI48 USB path proven on hardware by WP3-I’s diagnostic
bootloader, while restoring normal application jump and firmware-update behaviour.

This WP does **not** flash hardware. A successful build or DiagBL enumeration is
**not** proof that Mission Planner will yet see a MAVLink HEARTBEAT.

## What changed

| File | Change |
| ---- | ------ |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef-bl.dat` | `OSCILLATOR_HZ 0` (HSI64 → 400 MHz); keep USB HSI48; **no** DiagBL flags |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat` | `OSCILLATOR_HZ 0`; remove unproven `MCU_CLOCKRATE_MHZ 480`; keep USB HSI48 |
| `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/README.md` | Document HSI64 software path |
| `Tools/autotest/unittest/hdzero_halo_unittest.py` | Assert HSI64 + no 480 MHz + no DiagBL flags on production |
| `Tools/autotest/unittest/hdzero_halo_diagbl_unittest.py` | Isolation now by protocol/jump flags (both boards share HSI64) |
| `Tools/bootloaders/HDZeroHalo_bl.{bin,elf,hex}` | Rebuilt production BL (old WP3-C image preserved under evidence) |

**Already present from WP3-H (shared, production-safe):**

- `Tools/AP_Bootloader/support.cpp` `strlen()` with
  `optimize("no-tree-loop-distribute-patterns")` and `s1[ret]` counting loop.
- Board-local USBSEL override via `#ifndef STM32_USBSEL` in `stm32h7_mcuconf.h`.
- Diag-only hooks in `board.c` / `usbcfg.c` / `bl_protocol.cpp` remain
  compile-time dead unless DiagBL flags are set.

**Not carried into production:** `HAL_BOOTLOADER_NO_APP_JUMP`,
`HAL_BOOTLOADER_READ_ONLY`, `HAL_BOOTLOADER_DIAG_LED`, `AP_FLASH_ECC_CHECK_ENABLED 0`,
timeout/fastboot zeroing.

## Clock configuration (software)

ChibiOS `STM32_HSECLK 0U` path (`stm32h7_mcuconf.h`):

| Item | Value |
| ---- | ----- |
| HSE | disabled |
| HSI | enabled (64 MHz) |
| PLLSRC | HSI |
| PLL1 | M=4, N=50, P=2 → **400 MHz SYSCLK** |
| VOS | Scale1 + `STM32_ENFORCE_H7_REV_XY` |
| Expected HCLK | 200 MHz (HPRE /2) |
| Flash latency | 2 WS at 200 MHz VOS1 (≤ 210 MHz 2WS threshold) |
| USB | `STM32_USBSEL_HSI48_CK`; `STM32_HSI48_ENABLED TRUE` |
| Custom 480 MHz | **absent** (HSE-only; rejected for Halo) |

Generated headers confirm `#define STM32_HSECLK 0U` and
`#define STM32_USBSEL STM32_USBSEL_HSI48_CK` for both BL and app.
Both binaries contain PLLCKSELR immediate `0x00408040` (HSI, M1=4, M2=8, M3=4).
`stm32_clock_init` enables HSION and HSI48ON; no HSERDY wait in the clock-init
excerpt.

Bootloader and application each run their own RCC init after reset / jump.
On jump, production `jump_to_app` disables D/I-cache, resets OTG FS, disables
IRQs, programs `SCB_VTOR` to `0x08020000`, then loads MSP/entry from the app
vector table.

## PRODUCTION_STRLEN_FIXED / libc audit

Shipped WP3-C production BL still had the broken self-branch
(`0x080010bc: f7ff bffe; b.w strlen`). That image is preserved.

New production ELF `strlen` at `0x080010bc`:

```text
080010bc <strlen>:
 80010bc:  mov   r3, r0
 80010be:  movs  r0, #0
 80010c0:  ldrsb r2, [r3, r0]
 80010c2:  cbnz  r2, 80010c6
 80010c4:  bx    lr
 80010c6:  adds  r0, #1
 80010c8:  b.n   80010c0
```

Bootloader scan: **zero** infinite self-branch stubs among libc replacements.
Application (newlib) `strlen` / `memset` / `memcpy` / `strcpy` / `strcmp`: no
self-branches.

## NORMAL_APP_JUMP

Source: `jump_to_app()` is **not** wrapped in an early return for production
(`HAL_BOOTLOADER_NO_APP_JUMP` defaults 0).

ELF: `jump_to_app` at `0x08000670` is a full validation + VTOR + `do_jump` path
(push/validate lead words/entry range/APB disable/OTG reset/`cpsid`/VTOR
`0xe000ed08`/cache disable). Not the DiagBL `bx lr` stub.

`APP_START_ADDRESS` = `0x08000000 + 128 KiB` = `0x08020000`.
App ELF LOAD at `0x08020000`; reset vector `0x08020db9` in range.
BL ELF LOAD at `0x08000000`; BIN 18916 B ≪ 128 KiB sector 0.

ECC recovery symbols remain linked (`check_ecc_errors`, flash write/erase).

## MAVLINK_USB_CONFIGURATION

- `SERIAL_ORDER` starts with `OTG1` → SERIAL0 = USB CDC.
- Upstream default: `DEFAULT_SERIAL0_PROTOCOL SerialProtocol_MAVLink2`
  (`AP_SerialManager.cpp`) when board does not override (Halo does not).
- USB IDs: `0x1209/0x5741`; product strings `HDZeroHalo-BL` (BL) /
  `HDZeroHalo` (app); manufacturer `ArduPilot`.
- Pins PA11/PA12 OTG FS unchanged.

**Hardware HEARTBEAT is untested.** Software configuration only.

## IMU_CONFIGURATION

Unchanged from WP2B-D / WP2B-G:

- ICM42688P (+ MPU6000 probe) on SPI1, `ROTATION_ROLL_180` / `ROTATION_YAW_270`
- DShot300 via `MOT_PWM_TYPE 5`, TIM3 BIDIR DMA
- `HAL_BARO_ALLOW_INIT_NO_BARO 1`
- PE3 VTX_PWR / PD12 buzzer OUTPUT LOW
- No new arming bypass

## FLASH_LAYOUT / FLASH_SAFETY

| Region | Address | Notes |
| ------ | ------- | ----- |
| Bootloader | `0x08000000`–`0x0801FFFF` | 128 KiB; new BL 18916 B |
| Application | `0x08020000` | LOAD verified |
| Parameters | `STORAGE_FLASH_PAGE 14` → `0x081C0000` | `HAL_STORAGE_SIZE 32768` |
| ROM DFU | physical BOOT | unchanged; software DFU entry still disabled |

No RDP/option-byte edits. No external SPI flash changes.
Sector-0-only DFU can replace DiagBL with this production BL without touching
app/params (same procedure as WP3-I).

Preserved hashes rechecked:

| Artifact | SHA256 |
| -------- | ------ |
| WP3-H2 DiagBL (authorized HW image) | `8d415142…882a77` |
| Prior production BL (WP3-C, broken strlen) | `37c43d81…6d91fd` |
| Original Betaflight full-flash backup | `4d551433…6e6533` |

## Builds and regression

```sh
PATH="$PWD/.venv/bin:$PATH" ./waf configure --board HDZeroHalo --bootloader --out=build/wp3-j-bl
PATH="$PWD/.venv/bin:$PATH" ./waf bootloader
PATH="$PWD/.venv/bin:$PATH" ./waf configure --board HDZeroHalo --out=build/wp3-j-app
PATH="$PWD/.venv/bin:$PATH" ./waf copter
.venv/bin/python -m unittest Tools.autotest.unittest.hdzero_halo_unittest \
  Tools.autotest.unittest.hdzero_halo_diagbl_unittest \
  Tools.autotest.unittest.hdzero_halo_diagbl_safety_unittest
```

| Target | Result |
| ------ | ------ |
| Production bootloader | PASS, 18916 B flash used |
| ArduCopter | PASS, 1240520 B flash used |
| Unit tests | **29/29 PASS** |
| flake8 (modified unittests) | PASS |
| `git diff --check` (touched paths) | PASS |

## New artifacts

| Artifact in `evidence/wp3-j-production-usb-boot/after/` | Bytes | SHA256 |
| --- | ---: | --- |
| `HDZeroHalo_bl.bin` | 18916 | `4f92d710e21be29daed876084be9db7045e6f29ef08d290c4f9ab0253cb1d52f` |
| `HDZeroHalo_bl.elf` | 52216 | `3c8397a97b0b64688e48c7e6ae75231beff8bb630a7f90b74f33b7b33b5112ed` |
| `arducopter.bin` | 1240584 | `ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7` |
| `arducopter.elf` | 2583916 | `5d9af4f77d2fc621b31efeef5d4cffccff1895adff5dbfdca007fe7573acef62` |
| `arducopter_with_bl.hex` | — | `de0ec48db7bb7aaaf8fe55e1fdd3006966e614504d89624cd5f9a51228471e88` |

Also copied to `Tools/bootloaders/HDZeroHalo_bl.*` (old image under `preserved/`).

## Shared-code impact

Halo clock changes are **board-local** (`HDZeroHalo` hwdefs only).
Shared `strlen` fix and USBSEL `#ifndef` were already in-tree from WP3-H/C and
apply to all bootloaders / boards that rebuild; Diag hooks remain gated.
GitNexus `impact` on startup/USB symbols returns `UNKNOWN` (index limitation);
callers confirmed by text search and ELF. `detect_changes` risk **low** for
indexed diag symbols; does not replace ELF/regression evidence.

## Distinction: software-proven vs hardware-untested

| Claim | Status |
| ----- | ------ |
| Production BL builds with HSI64 + HSI48 + fixed strlen | Software proven |
| Production BL retains normal jump + ECC + flash protocol | Software / ELF proven |
| ArduCopter builds with HSI64 400 MHz + HSI48 USB + MAVLink2 on SERIAL0 | Software proven |
| DiagBL USB enum on Halo (WP3-I) | Hardware proven (prior WP) |
| Production BL USB enum after flash | **Not tested** |
| App jump + ArduCopter start + HEARTBEAT | **Not tested** |
| Fast green LED on DiagBL | Still unexplained (WP3-I) |
| Physical HSE crystal | Unused by this software path; still unknown |

## REMAINING_RISKS

1. On-device application is still the older HSE-dependent image until a separate
   app program. Flashing **only** the new BL onto a board that still has the
   WP3-C app yields a clock mismatch on jump (BL HSI64 → app expects HSE).
2. HSI48 without CRS (ChibiOS HAL limit) may affect long USB sessions.
3. DiagBL fast green blink cause unknown; may reappear or differ under production LED use.
4. First production BL timeout (default 5 s) will attempt app jump — if app is
   old/HSE, may hang; keep ROM DFU recovery ready.
5. 400 MHz vs prior 480 MHz timing: timers/DShot/baud derived from SYSCLK need
   bench confirmation (software tree is consistent at 400 MHz).

## Recommended programming plan (DO NOT EXECUTE in this WP)

**HARDWARE_FLASH_ALLOWED = NO** until independent review authorizes a trial.

### Step A — Bootloader only (preferred first flash)

Same as WP3-I sector-0-only DFU:

1. Physical BOOT → ROM DFU (`0483:df11`).
2. Backup full flash if not already archived.
3. `-e 0` (sector 0 only) then `--skipErase -d HDZeroHalo_bl.bin 0x08000000 -v`.
4. Cold start **without** BOOT: expect `1209:5741`, product `HDZeroHalo-BL`,
   ArduPilot bootloader COM port (not DiagBL string).
5. Do **not** expect MAVLink HEARTBEAT from the bootloader alone.

### Step B — Application (separate image; only after Step A review)

1. ROM DFU again (or use working BL protocol once verified).
2. Program `arducopter.bin` at **`0x08020000` only** (do not mass-erase).
3. Leave parameter pages (`0x081C0000+`) intact unless intentionally wiping.
4. Cold start: expect USB re-enum as `HDZeroHalo`, then Mission Planner
   MAVLink HEARTBEAT on SERIAL0.
5. Bench only: no arm, no motors, no flight.

Alternative: `arducopter_with_bl.hex` programs BL+app together — higher risk;
prefer staged A then B.

## RECOMMENDED_FIRST_HARDWARE_TEST

After independent review authorization:

1. Sector-0-only DFU of `HDZeroHalo_bl.bin` (`4f92d710…`).
2. Verify USB bootloader enumeration and product string.
3. Separately program new `arducopter.bin` (`ec4e56ca…`) at `0x08020000`.
4. Verify Mission Planner connection and HEARTBEAT.
5. Stop. No arming / motor / flight tests.

## READY_FOR_INDEPENDENT_REVIEW

`YES_SOFTWARE_ONLY` — not hardware authorization.
`HARDWARE_FLASH_ALLOWED=NO` remains in force.
