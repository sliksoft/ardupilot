# WP1B_DSHOT_DMA — configure-time DMA / DShot evidence

**Board:** HDZeroHalo  
**Status:** code/configure evidence only — **not TESTED** on hardware  
**HARDWARE_FLASH_ALLOWED = NO**

## Motor configuration (`hwdef.dat`)

| Motor | Pin | Timer | BIDIR |
|-------|-----|-------|-------|
| M1 | PC6 | TIM3_CH1 | yes |
| M2 | PC7 | TIM3_CH2 | no |
| M3 | PC8 | TIM3_CH3 | yes |
| M4 | PC9 | TIM3_CH4 | no |

Pattern matches `AnyleafH7`. LED strip PA10 = TIM1_CH3 **NODMA**. Buzzer = GPIO (not TIM4).

## Protocol defaults

| Protocol | Config | Status |
|----------|--------|--------|
| DShot300 | `MOT_PWM_TYPE 5` in `defaults.parm` | NEEDS_CONFIG → ready for bench |
| DShot600 | Set `MOT_PWM_TYPE 6` after AM32 bench | Supported by same path |
| Bidirectional | `HAL_WITH_BIDIR_DSHOT` defined; enable `SERVO_BLH_BDMASK` on HW | NEEDS_CONFIG / not TESTED |

## DMA_NOSHARE / priority

```text
DMA_PRIORITY TIM3* SPI1* SPI2*
DMA_NOSHARE  TIM3* SPI1* SPI2*
```

## Generator output (`build/HDZeroHalo/hwdef.h`)

Captured in `evidence/wp1b/dma_assignments.txt`:

| Peripheral | Stream (excerpt) |
|------------|------------------|
| TIM3_UP / CH1 / CH3 | DMA1 Stream 0 (shared UP+CH for bdshot) |
| SPI1 RX/TX | DMA1 Stream 1 / 2 |
| SPI2 RX/TX | DMA1 Stream 3 / 4 |
| USART1 RX/TX | DMA1 Stream 6 / DMA2 Stream 7 |
| UART5 RX/TX | DMA2 Stream 0 / 5 |
| ADC1 | DMA1 Stream 5 |

`#define HAL_WITH_BIDIR_DSHOT` present.

## Conflicts

No configure-time unassigned TIM3/SPI fatal. LED NODMA avoids TIM1 vs TIM3 fight. UART3/4 RX-only are NODMA.

## Next (hardware WP)

1. Unloaded DShot300 on AM32  
2. DShot600  
3. `SERVO_BLH_BDMASK` + eRPM quality  
