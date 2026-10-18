# WP1A_DSHOT_DMA — DShot300 / DShot600 / bidirectional feasibility

**Date:** 2026-10-18  
**Priority:** mandatory protocols for this port  
**Halo motors:** PC6–PC9 on TIM3 CH1–4 (Betaflight `config.h` L51–54, L87–90)

Status tags apply to **code-level feasibility only**. Nothing is **TESTED** on Halo hardware.

## How ArduPilot differs from Betaflight

| Aspect | Betaflight Halo | ArduPilot ChibiOS |
|--------|-----------------|-------------------|
| Default motor protocol path | `DEFAULT_DSHOT_BITBANG DSHOT_BITBANG_ON` (`config.h` L102) | Timer **DMAR** PWM groups (`RCOutput.cpp`, comment L16–21) |
| Bi-dir RPM | BF bdshot / bitbang paths | `HAL_WITH_BIDIR_DSHOT` when hwdef has `BIDIR` (`chibios_hwdef.py` L2200–2201) |
| Rate selection | BF CLI | `MOT_PWM_TYPE` 5=DShot300, 6=DShot600 (`AP_MotorsMulticopter.cpp` L99) |

**Conclusion:** BF bitbang being ON does **not** prove ArduPilot must use bitbang. ArduPilot’s supported path is timer+DMA on the TIM3 channels.

## STM32 pin capability

From `libraries/AP_HAL_ChibiOS/hwdef/scripts/STM32H743xx.py`:

- `PC6:TIM3_CH1`, `PC7:TIM3_CH2`, `PC8:TIM3_CH3`, `PC9:TIM3_CH4` — all present.

## In-tree precedent (strongest evidence)

`AnyleafH7/hwdef.dat` L86–89, L100:

```text
PC6  TIM3_CH1 TIM3  PWM(1)  GPIO(50)  BIDIR
PC7  TIM3_CH2 TIM3  PWM(2)  GPIO(51)
PC8  TIM3_CH3 TIM3  PWM(3)  GPIO(52)  BIDIR
PC9  TIM3_CH4 TIM3  PWM(4)  GPIO(53)
DMA_NOSHARE SPI1* TIM3* TIM15* TIM1*
```

Same four motor pins, same TIM3 mapping, with bidirectional DShot enabled in an official-style H743 hwdef.

## Comparison boards (requested)

| Board | Motor TIM / BIDIR | Relevance |
|-------|-------------------|-----------|
| TBS_LUCID_H7 | TIM3 CH3/4 BIDIR + TIM2/5/4 (`hwdef.dat` L145–154); `DMA_NOSHARE` TIM3*… L186 | TIM3 bdshot + DMA discipline |
| MatekH743-bdshot | Remap to TIM3/TIM2/TIM5/TIM4 BIDIR L23–30; DMA L44–45 | Classic H743 bdshot pattern |
| GEPRC_TAKER_H743 | TIM3 CH1–4 with BIDIR on M1/M4 L117–121 | TIM3 FPV quad |
| FoxeerH743v1 | TIM3 BIDIR L128–131 | TIM3 + SPI flash board |
| TMotorH743 | TIM5 BIDIR L121–124 | DShot on single timer group |
| **AnyleafH7** | **PC6–9 TIM3 BIDIR** L86–89 | **Best pin match** |

## Feasibility verdicts

### DShot300 — NEEDS_CONFIG (mechanism SUPPORTED)

- Protocol enum and RCOutput DMAR path exist.
- Requires Halo hwdef PWM lines on TIM3 CH1–4 + successful DMA resolve.
- Not TESTED on Halo.

### DShot600 — NEEDS_CONFIG (mechanism SUPPORTED)

- Same path as DShot300; higher bit rate, same timer/DMA requirements.
- Timing sensitivity noted in `RCOutput.cpp` L238+.
- Not TESTED on Halo / AM32 combo.

### Bidirectional DShot — NEEDS_CONFIG (mechanism SUPPORTED)

- Enable with `BIDIR` on complementary channels (typical CH1/CH3 pattern as Anyleaf).
- Generates `HAL_WITH_BIDIR_DSHOT` (`chibios_hwdef.py` L2201).
- Requires `DMA_NOSHARE` protecting `TIM3*` from SPI/UART steal (`dma_resolver.py` L300–369 sets `has_bdshot` when `_CH` peripherals present).
- ESC RPM via `RCOutput::get_erpm()` (`RCOutput.h` L72–80).
- Not TESTED on Halo.

### AM32

- HDZero docs for related products reference AM32 targets (e.g. Gamma intro `AM32_HDZERO_HALO_F421`).
- ArduPilot DShot + AM32 is widely used; no Halo-specific incompatibility found in code search.
- Passthrough / configuration remains a **hardware validation** item (UNKNOWN / not TESTED).

## DMA / peripheral conflict plan

Recommended hwdef discipline (from Anyleaf + Lucid):

```text
DMA_PRIORITY TIM3* SPI1* SPI2*
DMA_NOSHARE  TIM3* SPI1* SPI2*
```

| Peripheral | Halo pin/bus | Conflict risk | Mitigation |
|------------|--------------|---------------|------------|
| Motors TIM3 | PC6–9 | Critical — needs UP + CH DMA for bdshot | `DMA_NOSHARE TIM3*` |
| SPI1 IMU | PA5–7 | High during fast sampling | `DMA_NOSHARE SPI1*` |
| SPI2 flash | PB13–15 | Logging DMA | `DMA_NOSHARE SPI2*` |
| LED TIM1 CH3 | PA10 | Medium — LED vs TIM1 DMA | Prefer `NODMA` on LED PWM or isolate TIM1 |
| Buzzer | PD12 | Low if GPIO | Use `BUZZER OUTPUT GPIO` (not TIM4 ALARM) |
| UART1 ELRS | PB6/7 | Medium | Keep DMA if possible; CRSF can work NODMA |
| UART5 MSP DP | PC12/PD2 | Medium–High for OSD | Prefer DMA-capable UART assignment |
| ADC1 | PC0/1/2 | Medium | Standard ADC DMA; H7 DMAMUX helps |

H743 **DMAMUX** (`dma_resolver.py` L329+) makes assignment more flexible than F4 fixed maps; configure-time `./waf configure --board …` is the proof that streams resolve.

## ESC RPM telemetry alternatives

1. Bidirectional DShot eRPM (preferred if DMA OK).
2. UART ESC telemetry on **UART4 RX PA1** (HDZ “ESC Telemetry RX4”; BF L64) via `SerialProtocol_ESCTelemetry`.

## WP1B / later validation gates (not WP1A)

- Configure-time DMA map must assign TIM3 without fatal unassigned peripherals.
- Bench: DShot300 then DShot600 on AM32, motors unloaded.
- Bench: bdshot eRPM cleanliness.
- Never mark TESTED from code review alone.
