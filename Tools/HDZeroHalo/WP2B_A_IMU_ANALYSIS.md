# WP2B_A_IMU_ANALYSIS — gyro variants and orientation

**Date:** 2026-10-18  
**HARDWARE_FLASH_ALLOWED = NO**

## Dual SKU (OEM + BF)

| Claim | Level | Evidence |
| ----- | ----- | -------- |
| Two product versions: MPU6000 **or** ICM42688 | OEM_CONFIRMED | HDZero intro + User Manual v1.5 |
| Not dual-fitted simultaneously | OEM_CONFIRMED / INFERRED | “two versions”; one IMU expected |
| BF compiles both drivers | SOURCE_CONFIRMED | `USE_GYRO_SPI_MPU6000` + `USE_GYRO_SPI_ICM42688P` in Halo `config.h` |
| Field MPU6000 Halo exists | OEM/community | BF issue #14536 title/body |

## SPI1 wiring (SOURCE_CONFIRMED)

| Signal | Pin | BF define |
| ------ | --- | --------- |
| SCK / SDI / SDO | PA5 / PA6 / PA7 | SPI1 |
| GYRO_1 CS | PB4 | `GYRO_1_CS_PIN` |
| GYRO_1 EXTI | PC13 | `GYRO_1_EXTI_PIN` |
| GYRO_2 CS | PB3 | `GYRO_2_CS_PIN` |
| GYRO_2 EXTI | PA15 | `GYRO_2_EXTI_PIN` |
| Bus instance | SPI1 | both gyros |

Master config keeps **both** CS lines so one unified image can probe either SKU.

## CS ↔ SKU mapping

Closed unmerged config PR #835 proposed:

| Target | Gyro | CS | EXTI |
| ------ | ---- | -- | ---- |
| `HDZERO_HALO` | ICM42688P only | PB4 | PC13 |
| `HDZERO_HALO_MPU6000` | MPU6000 only | PB3 | PA15 |

**Level: INFERRED** (PR not merged; matches prior WP1A). ArduPilot dual-probe on both CS remains the safe software strategy.

## WHO_AM_I (SOURCE_CONFIRMED)

| Device | Constant | File |
| ------ | -------- | ---- |
| MPU6000 | `0x68` | `accgyro_mpu.h` L37 |
| ICM42688P | `0x47` | `accgyro_mpu.h` L47 |
| ICM42605 | `0x42` | not Halo-targeted |

Detection: `mpu6000SpiDetect`, `icm426xx` whoAmI switch. Wrong driver rejects before full setup.

## Sensor alignment in Betaflight

| Item | Value | Level |
| ---- | ----- | ----- |
| `GYRO_1_ALIGN` / `GYRO_2_ALIGN` defaults | `CW0_DEG` if unset (`pg/gyrodev.c` L63–67) | SOURCE_CONFIRMED |
| Halo `config.h` alignment override | **None** | SOURCE_CONFIRMED |
| OEM CLI alignment | **None** | OEM_CONFIRMED |
| Driver raw axes | Standard register XYZ order (MPU accel/gyro outs; ICM `GYRO_DATA_X1` / `ACCEL_DATA_X1`) | SOURCE_CONFIRMED |

BF CW0 means “use driver frame as body frame” after BF’s own alignment matrix path — **not** a laboratory measurement of package rotation on the Halo PCB.

## ArduPilot comparison

Current `hwdef.dat`:

```text
IMU Invensensev3 … ROTATION_NONE
IMU Invensense   … ROTATION_ROLL_180_YAW_90
```

### What is software-proved

From WP2A / driver math (retained):

- Invensense (MPU) applies `(y, x, -z)` on raw registers.
- `ROTATION_ROLL_180_YAW_90` cancels that to the raw-register identity.
- Invensensev3 (ICM) keeps XYZ; `ROTATION_NONE` keeps identity.
- Relative MPU vs ICM frames are therefore aligned to a common **raw-register** reference.

### What is not proved

| Question | Level |
| -------- | ----- |
| Absolute mounting of that reference to Halo body / silkscreen | HARDWARE_REQUIRED |
| Whether OEM PCB rotates MPU and ICM packages identically | HARDWARE_REQUIRED |
| Six-face static accel / signed gyro rotation on each SKU | HARDWARE_REQUIRED |
| Photos / BOM / package orientation drawings | Not found in OEM text docs |

**IMU_ROTATION = RELATIVE_SOFTWARE_NORMALISED; ABSOLUTE_UNKNOWN**

## Production revisions

| Revision signal | Finding |
| --------------- | ------- |
| Gyro SKU split | Documented by HDZero |
| Config PR #835 | Would have split BF targets; not in master |
| Later config defaults (MSP DP, current scale) | Does not change IMU pins/align |
| PCB crystal / IMU placement drawings | Not obtained |

## Required physical checks (not done)

1. Read WHO_AM_I on PB4 and PB3; identify SKU and live CS.  
2. Photograph IMU package vs board axes / motor order silkscreen.  
3. Six static faces + signed rotations for the fitted SKU.  
4. Repeat on the other SKU before claiming one AP rotation for all boards.
