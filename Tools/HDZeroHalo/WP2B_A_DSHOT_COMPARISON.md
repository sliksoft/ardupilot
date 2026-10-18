# WP2B_A_DSHOT_COMPARISON — ESC / DShot / DMA

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Halo motor hardware in Betaflight (SOURCE_CONFIRMED)

| Motor | Pin | Timer map comment | DMA note |
| ----- | --- | ----------------- | -------- |
| M1 | PC6 | TIM3 CH1 | `TIMER_PIN_MAP(0,…,0)` |
| M2 | PC7 | TIM3 CH2 | opt 1 |
| M3 | PC8 | TIM3 CH3 | opt 2 |
| M4 | PC9 | TIM3 CH4 | opt 3 |
| TIM3 update | — | `TIMUP3_DMA_OPT 5` | Halo config |
| LED strip | PA10 | TIM1 CH3 | separate |

`DEFAULT_DSHOT_BITBANG DSHOT_BITBANG_ON` — Halo **defaults to bitbang DShot**, not timer-DMA DShot.

## Protocol defaults (SOURCE_CONFIRMED)

| Setting | BF 4.5.1 Halo path |
| ------- | ------------------ |
| Motor PWM protocol default | `PWM_TYPE_DSHOT600` (`pg/motor.c` when not brushed/disabled) |
| DShot bitbang | **ON** for Halo |
| DShot telemetry (bidir) default | `DSHOT_TELEMETRY_OFF` |
| OEM CLI motor protocol | Not overridden |
| ESC telemetry UART | UART4 RX PA1 (hardware pin); separate from bidir DShot |

OEM User Manual v1.5: Halo ESC supports DSHOT 150/300/600/1200/**2400**, MultiShot, OneShot; AM32 or BLHeli32; FC cable telemetry supported.

## Bidirectional DShot

BF can enable `dshot_bidir` / telemetry in CLI, but Halo **defaults OFF**. Bitbang implementation lives in `drivers/stm32/dshot_bitbang*.c` — a different hardware mechanism from ArduPilot’s TIM3 DMAR + input-capture bdshot path.

**A working BF bitbang DShot path does not prove the ArduPilot TIM3-DMA / Shared_DMA path.**

## New hardware information vs prior WPs

| Item | Already known (WP1/WP2A) | New / reinforced in WP2B-A |
| ---- | ------------------------ | -------------------------- |
| PC6–9 TIM3 | Yes | Confirmed in pinned `0096077` + ELF build |
| Bitbang default ON | Yes | Confirmed; still the BF production default |
| TIMUP3_DMA_OPT 5 | Yes | Still present (relevant if bitbang disabled) |
| Default DSHOT600 | Often assumed | Confirmed in `pg/motor.c` default chain |
| Bidir default OFF | Partially | Explicit `DEFAULT_DSHOT_TELEMETRY OFF` |
| ESC scale 170 | ESC doc | Confirmed in User Manual v1.5 ESC section |
| AM32 / BLHeli32 variants | Docs | Manual: target `HDZ_ESC_1R0_F421`, AM32 2.18 / BLHeli 32.10 |

No alternate motor timer mux or hidden fifth motor channel found in Halo config.

## ArduPilot comparison

| Topic | ArduPilot HDZeroHalo | Betaflight Halo |
| ----- | -------------------- | --------------- |
| Pins / timer | PC6–9 TIM3 CH1–4 | Same |
| Primary path | Timer DMA + bdshot (`BIDIR` on CH1/CH3) | Bitbang ON by default |
| Default rate | `MOT_PWM_TYPE` 5 (DShot300) in defaults | DShot600 protocol default |
| DMA | DMA1 Stream0 shared UP/CH1/CH3 + DMAMUX | Bitbang uses different resources; TIMUP opt reserved |
| LED strip | PA10 NODMA / unsupported addressable | TIM1 CH3 with strip feature |

## Risks

1. Validating motors only under BF bitbang leaves AP DMA/bdshot unproved.  
2. Wrong HSE invalidates both stacks’ bit timing.  
3. ESC firmware (AM32 vs BLHeli32) and bidir support must be qualified per ESC SKU.  
4. Enabling BF timer DShot (bitbang off) would exercise `TIMUP3_DMA_OPT` — not the AP driver.

## Verdict

```text
TIM3_DSHOT = PINS_AND_TIMER_SOURCE_CONFIRMED
BIDIR_DSHOT = BF_DEFAULT_OFF; AP_PATH_SEPARATE_UNVERIFIED_ON_HW
BF_BITBANG = DEFAULT_ON
```
