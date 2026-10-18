# BUILD_BASELINE — environment and H743 reference build

**Work package:** WP0  
**Date:** 2026-10-18 (UTC)

## Source control

| Item | Value |
|------|-------|
| Project path | `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter` |
| ArduPilot path | `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/ardupilot` |
| GitHub fork | https://github.com/sliksoft/ardupilot (fork of ArduPilot/ardupilot) |
| `origin` | `https://github.com/sliksoft/ardupilot.git` |
| `upstream` | `https://github.com/ArduPilot/ardupilot.git` |
| Branch | `board/hdzero-halo` |
| HEAD / upstream base SHA | `afeb9c4941543d97f3e04fecf257b8f598f49a6a` |
| Upstream tip (master) at check | same SHA as HEAD |
| Sparse checkout | no |
| Shallow / partial clone | no |
| Checkout integrity | `git fsck` clean; key trees present |

### Submodules (exact revisions at HEAD)

| Submodule | Revision |
|-----------|----------|
| modules/ChibiOS | `9aebaf4a40442277d01bd9dd38c13713fc45ef41` |
| modules/DroneCAN/DSDL | `04e0e818b06c180eb1720fcdf16484d0f12895ee` |
| modules/DroneCAN/dronecan_dsdlc | `de47a8972b7d8c59e50c3acfab5754db29798caa` |
| modules/DroneCAN/libcanard | `601ed35467e0ac38819df17cd7c918de19f62d58` |
| modules/DroneCAN/pydronecan | `08cda37aaf2958657399606653b99ceb5a6beae0` |
| modules/Micro-CDR | `3d1b17703c7cf4f22def2910bc845bdb5152d7b5` |
| modules/Micro-XRCE-DDS-Client | `97175304425c5bee87c6fddd99de1ef8d0c394dc` |
| modules/gbenchmark | `d572f4777349d43653b21d6c2fc63020ab326db2` |
| modules/gsoap | `e1f690585d4803402584962bfaa8240ecaf1db30` |
| modules/gtest | `c5fed93f941865a0e912e9baf46ded713506590a` |
| modules/littlefs | `34be692aafaaf4319a18e415b08aa4332697408b` |
| modules/lwip | `a6bf350c679ed8ba042ad58bf81cc540d61bb605` |
| modules/mavlink | `e03dad40efb3a4009ad6d78de5e55997139ac2f3` |
| modules/waf | `35eadbb64e2052099a853b571e507c33032b392c` |

All 14 submodules checked out (no `-` / uninitialized prefix in
`git submodule status`).

## Host environment (WSL2)

| Item | Value |
|------|-------|
| OS | Ubuntu 24.04.5 LTS (noble) |
| Kernel | `6.6.87.2-microsoft-standard-WSL2` |
| CPU | 16 threads |
| RAM | 47 GiB |
| Disk | ~608 GiB free on `/` |
| Git | 2.43.0 |
| Python | 3.12.3 |
| Project venv | `ardupilot/.venv` (gitignored) |
| ARM GCC | system `arm-none-eabi-gcc` 13.2.1 (`15:13.2.rel1-2`) |
| Official `/opt/gcc-arm-none-eabi-10-2020-q4-major` | not installed |
| ccache | not installed |

### Environment changes made in WP0

1. Created `ardupilot/.venv` (Python 3.12).
2. Installed pip packages required for ChibiOS waf builds:
   `empy==3.3.4`, `pexpect`, `ptyprocess`, `lxml`, `pyserial`, `intelhex`,
   `pymavlink`, `dronecan`, `future`.
3. Did **not** run full `install-prereqs-ubuntu.sh` (avoids optional SITL/GUI stack
   and `/opt` toolchain download). System ARM GCC 13.2 produced a clean
   reference build.

## Reference board build

| Item | Value |
|------|-------|
| Board | `TBS_LUCID_H7` (confirmed via `./waf list_boards`) |
| Vehicle | ArduCopter (`./waf copter`) |
| Commands | `source .venv/bin/activate && ./waf configure --board TBS_LUCID_H7 && ./waf copter` |
| Result | **SUCCESS** (~1m25s) |
| Compiler warnings/errors in log | 0 matching `warning:` / `error:` |
| Text / Data / BSS (size) | 1568484 / 2584 / 392576 |
| Flash used (waf summary) | 1571068 B (free 132860 B) |
| Outputs | `build/TBS_LUCID_H7/bin/arducopter{.apj,.bin,_with_bl.hex}` |
| `arducopter.apj` SHA256 | `d4b8a2a91047b7615fd4d50095fa0d3424f331d0a0500a7a7f48e33d6b258e04` |
| `arducopter.bin` SHA256 | `3d1037427da1b370a72ed77308e80944063fa981ae00ba894d55fd7c041bd004` |

### Evidence files (outside Git)

- `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp0/configure_TBS_LUCID_H7.log`
- `/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp0/build_TBS_LUCID_H7_copter.log`
- Summary copy: `evidence/wp0/BUILD_SUMMARY.txt` (if present)

### Toolchain risk note

ArduPilot’s Ubuntu installer prefers
`gcc-arm-none-eabi-10-2020-q4-major` under `/opt`. WP0 used Ubuntu’s 13.2.1
package successfully for the Lucid H7 build. If a future board or bootloader
build fails with GCC 13-only issues, install the official 10-2020-q4 toolchain
before changing flight code.

## Reproduce

```sh
cd /home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/ardupilot
source .venv/bin/activate
./waf configure --board TBS_LUCID_H7
./waf copter
ls -l build/TBS_LUCID_H7/bin/arducopter.apj
```
