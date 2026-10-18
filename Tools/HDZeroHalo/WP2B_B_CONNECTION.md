# WP2B_B_CONNECTION — WSL2 USB serial access

**Date:** 2026-10-18  
**Branch:** `board/hdzero-halo`  
**HARDWARE_FLASH_ALLOWED = NO**  
**Policy:** strict read-only CLI / MSP identity — no `set` / `save` / `defaults` / DFU / flash

## Host checks

| Check | Result |
| ----- | ------ |
| Device | `/dev/ttyACM0` `crw-rw---- root:dialout` |
| USB | `0483:5740` STMicroelectronics Virtual COM Port (`lsusb`) |
| User groups | `sliksoft` ∈ `dialout` |
| Port busy | No holder via `lsof` / `fuser` at session start |
| Tool | Python 3 + `pyserial` 3.5 (already installed) |
| Forced access | Not used |

## Session method

Custom read-only pyserial script with a denylist rejecting `set`, `save`, `defaults`, `bl`, `dfu`, `reboot`, resource reassignment, etc. Entered CLI with `#`, ran only `version` / `status` / `get` / `resource` / `timer` / `dma` / `flash_info` / `diff all` / `dump all` / `tasks` / `mcu_id`.

Evidence (outside Git):  
`/home/sliksoft/VliegAI/HDZero-Halo-ArduCopter/evidence/wp2b-b/cli/`  
Hashes: `evidence/wp2b-b/hashes/artifacts.sha256`

## Connection result

```text
CONNECTION = PASS
PORT = /dev/ttyACM0
VID_PID = 0483:5740
CLI_ENTERED = YES
```
