# WP4-B: Quad/X frame configuration

Date: 2026-10-21. Parameter change on the live WP3-K vehicle **after** WP4-A
and **before** WP4-C. No flash. This note records the resulting baseline state
verified by the WP4-C inventory.

```text
FRAME_CLASS                    = 1   # Quad
FRAME_TYPE                     = 1   # X
STATUSTEXT                     = Frame: QUAD/X
PREARM_FRAME_CLASS             = CLEARED (no longer reported)
HARDWARE_FLASH_ALLOWED         = NO
```

## Context

WP4-A measured `FRAME_CLASS=0` / `FRAME_TYPE=12` and PreArm
`FRAME_CLASS` on the USB bench. Those live parameters were then set to Quad/X
(`1` / `1`). WP4-C re-read the vehicle and confirmed:

| Param | Live | Notes |
| --- | --- | --- |
| `FRAME_CLASS` | 1 | Quad |
| `FRAME_TYPE` | 1 | X — differs from hwdef `HAL_FRAME_TYPE_DEFAULT 12` |
| STATUSTEXT | `Frame: QUAD/X` | No FRAME PreArm |

Evidence: `evidence/wp4-c/WP4_C_REPORT.md` and `evidence/wp4-c/all_params.csv`.

## Limits

- Configuration only; not an arming or motor qualification.
- Hwdef default `FRAME_TYPE` remains 12 until a separate source change is
  authorized. Fresh flashes without saved params will not match this live state.
