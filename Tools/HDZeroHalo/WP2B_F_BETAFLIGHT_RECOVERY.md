# WP2B_F_BETAFLIGHT_RECOVERY — recovery image & DFU plan

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
**DFU_HARDWARE_TEST = NOT_PERFORMED**

Evidence: `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-f/recovery/`  
DFU notes: `evidence/wp2b-f/dfu/`

## Live firmware to recover *to* (desired)

| Field | Value | Source |
| ----- | ----- | ------ |
| Version | Betaflight **2026.6.2** | WP2B-B CLI |
| Commit | **`e0b7bb01b`** | WP2B-B `version` |
| Config rev | **`3a406c5`** | WP2B-B |
| Target | **`HDZERO_HALO`** (HDZO) | WP2B-B / MSP |
| Build stamp | Oct 18 2026 / 15:24:23 | WP2B-B |
| MCU UID | `004000383533510f39303730` | WP2B-B / WP2B-E |

Exact bit-identical hex for this cloud/local build was **not** found in archives or GitHub release assets (Halo-named assets absent from the `2026.6.2` GitHub release).

## Config backup (trusted, read-only)

Copied from WP2B-B into evidence (outside Git):

| File | SHA256 |
| ---- | ------ |
| `wp2b-b_27_diff_all.txt` | `c9baa1c393825b5bd1acdcff2b2945bfa7216f5d358cfd75ec772a228ad88c8e` |
| `wp2b-b_28_dump_all.txt` | `4f53eb63f3b184bc61ecd464f4cb2b6d7d16b657be206d747e71d7fb2769f6d2` |
| `wp2b-b_01_version.txt` | `e4066a80bbaf49a661e6d18e90ae3c7f42e542b2bcd1d7fb7219ff952c7fd998` |
| `wp2b-b_FULL_TRANSCRIPT.txt` | `b36f43a2687addb29d09ead2d94ef7e1afd2782a48131fd9521922d73ddc84ba` |

These restore **configuration**, not the firmware blob.

## Candidate firmware images (outside Git)

| Role | File | SHA256 | Trust |
| ---- | ---- | ------ | ----- |
| **Exact installed 2026.6.2 `e0b7bb01b`** | *(not archived)* | — | **MISSING** |
| Near same release (UNCONFIRMED) | `NEAR_community_2026.6.2_HDZERO_HALO_commit8753f38fc.hex` | `d94bb831f22d134722d889f77ecafb1aa573d4bccb05c5a61c69d7d1b1653259` | Same version string + config `3a406c5`, but revision **`8753f38fc`** and stamp Sep 29 2026 — **not** live build |
| Near (bin) | `…8753f38fc.bin` | `b33210b61c9a7551999a3d884dde4dbff9c687f36b8ca33ffa8736b56f44c1e1` | Same caveat |
| Alternate (factory-line) | `ALT_local_reproduced_4.5.1_HDZERO_HALO.hex` | `d2f590334043684e1339c71e8e2767cc7d5da4bdd1e6ded26e829b1325ef3a03` | Local official-toolchain Halo build (WP2B-A); **not** installed image |
| Reject as Halo recovery | `NOT_HALO_generic_4.5.1_STM32H743.hex` | `38569624d5722ae6f7522ec44a89db34f03b90c1c33418eab890d5a87285f2ae` | Generic H743 — wrong target |

```text
BETAFLIGHT_RECOVERY_IMAGE = EXACT_e0b7bb01b_NOT_AVAILABLE
RECOVERY_IMAGE_PRIMARY_PLAN = CLOUD_ONLINE_HDZERO_HALO_THEN_REAPPLY_DIFF_ALL
RECOVERY_IMAGE_ALT_ARCHIVED = LOCAL_4_5_1_HALO_HEX (SHA above)
RECOVERY_IMAGE_NEAR_2026_6_2 = UNCONFIRMED_COMMIT_MISMATCH_8753f38fc
```

Do **not** treat the community `8753f38fc` file as a trusted bit-identical restore of this board.
Do **not** use the generic `STM32H743.hex` as Halo recovery.

## Preferred recovery sequence (plan only — not executed)

### Preconditions (stop if any fail)

1. User explicitly authorises DFU/flash for this session.  
2. WP2B-B `diff all` / `dump` readable on disk (copied above).  
3. Windows host has Betaflight Configurator + STM32 DFU drivers (Zadig if needed).  
4. usbipd-win / WSL2 path understood: DFU is typically done in **Windows** Configurator, not WSL ACM.  
5. Target name forced to **`HDZERO_HALO`** (OEM docs typo `HAZERO_HALO` must be ignored).

### Checkpoints

| Step | Action | Stop if |
| ---- | ------ | ------- |
| C0 | Confirm USB CDC still works (`0483:5740`) if board still boots BF | Unexpected device ID |
| C1 | Power off FC; Configurator: **No reboot sequence** + **Full chip erase** | Operator unsure → STOP |
| C2 | Hold **BOOT**, plug USB-C, release BOOT | Device not STM32 BOOTLOADER / DFU → STOP, release, retry once |
| C3 | Load Firmware **[Online]** target `HDZERO_HALO` (prefer 2026.6.2 if listed; else documented factory 4.5.1) | Wrong target auto-selected → STOP |
| C4 | Flash; wait for success | Flash error / verify fail → STOP; do not retry blindly |
| C5 | Board re-enumerates as CDC; CLI `version` shows HDZERO_HALO | Wrong board_name → STOP |
| C6 | CLI: load `diff all` from backup; review; `save` only after human review | Diff targets another board → STOP |
| C7 | Re-check gyro ICM42688P, UART1 CRSF, UART5 MSP DP | Sensor missing → investigate before further work |

### Risks

| Risk | Mitigation |
| ---- | ---------- |
| Full chip erase wipes BF config @ `0x08020000` | Keep `diff all` / `dump`; re-apply after flash |
| Option bytes / RDP unknown | Do not change option bytes; stop if Configurator warns |
| ROM version DFU quirks (AN2606) | Prefer documented BOOT method; one careful attempt |
| Flashing AP then returning | AP layout ≠ BF; always ROM DFU full erase + Halo BF image |
| Wrong target name in OEM docs | Use **HDZERO_HALO** only |
| Near-version community hex | Not primary; only if human accepts commit mismatch |

### WSL2 / usbipd notes

- Normal BF CLI/MSP: Windows → `usbipd` → WSL `/dev/ttyACM0` (already proved).  
- DFU flash: prefer **native Windows** Configurator while device is in STM32 DFU (`0483:df11` class).  
- Do not bind DFU to WSL unless a tested `dfu-util` path is separately approved.  
- After flash, re-attach CDC to WSL if further read-only checks are needed.

### What this WP did **not** do

- No BOOT press commanded by software.  
- No DFU enumeration test.  
- No erase, flash, or option-byte write.  
- No download from unverified third parties marked as *trusted* recovery.

## OEM documentation citation

https://docs.hd-zero.com/halo-firmware — BOOT + full erase procedure; factory version 4.5.1 cited; target string typo `HAZERO_HALO` noted; proven identity remains `HDZERO_HALO`.
