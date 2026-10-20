# External evidence index — HDZero Halo hardware baseline

Original evidence lives **outside** this Git repository and was left unmodified:

`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/`

This directory holds curated, herleidbare copies of the qualification reports and
small machine-readable summaries needed to reconstruct the tested baseline.
Full flash dumps, large raw MAVLink captures, and Windows staging trees stay
external only.

`HARDWARE_FLASH_ALLOWED = NO` for further work unless separately authorized.

## Tested firmware identity

| Artifact | Bytes | SHA256 |
| --- | ---: | --- |
| Production bootloader `HDZeroHalo_bl.bin` | 18916 | `4f92d710e21be29daed876084be9db7045e6f29ef08d290c4f9ab0253cb1d52f` |
| ArduCopter app `arducopter.bin` | 1240584 | `ec4e56caedb6aa58af4db0fecce7c585bb46bf5ef0859fe12bba26c5726773a7` |
| ArduCopter ELF (WP3-J after/) | 2583916 | `5d9af4f77d2fc621b31efeef5d4cffccff1895adff5dbfdca007fe7573acef62` |
| Postflash full 2 MiB readback (external) | 2097152 | `56be4a3a71e4daa88ec64b248ed210ea69ac87d990ff5e6f69acf4b0c984a310` |

Repo bootloader binaries under `Tools/bootloaders/HDZeroHalo_bl.{bin,elf,hex}`
match the flashed BL BIN (`4f92d710…`).

Live firmware string on hardware (WP4-C):

- `ArduCopter V4.8.0-dev (c1a1fc2d)`
- ChibiOS `9aebaf4a`
- Board `HDZeroHalo`, `AP_HW_HDZERO_HALO` = 1414
- USB `1209:5741`, product `HDZeroHalo`

`c1a1fc2d` is the git tip that existed when WP3-J images were built. The
working-tree source changes committed with this baseline are those used to
produce the WP3-J/K images (HSI64/HSI48, `strlen` fix, USB path); they were
not yet committed at flash time.

## Hardware configuration (bench)

| Item | Value |
| --- | --- |
| MCU | STM32H743 (Device ID `0x450`, SN `200364500000`) |
| Host USB | Windows COM14, VID:PID `1209:5741` |
| Power | USB only (no LiPo / ESC / RC / GPS / mag / baro) |
| Frame (after WP4-B) | `FRAME_CLASS=1`, `FRAME_TYPE=1` (QUAD/X) |
| Motors config | `MOT_PWM_TYPE=5` (DShot300), outputs 1–4; pad 5 PWM unused |
| IMU | ICM42688P path healthy; hwdef `ROTATION_ROLL_180` |
| Flash programming | Single ROM-DFU session; sectors 0–10; 11–15 preserved preboot |

## Qualification results

| Work package | Result | In-repo copy | External original |
| --- | --- | --- | --- |
| WP3-K production first boot | PASS (USB + HEARTBEAT + MP path) | `wp3-k/` | `evidence/wp3-k-production-first-boot/` |
| WP4-A USB IMU/attitude | PASS (roll/pitch/level) | `wp4-a/` | `evidence/wp4-a-usb-imu-attitude/` |
| WP4-B Quad/X | PASS (`FRAME_CLASS/TYPE=1`) | see `../WP4_B_QUAD_X.md` | live params verified in WP4-C |
| WP4-C full FC inventory | COMPLETE (1195 params) | `wp4-c/` | `evidence/wp4-c-fc-usb-inventory/` |

### Remaining limitations (expected on USB bench)

- Mag unhealthy / no device; no baro; no RC; battery unhealthy without pack
- No ESC/motor spin, bidirectional DShot, ARM, or flight tests
- Production BL ECC recovery may later erase app/param sectors
- Hwdef still defaults `HAL_FRAME_TYPE_DEFAULT 12`; live vehicle is FRAME_TYPE 1

## Hash manifests

| File | Purpose |
| --- | --- |
| `SHA256SUMS.txt` | Hashes of every curated file in this directory |
| `EXTERNAL_ORIGINALS_SHA256.txt` | Hashes of the external originals used for the copies + flashed images |

## Intentionally excluded from Git

- `*/backup/preflash_*.bin`, `*/verify/postflash_fullflash.bin` (2 MiB dumps)
- Large raw MAVLink `frames*.hexl`, JSONL motion captures, Windows staging trees
- Build trees under `ardupilot/build/`
- `.claude/`, `.serena/` caches / local session files, and `CLAUDE.md` (no
  allowed ArduPilot commit subsystem; keep local)

## Copy normalization

In-repo markdown report copies are byte-identical to the external originals except where trailing whitespace was stripped so `git diff --check` stays clean. Substance and SHA256 of firmware/bootloader images are unchanged.

## Integrity checks performed at baseline commit

- Curated WP3-K / WP4-A / WP4-C reports byte-identical to external originals
- `Tools/bootloaders/HDZeroHalo_bl.bin` byte-identical to WP3-K staging BL
- Staging app SHA256 `ec4e56ca…` matches WP3-J `after/arducopter.bin`
- No API keys / tokens / private keys found in curated reports or param dump
- Halo unit tests: 29 passed (`hdzero_halo_*unittest.py`)
