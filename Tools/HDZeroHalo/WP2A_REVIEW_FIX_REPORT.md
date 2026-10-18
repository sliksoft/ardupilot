# WP2A independent-review fixes

**Date:** 2026-10-18

**Review basis:** `9e8f166ecd17c418d4070d4b6f4b92e7fee6bf8d`

**Branch:** `board/hdzero-halo`

Status: **HARDWARE_FLASH_ALLOWED = NO**

Implementation and verification were AI-assisted. No physical device was
flashed, erased, armed, commanded or reconfigured. No flight algorithm, shared
sensor driver, parameter index or submodule was changed. No WP2B was started.

## Disposition of all nine findings

| ID | Status | Change / remaining evidence |
| ---- | -------- | ----------------------------- |
| H1 HSE/HSI | FIXED | Rechecked BF4.5.1 Makefile -> compiler flags -> PLL source. Normal build uses HSE8; corrected reports. Physical source/image identity still unverified. HSI alternative not implemented. |
| H2 buzzer | FIXED | PD12 LOW after GPIO init in application and bootloader; active HIGH level1. Generated ODR/MODER and application level checked. Physical output unmeasured. |
| H3 IMU rotation | HARDWARE_BLOCKED | Relative software correction implemented: MPU ROLL_180_YAW_90, ICM NONE. Exact accel/gyro matrices documented. Absolute mounting on both SKUs still requires evidence. |
| H4 barometer prearm | FIXED | Removed HAL_BARO_ALLOW_INIT_NO_BARO entirely. Standard health checks remain; no sensor enters existing serviced USB configuration-error loop. No core changes. |
| M1 LED DMA | DEFERRED_WITH_REASON | Retained NODMA and all existing DMA assignments. All16 streams occupied; sharing would add unqualified contention. Addressable LED support explicitly unavailable. |
| M2 external barometer | FIXED | Default probe mask1030 (BMP280/MS5611/BMP388), existing parameters/backends retained, setup and recovery documented. Physical detection untested. |
| M3 PE3 reset | FIXED | Corrected reset claims: LOW requested after GPIO init only. Reset, brownout, ROM DFU and actual9V rail remain electrically unverified. |
| M4 BF flash docs | FIXED | First BF128KiB region described as vectors/startup, not a proved replaceable bootloader. AP address/erase contracts and combined artifact checked without changing layout. |
| L1 VBAT | VERIFIED_NO_CHANGE_NEEDED | Existing factor11 agrees with BF nominal defaults; corrected rationale. Current conversion10000/BF_scale gives100 A/V here. Physical calibration still required. |

## Exact source changes

- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat`: buzzer initial/on
  levels; two MPU rotations; removal of no-baro bypass; external probe default;
  accurate HSE/VBAT/LED/PE3 comments. Motor pins, DMA policy, UARTs, SPI devices,
  storage layout, board ID and ICM probe order remain unchanged.
- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef-bl.dat`: explicit PD12 LOW;
  qualified PE3 initialisation comment. HSE8/load offset/DFU setting unchanged.
- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/defaults.parm`: barometer and PE3
  guidance; `MOT_PWM_TYPE=5` retained. No hardware parameter operation occurred.
- `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/README.md`: supported configuration,
  no-baro USB recovery limits, relative IMU frame and LED limitation.
- `Tools/bootloaders/HDZeroHalo_bl.bin`, `.elf`, `.hex`: rebuilt from the
  corrected bootloader definition, using the existing repository build script.
- `Tools/autotest/unittest/hdzero_halo_unittest.py`: production hwdef generation,
  compiled initial GPIO checks, actual production prearm method with a sensor
  boundary, old-bypass negative control, probe defaults and DMA isolation.
- `Tools/HDZeroHalo/WP2A_HSE.md`, `WP2A_FINAL_REPORT.md`: corrected build-chain
  conclusion and separated software, image and physical evidence.
- `Tools/HDZeroHalo/WP2A_IMU_VBAT.md`: exact matrices, source conversions and
  remaining physical qualification.
- `Tools/HDZeroHalo/WP2A_BAROMETER.md`: new sensor/default/recovery/health guide.
- `Tools/HDZeroHalo/WP2A_PE3_POLARITY.md`, `WP2A_FLASH_LAYOUT.md`,
  `WP2A_TIM3_DMA.md`: initialisation boundary, BF/AP memory map and LED limitation.
- `Tools/HDZeroHalo/WP1A_BLOCKERS.md`, `WP1A_BOOTLOADER.md`, `WP1A_FINAL_REPORT.md`,
  `WP1A_HARDWARE_AUDIT.md`: corrected earlier rejection of the BF HSE8 rationale.
- `Tools/HDZeroHalo/WP1B_INDEPENDENT_REVIEW.md`: explicitly superseded the wrong
  buzzer recommendation while preserving historical build observations.
- `Tools/HDZeroHalo/WP1B_MEMORY_LAYOUT.md`: removed the unsupported BF-bootloader
  rationale for changing AP reserve size.
- `Tools/HDZeroHalo/PORT_STATUS.md`, `README.md`: current status and document index.
- This report records validation, scope and remaining blockers.

Existing `AGENTS.md`, `CLAUDE.md`, `.claude/` and `.serena/` are excluded from
staging and are checked against their initial SHA256 manifest.

## Offline validation and evidence

Logs and generated artifacts are outside Git at
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2a-review-fixes/`.
Tests use temporary directories; no USB, serial or hardware handles are opened.

