# WP2B_A_POWER_ADC — PE3 9V, ADC, battery, current

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## PE3 / switchable 9V BEC

### Configuration sources

| Source | PE3 / PINIO content |
| ------ | ------------------- |
| Halo `config.h` (all revisions) | **No** PINIO / PE3 defines |
| OEM CLI zip `HDZERO_HALO.txt` | **No** PINIO lines |
| HDZero firmware docs / User Manual | Explicit CLI: `resource PINIO 1 E03`, `set pinio_config = 1`, `set pinio_box = 40`, USER1 mode |

So PE3 is an **OEM post-flash / documented** resource assignment, not compiled into the board `config.h`.

### Betaflight PINIO semantics (SOURCE_CONFIRMED)

Files: `drivers/pinio.h`, `drivers/pinio.c` (BF 4.5.1).

- `pinio_config = 1` ⇒ `PINIO_CONFIG_MODE_OUT_PP` (0x01), **not** `PINIO_CONFIG_OUT_INVERTED` (0x80).
- Non-inverted init: `IOLo` → idle **LOW**, `state = false` (`pinio.c` L106–110).
- `pinioSet(index, on)`: `newState = on ^ inverted` → USER1 **on** drives **HIGH**.

**Software polarity: ACTIVE_HIGH enable, idle LOW after pinioInit.**

### Not proved from firmware

| Topic | Level |
| ----- | ----- |
| FET / load-switch truth table vs GPIO level | HARDWARE_REQUIRED |
| 9V rail voltage when PE3 HIGH/LOW | HARDWARE_REQUIRED |
| State during MCU reset, brownout, ROM DFU (before GPIO init) | HARDWARE_REQUIRED |
| Whether factory images pre-apply PINIO resource | UNKNOWN (docs say online firmware “contains required CLI”; downloadable CLI lacks PINIO) |

### ArduPilot comparison

`hwdef.dat` / `hwdef-bl.dat`: `PE3 VTX_PWR OUTPUT LOW` — holds LOW after GPIO init; not bound to RELAY auto-on. Matches BF idle intent; does not prove rail-off across reset.

---

## ADC pins (SOURCE_CONFIRMED)

| Function | Pin | BF |
| -------- | --- | -- |
| VBAT | PC0 | `ADC_VBAT_PIN` |
| RSSI | PC1 | `ADC_RSSI_PIN` |
| Current | PC2 | `ADC_CURR_PIN` |
| Sources | ADC meters | `DEFAULT_*_METER_SOURCE …_ADC` |

## Voltage scale

BF 4.5.1 defaults (`sensors/voltage.c` L105–114, L142–144, L167):

| Parameter | Default | Halo override |
| --------- | ------- | ------------- |
| `vbat_scale` | **110** | None in config / OEM CLI |
| `vbat_divider` | **10** | None |
| `vbat_multiplier` | **1** | None |

Conversion (centivolts):

```text
((((src * vbatscale * getVrefMv() / 10) + (0xFFF*5)) / (0xFFF * divider)) / multiplier)
```

Comment in BF: scale 110 with 10:1 divider corresponds to reporting battery volts from the divider network.  
Nominal battery/ADC-pin factor used by AP as `HAL_BATT_VOLT_SCALE 11.0` is the **software-equivalent** of scale110/div10/mult1 — **INFERRED / SOURCE formula**, not resistor measurement.

Vref: H7 path uses internal Vrefint calibration (`getVrefMv`); fallback path can report 3300 mV (`adcinternal.c`). Physical divider resistors **HARDWARE_REQUIRED**.

## Current scale

| Source | Scale | Units |
| ------ | ----- | ----- |
| BF generic default | 400 | mV/10A (`current.c` L93–94) |
| Halo config `0096077` | *(no `#define DEFAULT_CURRENT_METER_SCALE`)* | — |
| OEM CLI | `ibata_scale = 100` | OEM_CONFIRMED |
| Halo config ≥ `d3abecf` | `#define DEFAULT_CURRENT_METER_SCALE 100` | SOURCE_CONFIRMED |
| ESC manual current sensor | scale **170**, offset 0 | OEM ESC — **different sensor** |

BF ADC current (`current.c` ~L118–119): scale in **mV/10A**;  
`centiAmps = (millivolts * 10000 / scale + offset) / 10`.

ArduPilot `BATT_AMP_PERVLT` / `HAL_BATT_CURR_SCALE` is **A/V**. Conversion:

```text
AP_A_PER_V = 10000 / BF_ibata_scale
```

For BF 100 → AP **100** A/V. Numerical equality is coincidence of units; do not assume for other scales.

## Nominal Halo reconstruction

| Quantity | Reconstructed nominal | Level |
| -------- | --------------------- | ----- |
| VBAT | BF 110/10/1 → AP mult **11.0** | SOURCE_CONFIRMED defaults; uncalibrated |
| Current (FC ADC) | **100** (BF) → AP **100** A/V | OEM CLI + later config |
| ESC current | 170 | OEM ESC doc; not FC ADC |
| RSSI PC1 | Present; no OEM scale | UNKNOWN |

## ArduPilot vs BF unit warning

Same names ≠ same units. Always convert with the formulas above; calibrate on hardware before failsafes.
