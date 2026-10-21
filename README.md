<p align="center">
  <img src="Tools/HDZeroHalo/assets/redline-dynamics-banner.png" alt="Redline Dynamics — Autonomous Flight. Real Performance." width="800">
</p>
<p align="center"><strong>HDZero Halo · ArduCopter · Autonomous Missions</strong></p>

An independent **ArduCopter port for the HDZero Halo STM32H743 flight controller**, developed as a foundation for an autonomous drone with AI-assisted missions, LiDAR and obstacle avoidance.

## Project status

**USB bench-tested (October 2026)**

- ArduCopter starts on the physical HDZero Halo.
- USB CDC / MAVLink communication with Mission Planner works.
- Gyroscope, accelerometer and roll/pitch orientation validated.
- Quad/X and DShot300 outputs 1–4 configured; electrical motor signals not tested.

**Next:** integrate and qualify navigation hardware, AI companion computer, LiDAR, power system and failsafes. **No autonomous flight or LiDAR operation has been demonstrated yet.**

## Source & documentation

- [HDZero Halo development branch](https://github.com/sliksoft/ardupilot/tree/board/hdzero-halo) — the latest locally tested commits may not yet be pushed.
- [HDZero Halo technical documentation](https://github.com/sliksoft/ardupilot/tree/board/hdzero-halo/Tools/HDZeroHalo)
- [Original ArduPilot project](https://github.com/ArduPilot/ardupilot)

This is **experimental, independently developed firmware**, not an official ArduPilot or HDZero release. The USB tests do not establish flight readiness.

Based on **ArduPilot**, with original author attribution and **GPL-3.0** licensing retained. See [COPYING.txt](COPYING.txt).
