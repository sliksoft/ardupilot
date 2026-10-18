# WP2B_F_FINAL_REPORT — HSE qualification & Betaflight recovery readiness

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**Start-HEAD:** `3754c26a820ccfaf0755fc175af4b3299ed46162`  
**Method:** documentation + source/binary/config verification; no flash, DFU, hwdef, or BF config changes  
**Evidence:** `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-f/`

Detail:

- `WP2B_F_HSE_QUALIFICATION.md`
- `WP2B_F_BETAFLIGHT_RECOVERY.md`
- `WP2B_F_FLASH_READINESS.md`

## Main conclusion

**Software still points at HSE 8 MHz for both Betaflight 2026.6.2 (`e0b7bb01b`) and ArduPilot `OSCILLATOR_HZ 8000000`, but the crystal remains physically unproved. An exact recovery hex for the installed 2026.6.2 build was not archived; config backups and an alternate local 4.5.1 Halo hex are secured. A DFU restore procedure is written with stop conditions and was not executed. First ArduPilot USB-bench flash is still NOT_READY.**

## Status block

```text
WP2B_F_STATUS = PASS_DOCS_PARTIAL_HARDWARE_GATES

HSE_SOURCE = SOURCE_CONFIRMED_HSE8_BF_DEFAULT (2026.6.2 e0b7bb + 4.5.1 chain)
HSE_PHYSICAL = PHYSICAL_UNPROVED
BETAFLIGHT_RECOVERY_IMAGE = EXACT_e0b7bb01b_NOT_AVAILABLE
RECOVERY_IMAGE_SHA256 = N/A_FOR_EXACT; ALT_4.5.1=d2f590334043684e1339c71e8e2767cc7d5da4bdd1e6ded26e829b1325ef3a03; NEAR_2026.6.2_8753f38fc=d94bb831f22d134722d889f77ecafb1aa573d4bccb05c5a61c69d7d1b1653259
BF_CONFIG_BACKUP = YES (WP2B-B diff_all/dump copied under evidence/wp2b-f)
DFU_PROCEDURE = DOCUMENTED_WITH_CHECKPOINTS
DFU_HARDWARE_TEST = NOT_PERFORMED
FLASH_LAYOUT = BF_vs_AP_DOCUMENTED (no dual-boot)
FIRST_AP_BENCH_READINESS = NOT_READY
OPEN_BLOCKERS =
  flash_auth_NO;
  DFU_untested;
  exact_BF_hex_missing;
  HSE_physical_unproved;
  gyro_polarity_incomplete;
  no_baro_for_normal_copter_start
COMMIT_SHA = (set after commit)
PUSH_STATUS = (set after push)

HARDWARE_FLASH_ALLOWED = NO
```

## WU summary

| WU | Result |
| -- | ------ |
| WU1 prior reports vs hwdef/BF | Consistent: HSE8 provisional; ICM `ROLL_180` applied (WP2B-D); live BF 2026.6.2 HDZERO_HALO |
| WU2 HSE | SOURCE_CONFIRMED software HSE8; LIVE 480 MHz ≠ physical proof |
| WU3 recovery binary | Exact `e0b7bb01b` missing; alt 4.5.1 + near 8753f38fc inventoried with SHA256 |
| WU4 DFU plan | Written; OEM typo HAZERO→HDZERO noted; **not tested** |
| WU5 flash readiness | USB bench NOT_READY |
| WU6 reports | This set + WP2B-C historical IMU-rotation notes updated |

## Safety compliance

- No ArduPilot firmware/hwdef edits  
- No BF config changes  
- No flash, erase, DFU activation, option-byte writes, or BOOT automation  
- No motor / ESC / PINIO / VTX actions  
- `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.serena/` not committed  
