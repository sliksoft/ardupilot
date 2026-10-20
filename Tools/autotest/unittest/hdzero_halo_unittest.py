"""Offline checks of generated Halo configuration and barometer no-baro path.

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

    def test_software_dfu_disabled_without_startup_hook(self):
        for configuration in self.outputs:
            with self.subTest(configuration=configuration):
                program = '''
#include "hwdef.h"
#if HAL_ENABLE_DFU_BOOT
#error "Halo must not advertise software DFU without startup hook support"
#endif
int main() { return 0; }
'''
                self.assertEqual(self.compile_and_run(configuration, program).returncode, 0)

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

    def barometer_probe(self, *, undef_macro=False):
        source = (ROOT / 'libraries/AP_Arming/AP_Arming.cpp').read_text()
        start = source.index('bool AP_Arming::barometer_checks(bool report)')
        end = source.index('\n#if AP_AIRSPEED_ENABLED', start)
        # Compile the production method, not a reimplementation of its guard.
        program = '''
#include <cstddef>
#include "hwdef.h"
'''
        if undef_macro:
            program += '#undef HAL_BARO_ALLOW_INIT_NO_BARO\n'
        program += '''
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
        if undef_macro:
            # Upstream path without the board macro: unhealthy fails, healthy passes.
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
        else:
            # Board macro present: always true, arming_checks never called.
            program += '''
int main() {
    AP_Arming arming;
    if (!arming.barometer_checks(true) || AP::baro().calls != 0 || arming.failures != 0) {
        return 1;
    }
    AP::baro().healthy = false;
    if (!arming.barometer_checks(true) || AP::baro().calls != 0 || arming.failures != 0) {
        return 2;
    }
    return 0;
}
'''
        return self.compile_and_run('app', program)

    def test_hal_baro_allow_init_no_baro_in_generated_config(self):
        program = '''
#include "hwdef.h"
#ifndef HAL_BARO_ALLOW_INIT_NO_BARO
#error "HAL_BARO_ALLOW_INIT_NO_BARO must be defined for Halo"
#endif
int main() { return 0; }
'''
        self.assertEqual(self.compile_and_run('app', program).returncode, 0)
        hwdef = (BOARD / 'hwdef.dat').read_text()
        self.assertRegex(hwdef, r'define\s+HAL_BARO_ALLOW_INIT_NO_BARO\s+1')

    def test_barometer_prearm_skipped_with_board_macro(self):
        self.assertEqual(self.barometer_probe().returncode, 0)

    def test_upstream_baro_health_path_without_macro(self):
        self.assertEqual(self.barometer_probe(undef_macro=True).returncode, 0)

    def test_external_barometer_and_buzzer_defaults(self):
        program = '''
#include "hwdef.h"
static_assert(DEFAULT_BUZZ_ON_LVL == 1, "buzzer must be active high");
static_assert(AP_BARO_PROBE_EXTERNAL_I2C_BUSES == 1, "external probes required");
static_assert(HAL_BARO_PROBE_EXT_DEFAULT == ((1 << 1) | (1 << 2) | (1 << 10)), "probe mask");
#ifndef HAL_BARO_ALLOW_INIT_NO_BARO
#error "no-baro init macro required"
#endif
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

    def test_imu_probe_rotations_frd(self):
        """Both CS variants: ICM ROLL_180, MPU YAW_270 (WP2B-D)."""
        header = (self.outputs['app'] / 'hwdef.h').read_text()
        self.assertIn(
            'AP_InertialSensor_Invensensev3::probe(*this,hal.spi->get_device("icm42688_1"),ROTATION_ROLL_180)',
            header)
        self.assertIn(
            'AP_InertialSensor_Invensensev3::probe(*this,hal.spi->get_device("icm42688_2"),ROTATION_ROLL_180)',
            header)
        self.assertIn(
            'AP_InertialSensor_Invensense::probe(*this,hal.spi->get_device("mpu6000_1"),ROTATION_YAW_270)',
            header)
        self.assertIn(
            'AP_InertialSensor_Invensense::probe(*this,hal.spi->get_device("mpu6000_2"),ROTATION_YAW_270)',
            header)
        self.assertNotIn('icm42688_1"),ROTATION_NONE)', header)
        self.assertNotIn('mpu6000_1"),ROTATION_ROLL_180_YAW_90)', header)

    def test_roll_180_matrix_and_determinant(self):
        """ROTATION_ROLL_180 is (x,y,z)->(x,-y,-z); det=+1 (matches AP_Math)."""
        # Mirror libraries/AP_Math/vector3.cpp ROTATION_ROLL_180 and test_math.cpp
        def roll180(v):
            x, y, z = v
            return (x, -y, -z)

        self.assertEqual(roll180((1, 1, 1)), (1, -1, -1))
        self.assertEqual(roll180((1, 2, 3)), (1, -2, -3))
        # Columns of R = diag(1,-1,-1); det = +1
        cols = [roll180((1, 0, 0)), roll180((0, 1, 0)), roll180((0, 0, 1))]
        det = (
            cols[0][0] * (cols[1][1] * cols[2][2] - cols[1][2] * cols[2][1])
            - cols[0][1] * (cols[1][0] * cols[2][2] - cols[1][2] * cols[2][0])
            + cols[0][2] * (cols[1][0] * cols[2][1] - cols[1][1] * cols[2][0])
        )
        self.assertEqual(det, 1)
        math_test = (ROOT / 'libraries/AP_Math/tests/test_math.cpp').read_text()
        self.assertIn('TEST_ROTATION(ROTATION_ROLL_180, 1, -1, -1)', math_test)
        self.assertIn('TEST_ROTATION(ROTATION_YAW_270, 1, -1, 1)', math_test)

    def test_six_face_msp_to_frd(self):
        """WP2B-C measured BF-body Acc dominants map to AP FRD under ROLL_180."""
        # Dominant unit vectors from evidence/wp2b-c (BF Y-left Z-up)
        faces = {
            'flat_top_up': (0.0, 0.0, 1.0),
            'flat_bottom_up': (0.0, 0.0, -1.0),
            'right_side_down': (0.0, 1.0, 0.0),
            'left_side_down': (0.0, -1.0, 0.0),
            'nose_down': (-1.0, 0.0, 0.0),
            'nose_up': (1.0, 0.0, 0.0),
        }
        expected_frd = {
            'flat_top_up': (0.0, 0.0, -1.0),
            'flat_bottom_up': (0.0, 0.0, 1.0),
            'right_side_down': (0.0, -1.0, 0.0),
            'left_side_down': (0.0, 1.0, 0.0),
            'nose_down': (-1.0, 0.0, 0.0),
            'nose_up': (1.0, 0.0, 0.0),
        }

        def roll180(v):
            return (v[0], -v[1], -v[2])

        for name, bf in faces.items():
            with self.subTest(face=name):
                self.assertEqual(roll180(bf), expected_frd[name])

    def test_mpu_driver_compose_yaw270_equals_roll180(self):
        """Invensense (y,x,-z) then YAW_270 == ROLL_180(raw)."""
        def a_mpu(v):
            x, y, z = v
            return (y, x, -z)

        def yaw270(v):
            x, y, z = v
            return (y, -x, z)

        def roll180(v):
            x, y, z = v
            return (x, -y, -z)

        for r in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 2, 3), (-4, 5, -6)):
            with self.subTest(r=r):
                self.assertEqual(yaw270(a_mpu(r)), roll180(r))

    def test_usb_clock_selects_hsi48(self):
        """WP3-C: Halo USB FS must use HSI48, not HSE-derived PLL3Q."""
        for configuration in self.outputs:
            with self.subTest(configuration=configuration):
                header = (self.outputs[configuration] / 'hwdef.h').read_text()
                self.assertIn('#define STM32_USBSEL STM32_USBSEL_HSI48_CK', header)
                self.assertNotIn('#define STM32_USBSEL STM32_USBSEL_PLL3_Q_CK', header)
        for filename in ('hwdef.dat', 'hwdef-bl.dat'):
            text = (BOARD / filename).read_text()
            self.assertRegex(text, r'define\s+STM32_USBSEL\s+STM32_USBSEL_HSI48_CK')

    def test_sysclk_uses_hsi64_not_hse(self):
        """WP3-J: Halo SYSCLK must use HSI64 (OSCILLATOR_HZ 0), not HSE."""
        for configuration in self.outputs:
            with self.subTest(configuration=configuration):
                header = (self.outputs[configuration] / 'hwdef.h').read_text()
                self.assertIn('#define STM32_HSECLK 0U', header)
                self.assertNotIn('#define STM32_HSECLK 8000000U', header)
                self.assertNotIn('HAL_CUSTOM_MCU_CLOCKRATE 480000000', header)
        for filename in ('hwdef.dat', 'hwdef-bl.dat'):
            text = (BOARD / filename).read_text()
            self.assertIsNotNone(re.search(r'^OSCILLATOR_HZ\s+0\s*$', text, re.M))
            self.assertIsNone(re.search(r'^MCU_CLOCKRATE_MHZ\s+480\s*$', text, re.M))
        # Production bootloader must keep normal app jump (not DiagBL flags).
        bl = (BOARD / 'hwdef-bl.dat').read_text()
        self.assertNotIn('HAL_BOOTLOADER_NO_APP_JUMP', bl)
        self.assertNotIn('HAL_BOOTLOADER_READ_ONLY', bl)
        self.assertNotIn('HAL_BOOTLOADER_DIAG_LED', bl)

    def test_peripheral_config_unchanged_by_imu_rotation(self):
        """Motors/DMA/UART/SPI/baro pins must not change with IMU rotation fix."""
        header = (self.outputs['app'] / 'hwdef.h').read_text()
        hwdef = (BOARD / 'hwdef.dat').read_text()
        self.assertIn('HAL_BARO_PROBE_EXT_DEFAULT', header)
        self.assertRegex(hwdef, r'define\s+STM32_USBSEL\s+STM32_USBSEL_HSI48_CK')
        self.assertIn('STM32_TIM_TIM3_UP_DMA_STREAM', header)
        self.assertRegex(hwdef, r'PC6\s+TIM3_CH1\s+TIM3')
        self.assertRegex(hwdef, r'PC7\s+TIM3_CH2\s+TIM3')
        self.assertRegex(hwdef, r'PC8\s+TIM3_CH3\s+TIM3')
        self.assertRegex(hwdef, r'PC9\s+TIM3_CH4\s+TIM3')
        self.assertRegex(hwdef, r'PB6\s+USART1_TX\s+USART1')
        self.assertRegex(hwdef, r'PB7\s+USART1_RX\s+USART1')
        self.assertRegex(hwdef, r'PC12\s+UART5_TX\s+UART5')
        self.assertRegex(hwdef, r'PD2\s+UART5_RX\s+UART5')
        self.assertRegex(hwdef, r'PA5\s+SPI1_SCK\s+SPI1')
        self.assertRegex(hwdef, r'PC6\s+TIM3_CH1\s+TIM3\s+PWM\(1\).*BIDIR')
        self.assertRegex(hwdef, r'PC8\s+TIM3_CH3\s+TIM3\s+PWM\(3\).*BIDIR')
        self.assertIn('HAL_WITH_BIDIR_DSHOT', header)
        self.assertIn('HAL_BARO_PROBE_EXT_DEFAULT 1030', hwdef)
        self.assertRegex(hwdef, r'define\s+HAL_BARO_ALLOW_INIT_NO_BARO\s+1')
        self.assertIn('HAL_BARO_ALLOW_INIT_NO_BARO', header)
        inv = (ROOT / 'libraries/AP_InertialSensor/AP_InertialSensor_Invensense.cpp').read_text()
        self.assertIn('int16_val(data, 1)', inv)
        self.assertIn('int16_val(data, 0)', inv)
        self.assertIn('-int16_val(data, 2)', inv)


if __name__ == '__main__':
    unittest.main()
