# WP2B-H: resolve the unsupported software DFU option

Date: 2026-10-19. Start HEAD: `6a7fe58f20f9024a17a93030661737152bf1131b`.
Branch: `board/hdzero-halo`. AI-assisted investigation, configuration correction,
tests and report by Codex. **HARDWARE_FLASH_ALLOWED = NO**.

## Outcome and scope

The unsupported bootloader-only `ENABLE_DFU_BOOT 1` declaration was removed.
Both application and bootloader now generate `HAL_ENABLE_DFU_BOOT FALSE`.
This withdraws an unusable capability; it does **not** implement software ROM
DFU. Physical BOOT-button/system-ROM recovery remains the documented route,
not physically exercised or qualified by this work. Normal AP USB bootloading
and reboot-to-AP-bootloader are separate from ROM DFU.

No shared startup, HAL implementation, generator or submodule was changed.
The original independent review remains unchanged at
`evidence/codex-halo-preflash-review/REPORT.md`, outside the repository.

## Exact root cause

| Layer | Before correction | Evidence in production source |
| --- | --- | --- |
| Halo bootloader configuration | Enabled only in BL | Original `hwdef-bl.dat:48-49` at start HEAD |
| Generator | Correctly emits TRUE and exports the build option for that declaration | `libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py:2585-2595` |
| Build flags | Requests `CRT0_ENTRY_HOOK=TRUE` for enabled BL | `Tools/ardupilotwaf/chibios.py:659-660` |
| ROM-entry implementation | Function exists and uses H743 ROM address `0x1FF09800` | `libraries/AP_HAL_ChibiOS/system.cpp:302-321` |
| Pinned startup | Never references the hook or its switch | `modules/ChibiOS/os/common/startup/ARMCMx/compilers/GCC/crt0_v7m.S:210-271` |
| Halo application | Option already absent, hence software DFU disabled | `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat`; generator default is integer zero |

ChibiOS is exactly the pinned gitlink
`9aebaf4a40442277d01bd9dd38c13713fc45ef41`, with no local changes.
The startup initializes the CPU and calls `__early_init`; it contains neither
`CRT0_ENTRY_HOOK` nor a call to `__entry_hook`.

The pre-correction `system.cpp.8.o` **does contain** `__entry_hook`, as verified
with `arm-none-eabi-nm -C`. Thus the implementation was compiled, not missing
from source or excluded by the BL guard. The final committed ELF has no such
symbol, and `_crt0_entry` disassembly has no hook call. Its absence follows
from the missing startup reference and elimination of unreachable code during
linking; optimizer removal is a consequence, not the root cause.

The generator, HAL function and build flag cannot supply a call absent from
the pinned assembly. Enabling the application option alone would therefore
not repair the chain. Adding a new board-specific startup path or changing
the ChibiOS submodule is unnecessary for the existing physical recovery plan
and outside this correction.

### Application request path

`libraries/AP_HAL_ChibiOS/Util.cpp:862-868` implements the persistent request
and reboot only under `HAL_ENABLE_DFU_BOOT`, outside a BL build.
`libraries/GCS_MAVLink/GCS_Common.cpp:3543-3554` guards the corresponding
MAVLink ROM-DFU request with the same macro. The compiled Halo application
does not offer that request, before or after this correction.

This was verified using the actual ArduCopter compile-database command for
`GCS_Common.cpp`, converted to preprocessing with dependency/output writes
removed. The resulting handler has no `hal.util->boot_to_dfu()` call or
"Entering DFU mode" branch. The rebuilt app ELF has neither the ChibiOS
`Util::boot_to_dfu` implementation nor `__entry_hook`. The ordinary reboot
handler remains present at `0x080A4A4C`; its disassembly was saved separately.
No request was sent to hardware.

## Minimal correction

`hwdef-bl.dat` now omits `ENABLE_DFU_BOOT`, using the existing disabled
generator default, and explains the physical BOOT route. Board documentation
and the feature matrix distinguish physical ROM recovery, unavailable software
entry and AP USB communication. A focused regression compiles both generated
headers and rejects an enabled software DFU capability.

An explicit `ENABLE_DFU_BOOT 0` is **not** equivalent in this checkout:
`get_config()` returns an unconverted string when present
(`chibios_hwdef.py:658-687`), and the DFU generator tests its truth value.
The nonempty string `"0"` consequently enables the option. The regression
caught that intermediate attempt. Removing the declaration is the correct
existing mechanism; the shared parser was left unchanged.

## Offline validation

