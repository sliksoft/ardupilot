# WP2A_TIM3_DMA — shared UP/CH1/CH3 DMA stream review

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**  
**On-hardware DShot:** not TESTED

## Verdict

| Field | Value |
|-------|-------|
| `TIM3_DMA_REVIEW` | **PASS (code/configure)** — shared stream is intentional for H7 bdshot |
| Hardware eRPM quality | UNKNOWN |

## Generator output (`build/HDZeroHalo/hwdef.h`)

```text
STM32_TIM_TIM3_UP_DMA_STREAM   STM32_DMA_STREAM_ID(1, 0)
STM32_TIM_TIM3_CH1_DMA_STREAM  STM32_DMA_STREAM_ID(1, 0)
STM32_TIM_TIM3_CH3_DMA_STREAM  STM32_DMA_STREAM_ID(1, 0)
STM32_TIM_TIM3_UP_DMA_CHAN     STM32_DMAMUX1_TIM3_UP
STM32_TIM_TIM3_CH1_DMA_CHAN    STM32_DMAMUX1_TIM3_CH1
STM32_TIM_TIM3_CH3_DMA_CHAN    STM32_DMAMUX1_TIM3_CH3
HAL_WITH_BIDIR_DSHOT           defined
```

Same **DMA1 Stream 0** for UP + CH1 + CH3; **DMAMUX request IDs differ**.

## Why sharing is expected

ArduPilot bidirectional DShot on ChibiOS uses timer DMAR for the burst, then input-capture DMA on BIDIR channels. On STM32H7, UP and CHx often resolve to one stream; the driver time-muxes the DMAMUX request and uses `Shared_DMA`:

- `RCOutput_bdshot.cpp` — when IC stream equals group UP stream, reuses `group.dma_handle` instead of allocating a second stream (`bdshot_setup_group_ic_DMA` / shared-handle path).
- Peer board: `AnyleafH7` TIM3 PC6–PC9 + BIDIR (same motor pin/timer pattern).

`DMA_NOSHARE TIM3*` prevents other peripherals from stealing that stream; LED strip is `NODMA` on TIM1.

## Motor pin / BIDIR map (hwdef)

| Motor | Pin | Timer ch | BIDIR in hwdef |
|-------|-----|----------|----------------|
| M1 | PC6 | TIM3_CH1 | yes |
| M2 | PC7 | TIM3_CH2 | no |
| M3 | PC8 | TIM3_CH3 | yes |
| M4 | PC9 | TIM3_CH4 | no |

Matches Anyleaf-style “twin BIDIR” (CH1+CH3 capture pair).

## Residual risk (not blockers for offline)

| Risk | Notes |
|------|-------|
| Configure conflict | None observed for TIM3/SPI |
| Runtime bdshot | Needs AM32 unloaded bench; not done |
| Wrong HSE | Would invalidate DShot bit timing even if DMA map is correct |

## Sources

- Local: `build/HDZeroHalo/hwdef.h` L281–286, L338+  
- Local: `libraries/AP_HAL_ChibiOS/RCOutput_bdshot.cpp` (shared DMA handle)  
- Local: `Tools/HDZeroHalo/WP1B_DSHOT_DMA.md`  
- Peer: `libraries/AP_HAL_ChibiOS/hwdef/AnyleafH7/hwdef.dat`
