# WP2A_PE3_POLARITY — switchable 9V VTX rail

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
**GPIO toggling this WP:** none (policy)

## Verdict

| Field | Value |
|-------|-------|
| `PE3_POLARITY` | **ACTIVE_HIGH enable** (software-inferred) |
| Idle / safe hold | **LOW = off** (matches BF PINIO init when non-inverted) |
| Electrically measured on Halo | **NO** |

## HDZero documentation (PROVEN text)

`hd-zero/hdzero-docs` `docs/halo-firmware.md` — “Switchable 9v BEC”:

```text
resource PINIO 1 E03
set pinio_config = 1
set pinio_box = 40
save
```

Then USER1 mode range switches the 9V BEC from the radio.

## Betaflight PINIO semantics (PROVEN code)

`pinio.h`:

- `PINIO_CONFIG_MODE_OUT_PP = 0x01`
- `PINIO_CONFIG_OUT_INVERTED = 0x80`

`pinio_config = 1` ⇒ mode push-pull, **not** inverted.

`pinioInit` for non-inverted:

- `IOLo(io)` at init → idle **LOW**, `state = false`

`pinioSet(index, on)`:

- `newState = on ^ inverted` → when USER1 **on**, pin driven **HIGH**

Therefore: **HIGH enables** the controlled output path that HDZero documents as the switchable 9V BEC; **LOW** is the inactive/off state after boot.

## ArduPilot current hwdef (safe hold)

```text
PE3 VTX_PWR OUTPUT LOW GPIO(83)
```

Not wired to `RELAY` defaults. Remains LOW unless future approved config enables a relay/PINIO mapping. **Do not toggle until hardware confirmation.**

## Classification

| Claim | Status |
|-------|--------|
| PE3 is PINIO resource for 9V BEC | PROVEN (HDZ docs) |
| `pinio_config=1` ⇒ active-HIGH enable, idle LOW | PROVEN (BF pinio.c + CLI) |
| FET / load-switch truth table on PCB | ASSUMED equal to PINIO level (OEM schematic absent) |
| Scope / meter confirmation | ABSENT |

## Sources

- `https://github.com/hd-zero/hdzero-docs/blob/main/docs/halo-firmware.md`
- `https://github.com/betaflight/betaflight/blob/master/src/main/drivers/pinio.c`
- `https://github.com/betaflight/betaflight/blob/master/src/main/drivers/pinio.h`
- Local: `libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo/hwdef.dat` PE3 lines