Evidence root, outside Git:
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-h/`.
Builds use the existing `.venv` on PATH and ARM GCC 13.2.1.

| Check | Result | Evidence |
| --- | --- | --- |
| New regression against original configuration | Expected FAIL, BL subcase only | `regression-before.log` |
| Complete Halo configuration suite after correction | PASS, 12 tests | `regression-after.log` |
| Python lint | PASS | `flake8.log` |
| BL regeneration/build, `Tools/scripts/build_bootloaders.py HDZeroHalo` | PASS, 18,924-byte BIN | `build-bootloader.log` |
| App configure, `./waf configure --board HDZeroHalo --no-submodule-update --Werror` | PASS | `configure-copter.log` |
| App build, `./waf copter` | PASS, flash 1,240,544 B; free 463,328 B | `build-copter.log` |
| Generated BL header before/after | Only TRUE-to-FALSE DFU macro change | `before/hwdef.h`, `after/hwdef.h` |
| BL linker and startup disassembly before/after | Byte-identical files | `before/`, `after/`, `invariants.log` |
| BL build flags | Obsolete `CRT0_ENTRY_HOOK` request removed | `before/chibios_flags.h`, `after/chibios_flags.h` |
| App macro and production MAVLink request branch | Disabled, branch absent | `after/gcs-preprocessed-handler.txt` |
| Actual app and BL ELF inspection | PASS for disabled capability | `after/bootloader-nm.txt`, `after/application/nm.txt`, ELF disassemblies and segment listings |
| Agent-file protection | All recorded hashes unchanged | `agent-files.sha256`, `agent-files-verified.log` |

BL generated header comparison preserves every other setting, including PE3
output LOW, HSE8 and flash reserves. Its linker still reserves 128 KiB at
`0x08000000`. The app linker still starts at `0x08020000`, with 1664 KiB;
the actual ELF flash payload ends at `0x0814EE20`, before parameter pages
14/15 at `0x081C0000`. The app header retains HSE8, 480 MHz and
`HAL_BARO_ALLOW_INIT_NO_BARO 1`.

`hwdef.dat`, `defaults.parm`, shared barometer/arming code, HAL implementation,
IMU code, RCOutput, and all submodules are unchanged from start HEAD. The
existing regression suite covers PE3/PD12 output levels, external barometer
probing/no-baro startup, IMU rotations and TIM3 DMA configuration. These are
offline configuration checks, not motor, DShot waveform or flight tests.

Rebuilt artifacts are retained outside Git; only the existing tracked BL
ELF/HEX/BIN are updated in the repository. Their embedded source version is
start HEAD with the documented working-tree correction, not a claim that an
unmodified start-HEAD checkout reproduces these builds.

| Artifact | SHA256 |
| --- | --- |
| `HDZeroHalo_bl.bin` | `a2efe9fefbe34593d9ad15b28b7222b32aa0d75546539ad1fa8b4db6c608a1a9` |
| `HDZeroHalo_bl.elf` | `7848acdc2a301e067916f9a5d1e2bf788ce943cbfe281bbb14886a8708e36c7d` |
| `HDZeroHalo_bl.hex` | `1cdd945a87e2bd68e67b87d8feaacc52cf1e92ce8c7c767b4bc1be8295729a3d` |
| `arducopter` ELF | `39f9b7dc2684108392bd4e6f79947ddf65f06dedcef548df0cdb3c91befa8a5f` |
| `arducopter.bin` | `c8d5b02273786ff7356aa47e3b43b00fafe11294572518b2e5978239d9cb4e80` |
| `arducopter.apj` | `13884fe1b9817195d85934154858b3f344e92a3f4eb75481146c6c6d633fe47b` |

## Graph and final checks

GitNexus initially matched start HEAD and reported a current runner with no
incomplete reasons. Impact for the hwdef is UNKNOWN (not indexed); impact for
the test class and generator method resolves no upstream callers and is also
UNKNOWN. This was not treated as proof of no impact: generator consumers,
startup, generated outputs and actual binaries were inspected directly.
No shared production function is edited.

Final graph/change checks and branch-convention results are recorded alongside
the build evidence. Only explicit WP2B-H paths are staged; the existing local
agent files remain outside the commits. No submodule, Betaflight, option byte
or hardware action is part of this work.

```text
WP2B_H_STATUS = PASS_OFFLINE_CONFIGURATION_CORRECTION
ROOT_CAUSE = PINNED_STARTUP_DOES_NOT_CALL_COMPILED_DFU_HOOK
SOFTWARE_DFU_ENTRY = UNSUPPORTED_DISABLED_IN_APP_AND_BOOTLOADER
PHYSICAL_BOOT_ROM_RECOVERY = RETAINED_DOCUMENTED_NOT_HARDWARE_TESTED
BOOTLOADER_BUILD = PASS
ARDUCOPTER_BUILD = PASS
REGRESSION_TESTS = PASS_12_OF_12
PROTECTED_HARDWARE_CONFIGURATION = UNCHANGED
HARDWARE_FLASH_ALLOWED = NO
```
