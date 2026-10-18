"""Offline checks of generated Halo configuration and its barometer arming path.

AP_FLAKE8_CLEAN
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOARD = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo'
GENERATOR = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py'


class HaloConfigurationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        cls.outputs = {}
        for name, filename, options in (
                ('app', 'hwdef.dat', []),
                ('bootloader', 'hwdef-bl.dat', ['--bootloader'])):
            outdir = Path(cls.directory.name) / name
            outdir.mkdir()
            result = subprocess.run([sys.executable, str(GENERATOR), '--quiet', '--outdir', str(outdir),
                                     '--params', str(BOARD / 'defaults.parm'), *options, str(BOARD / filename)],
                                    cwd=ROOT, capture_output=True, text=True)
            if result.returncode != 0:
                raise AssertionError(result.stdout + result.stderr)
            cls.outputs[name] = outdir

    def compile_and_run(self, configuration, program, defines=()):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'probe.cpp'
            binary = Path(directory) / 'probe'
            source.write_text(program)
            result = subprocess.run(['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                                     '-I', str(self.outputs[configuration]), *defines,
                                     str(source), '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return subprocess.run([str(binary)], capture_output=True, text=True)

    def test_initial_output_levels(self):
        for configuration in self.outputs:
            with self.subTest(configuration=configuration):
                program = '''
#include "hwdef.h"
static_assert((VAL_GPIOD_MODER & (3U << 24)) == (1U << 24), "PD12 must be output");
static_assert((VAL_GPIOD_ODR & (1U << 12)) == 0, "active-high buzzer must start off");
static_assert((VAL_GPIOE_MODER & (3U << 6)) == (1U << 6), "PE3 must be output");
static_assert((VAL_GPIOE_ODR & (1U << 3)) == 0, "PE3 inactive level after init");
int main() { return 0; }
'''
                self.assertEqual(self.compile_and_run(configuration, program).returncode, 0)

    def barometer_probe(self, defines=()):
        source = (ROOT / 'libraries/AP_Arming/AP_Arming.cpp').read_text()
        start = source.index('bool AP_Arming::barometer_checks(bool report)')
        end = source.index('\n#if AP_AIRSPEED_ENABLED', start)
        # Compile the production method, not a reimplementation of its guard.
        program = '''
#include <cstddef>
#include "hwdef.h"
#define CONFIG_HAL_BOARD 10
#define HAL_BOARD_SITL 3
#define MAVLINK_MSG_STATUSTEXT_FIELD_TEXT_LEN 50
struct Barometer {
    bool healthy = false;
    unsigned calls = 0;
    bool arming_checks(size_t, char *) { ++calls; return healthy; }
};
namespace AP {
    Barometer sensor;
    Barometer &baro() { return sensor; }
}
struct AP_Arming {
    enum class Check { BARO };
    unsigned failures = 0;
    bool check_enabled(Check) const { return true; }
    void check_failed(Check, bool, const char *, const char *) { ++failures; }
    bool barometer_checks(bool report);
};
'''
        program += source[start:end]
        program += '''
int main() {
    AP_Arming arming;
    if (arming.barometer_checks(true) || AP::baro().calls != 1 || arming.failures != 1) {
        return 1;
    }
    AP::baro().healthy = true;
    if (!arming.barometer_checks(true) || AP::baro().calls != 2 || arming.failures != 1) {
        return 2;
    }
    return 0;
}
'''
        return self.compile_and_run('app', program, defines)

    def test_barometer_health_reaches_prearm_check(self):
        self.assertEqual(self.barometer_probe().returncode, 0)

    def test_probe_detects_previous_barometer_bypass(self):
        self.assertEqual(self.barometer_probe(('-DHAL_BARO_ALLOW_INIT_NO_BARO=1',)).returncode, 1)

    def test_external_barometer_and_buzzer_defaults(self):
        program = '''
#include "hwdef.h"
static_assert(DEFAULT_BUZZ_ON_LVL == 1, "buzzer must be active high");
static_assert(AP_BARO_PROBE_EXTERNAL_I2C_BUSES == 1, "external probes required");
static_assert(HAL_BARO_PROBE_EXT_DEFAULT == ((1 << 1) | (1 << 2) | (1 << 10)), "probe mask");
int main() { return 0; }
'''
        self.assertEqual(self.compile_and_run('app', program).returncode, 0)

    def test_tim3_capture_shares_only_its_own_output_stream(self):
        header = (self.outputs['app'] / 'hwdef.h').read_text()
        mappings = re.findall(r'#define\s+(\w+_DMA_STREAM)\s+STM32_DMA_STREAM_ID\((\d+),\s*(\d+)\)', header)
        streams = {name: (int(controller), int(stream)) for name, controller, stream in mappings}
        motor = streams.pop('STM32_TIM_TIM3_UP_DMA_STREAM')
        self.assertEqual(streams.pop('STM32_TIM_TIM3_CH1_DMA_STREAM'), motor)
        self.assertEqual(streams.pop('STM32_TIM_TIM3_CH3_DMA_STREAM'), motor)
        self.assertNotIn(motor, streams.values())
        self.assertEqual(len(streams), len(set(streams.values())))
        self.assertEqual(len(streams), 15)
        self.assertNotIn('STM32_TIM_TIM1_UP_DMA_STREAM', streams)


if __name__ == '__main__':
    unittest.main()
