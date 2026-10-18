# Halo external barometer and startup safety

Status: **HARDWARE_FLASH_ALLOWED = NO**

## Standard firmware

Halo has no established onboard barometer. The firmware requires a supported
external one on I2C1 (PB8 SCL/PB9 SDA). The no-baro compile-time bypass is
removed entirely; defining it as zero would still activate its `#ifdef` paths.
No shared sensor driver, flight algorithm or arming parameter is changed.

Default `BARO_PROBE_EXT=1030` enables BMP280 (2), MS5611 (4) and BMP388 (1024)
through the existing external I2C probe table. `BARO_EXT_BUS=-1` scans external
buses; this board declares I2C1 external. An existing saved mask overrides the
new default. Select the required sensor mask, save and reboot to retry probing.

| Model | Mask | Probe addresses | Driver |
| ------- | -----: | ----------------- | -------- |
| BMP280 | 2 | 0x76, 0x77 | AP_Baro_BMP280 |
| MS5611 | 4 | 0x77, 0x76 | AP_Baro_MS5611 |
| BMP388 | 1024 | 0x76, 0x77 | AP_Baro_BMP388 |

Additional compiled external I2C selections are BMP085 (1), MS5607 (8),
MS5637 (16), FBM320 (32), DPS280 (64), LPS25H via LPS2XH (128), SPL06 (2048)
and BMP581 (8192). AUAV (16384) additionally depends on its airspeed backend;
MSP (4096) uses the MSP sensor path rather than this physical I2C probe table.
The fix report's preprocessor log records actual backend definitions.

These are compiled software paths, not qualified Halo peripherals. Other mask
bits remain subject to backend availability. In particular bit6 selects DPS280;
it does not instantiate the
separate DPS310 subclass/temperature workaround. DPS310 is not claimed as a
qualified configuration. Keller/MS5837 entries are vehicle-conditional and are
not claimed for this Copter build.

## No-baro bench state

If no driver is detected, `AP_Baro::init()` calls
`AP_BoardConfig::config_error("Baro: unable to initialise driver")`. The existing
loop reports the error periodically, services MAVLink receive/send and delays
through the scheduler. It is a deliberate recovery state, not an uncontrolled
crash or a fake sensor. USB console setup precedes sensor initialisation.
Parameter writes can be saved; reboot is required to attempt detection again.

This does **not** complete normal Copter startup. Telemetry UART and OSD setup
occur after barometer initialisation and must not be promised in this state.
It is unsuitable for arming, flight or motor testing. No separate no-baro image
or instruction to disable arming checks is supplied.

## Detected but unhealthy sensor

With the bypass absent, `AP_Arming::barometer_checks()` calls the standard
`AP_Baro::arming_checks()`, including `all_healthy()`, when normal barometer
arming checks are enabled. A failed health check returns false. Copter's
additional altitude comparison is retained. Existing user-saved arming settings
must also be checked during later qualification; this WP does not alter them.

The offline regression compiles the actual production prearm method against
generated Halo definitions and an unhealthy/healthy sensor boundary. Reintroducing
the old bypass makes that probe fail. This checks dispatch/control flow, not
physical sensor health, pressure accuracy or full-vehicle startup behaviour.

## Source anchors and later evidence

- `AP_Baro.cpp:69-70,181-187,715-740,783-851,1138-1163`.
- `AP_Arming.cpp:394-413`; `ArduCopter/AP_Arming_Copter.cpp:127-150`.
- `AP_BoardConfig.cpp:550-606`; `AP_Vehicle.cpp` early console setup;
  `ArduCopter/system.cpp:35-41` sensor/UART/OSD ordering.
- Existing SITL `ConfigErrorLoop`, `BaroDrivers`, `SensorErrorFlags` provide
  broader integration scenarios; only tests explicitly listed in the fix report
  were run. SITL success would not establish physical I2C or barometer health.

Required hardware evidence: correct supply/pull-ups, model/address/identity,
plausible pressure/temperature/altitude, disconnected/unhealthy-sensor rejection,
and USB recovery without a detected sensor. None was performed here.