| Check | Command / surface | Result | Evidence |
| ------- | ------------------- | -------- | ---------- |
| Bootloader | `PATH="$PWD/.venv/bin:$PATH" .venv/bin/python Tools/scripts/build_bootloaders.py HDZeroHalo` | Built with Werror; flash18920 B, binary18924 B | `build_bootloader.log`, `hwdef-bootloader.h`, `ldscript-bootloader.ld` |
| App configure | `.venv/bin/python ./waf configure --board HDZeroHalo --no-submodule-update --Werror` | Successful | `configure_copter.log` |
| ArduCopter | `.venv/bin/python ./waf copter` | Built with Werror; flash1240776 B, free463096 B | `build_copter.log` |
| New regressions | `.venv/bin/python Tools/autotest/unittest/hdzero_halo_unittest.py -v` | 5/5 passed | `config_tests.log` |
| Python lint | `flake8 Tools/autotest/unittest/hdzero_halo_unittest.py` | Passed | Command result; no diagnostics |
| Markdown lint | `markdownlint-cli2` on all 17 changed Markdown files | Passed after table/link formatting | `markdownlint.log` |
| Actual ARM clock definitions | Original system.cpp compile flags, syntax-only assertions | HSE8, CPU480, SPI1/2=80, USB48, USART1=100, I2C1=32, TIMCLK1=240 MHz | `clock_assertions.log`, `compiled_clock_macros.log` |
| Compiled feature paths | Original translation-unit flags plus enabled-feature assertions | CRSF telemetry, MSP DisplayPort, logger, barometer backends, DShot | `peripheral_assertions.log`, `peripheral_features.log`, `compiled_feature_macros.log` |
| Flash/image integrity | APJ decompression, combined HEX comparison against BL/app bytes, address bounds | Board1414; BL/app match; no data at/above parameter start0x081C0000 | `layout_and_hashes.log` |
| Existing host tests | Debug SITL configuration; targets `tests/test_rotations,tests/test_prescaler` | See final results below | `build_host_tests_debug.log`, `test_rotations_debug.log`, `test_prescaler_debug.log` |

The new prearm probe compiles `AP_Arming::barometer_checks()` directly from
production source using generated Halo definitions. An unhealthy sensor is
rejected; a healthy one is accepted. Reintroducing the old bypass causes the
probe executable to fail. The sensor boundary is a small fake, so this proves
the board's compile-time guard/dispatch, not a physical sensor or complete
Copter startup. Generated output tests verify PD12/PE3 register intentions,
not reset voltages. DMA tests verify assignments, not runtime scheduling.

Initial release-mode rotation tests reported4 passes and1 failed death-test:
`AP_InternalError::error()` only panics in SITL when HAL_DEBUG_BUILD is defined.
No source or test was weakened. The host tests were rebuilt in debug mode to
exercise the intended abort contract. The initial failure is retained in
`test_rotations_release.log`; final debug results are recorded below.

### Final host results

Debug `test_rotations`:5/5 passed, including the existing death-test.
Debug `test_prescaler`:77/77 passed, including DShot300/600 and bidirectional
sampling-rate cases. No hardware or simulated vehicle was armed. The initial
release failure was a test-build prerequisite mismatch, not a Halo regression.

### Firmware regression comparison

WP1B application flash usage1240424 B ->1240776 B (+352 B); bootloader flash
usage remains18920 B. The existing128KiB reserve,1664KiB application region,
parameter pages14/15, four motor pins, serial order, SPI routing and TIM3 DMA
allocation remain intact. APJ decompression and combined HEX contents were
compared with actual binaries. This is artifact integrity, not hardware proof.

The APJ records base git identity `9e8f166e` because it is built from the corrected
working-tree snapshot before commits. Artifact hashes and generated definitions
identify the tested contents; do not describe these as binaries built after
the final documentation commit. The final commit SHA is reported at handoff.

## Additional findings and deliberate boundaries

- HSI-only already has an MCU/HAL path but changing only OSCILLATOR_HZ and CPU
  rate would conflict with the generated SPI4/5 expectation. No HSI implementation
  or assertion suppression was introduced.
- Without a barometer, USB recovery precedes normal telemetry/OSD startup.
  Full normal no-baro operation is not claimed or provided.
- The external DPS280 probe does not instantiate the distinct DPS310 subclass
  temperature workaround. DPS310 qualification is not claimed; no driver change
  was made. Models/masks actually offered are documented in WP2A_BAROMETER.md.
- Physical FC BOOT recovery is vendor-supported, not exercised. The application
  does not enable application-initiated ROM DFU; bootloader DFU support is separate.
- Full SITL vehicle integration scenarios (`ConfigErrorLoop`, `BaroDrivers`,
  `SensorErrorFlags`) were not run. No ARM or motor scenario was used. Host unit
  tests, compiler checks and source inspection do not replace physical evidence.

## Independent review and graph evidence

The independent read-only gate approved the complete 24-file snapshot before
commit, with no functional blocker in the offline scope. It checked all nine
dispositions, matched all six firmware hashes, decompressed the APJ and compared
both combined-HEX payloads. It inspected the test/build logs without rerunning
them. Its Markdown-lint note was resolved by formatting tables and links; no
functional source changed after approval. Verdict: `independent_gate_review.md`
in the evidence directory. GitNexus impact of generic barometer
checks identifies pre_arm_checks -> arm/update; shared implementation is unchanged.
Hwdef/configuration edges are not fully represented by the graph. Direct generator,
compiler and source checks supplement it. Index-only refresh preserves agent files;
graph truncation/receiver-resolution limitations are not treated as low risk.

## Remaining hardware blockers

1. Exact MCU/revision/flash capacity, physical clock source, factory image/CLI,
   option-byte/protection information and ROM/BOOT recovery on the actual board.
2. Absolute IMU frame, part and chip-select identity on each SKU; six faces and
   signed accel/gyro rotations. Relative matrix correction does not close this.
3. PD12 and PE3/9V electrical states across reset, startup, bootloader, failure
   and ROM DFU. GPIO initialisation alone cannot establish those states.
4. Barometer identity, pressure/temperature plausibility, missing/faulty-sensor
   rejection and USB configuration recovery on physical hardware.
5. DShot300/600 timing, four-channel bidirectional eRPM/error rates and operation
   under simultaneous IMU/logging/UART loads with the actual ESC firmware.
6. RC/CRSF telemetry and failsafe/recovery, HDZero OSD/canvas, USB, logger
   throughput/full-flash/download behaviour, ADC voltage/current calibration,
   and any external GPS/compass. No hardware PASS is assigned.

## Status block

```text
REVIEW_FIX_STATUS = SOFTWARE_FIXES_IMPLEMENTED; HARDWARE_QUALIFICATION_OPEN
H1_HSE = FIXED
H2_BUZZER = FIXED
H3_IMU_ROTATION = HARDWARE_BLOCKED; RELATIVE_SOFTWARE_FIX_IMPLEMENTED
H4_BARO_PREARM = FIXED
M1_LED_DMA = DEFERRED_WITH_REASON; ADDRESSABLE_LED_UNSUPPORTED
M2_EXTERNAL_BARO = FIXED; PHYSICAL_DETECTION_UNVERIFIED
M3_PE3_RESET = FIXED_DOCUMENTATION; ELECTRICAL_BEHAVIOUR_UNVERIFIED
M4_BF_FLASH_DOCS = FIXED; AP_LAYOUT_VERIFIED_OFFLINE
L1_VBAT = VERIFIED_NO_CHANGE_NEEDED; NOMINAL11_UNCALIBRATED
ARDUCOPTER_BUILD = PASS_OFFLINE
BOOTLOADER_BUILD = PASS_OFFLINE
DSHOT300 = COMPILED; PRESCALER_TESTED; HARDWARE_UNVERIFIED
DSHOT600 = COMPILED; PRESCALER_TESTED; HARDWARE_UNVERIFIED
BIDIR_DMA = GENERATED_MAPPING_TESTED; DRIVER_SOURCE_CHECKED; HARDWARE_UNVERIFIED
REGRESSION_TESTS = CONFIG5_PASS; DEBUG_ROTATIONS5_PASS; DEBUG_PRESCALER77_PASS
OPEN_HARDWARE_BLOCKERS = SIX_GROUPS_LISTED_ABOVE
HEAD_SHA = FINAL_COMMIT_SHA_REPORTED_AT_HANDOFF
PUSH_STATUS = PENDING_AT_REPORT_PREPARATION
HARDWARE_FLASH_ALLOWED = NO
READY_FOR_CODEX_REREVIEW = YES; HARDWARE_QUALIFICATION_OPEN
```
