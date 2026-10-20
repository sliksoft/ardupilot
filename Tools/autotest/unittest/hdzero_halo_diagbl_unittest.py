"""Offline checks of the isolated HDZero Halo diagnostic bootloader.

AP_FLAKE8_CLEAN
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOARD = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/HDZeroHaloDiagBL'
PROD = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/HDZeroHalo'
GENERATOR = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/scripts/chibios_hwdef.py'


class HaloDiagBootloaderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.directory.cleanup)
        outdir = Path(cls.directory.name) / 'bootloader'
        outdir.mkdir()
        result = subprocess.run(
            [sys.executable, str(GENERATOR), '--quiet', '--outdir', str(outdir),
             '--bootloader', str(BOARD / 'hwdef-bl.dat')],
            cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.header = (outdir / 'hwdef.h').read_text()
        cls.hwdef = (BOARD / 'hwdef-bl.dat').read_text()
        cls.prod_bl = (PROD / 'hwdef-bl.dat').read_text()

    def compile_and_run(self, program):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'probe.cpp'
            binary = Path(directory) / 'probe'
            source.write_text(program)
            result = subprocess.run(
                ['g++', '-std=c++17', '-Wall', '-Wextra', '-Werror',
                 '-I', str(Path(self.directory.name) / 'bootloader'),
                 str(source), '-o', str(binary)],
                capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return subprocess.run([str(binary)], capture_output=True, text=True)

    def test_isolated_from_production_halo(self):
        """DiagBL stays separate: production shares HSI64 but keeps app jump."""
        self.assertNotEqual(self.hwdef, self.prod_bl)
        # WP3-J: production also uses HSI64; isolation is protocol/LED/jump flags.
        self.assertRegex(self.prod_bl, r'OSCILLATOR_HZ\s+0\b')
        self.assertNotIn('HAL_BOOTLOADER_NO_APP_JUMP', self.prod_bl)
        self.assertNotIn('HAL_BOOTLOADER_READ_ONLY', self.prod_bl)
        self.assertNotIn('HAL_BOOTLOADER_DIAG_LED', self.prod_bl)
        self.assertIn('HAL_BOOTLOADER_NO_APP_JUMP', self.hwdef)
        self.assertIn('HAL_BOOTLOADER_READ_ONLY', self.hwdef)
        self.assertIn('HAL_BOOTLOADER_DIAG_LED', self.hwdef)

    def test_hsi64_system_clock_generated(self):
        self.assertIn('#define STM32_HSECLK 0U', self.header)
        self.assertRegex(self.hwdef, r'OSCILLATOR_HZ\s+0\b')
        self.assertNotIn('MCU_CLOCKRATE_MHZ 480', self.hwdef)

    def test_usb_hsi48_and_no_app_jump(self):
        program = '''
#include "hwdef.h"
static_assert(STM32_HSECLK == 0U, "HSE must be disabled");
#ifndef HAL_BOOTLOADER_NO_APP_JUMP
#error "NO_APP_JUMP missing"
#endif
#if !HAL_BOOTLOADER_NO_APP_JUMP
#error "NO_APP_JUMP must be 1"
#endif
#ifndef AP_FASTBOOT_ENABLED
#error "AP_FASTBOOT_ENABLED missing"
#endif
#if AP_FASTBOOT_ENABLED
#error "fastboot must be disabled"
#endif
#ifndef HAL_BOOTLOADER_TIMEOUT
#error "timeout missing"
#endif
#if HAL_BOOTLOADER_TIMEOUT != 0
#error "timeout must be 0"
#endif
#ifndef HAL_BOOTLOADER_DIAG_LED
#error "diag LED missing"
#endif
int main() { return 0; }
'''
        self.assertEqual(self.compile_and_run(program).returncode, 0)
        self.assertIn('#define STM32_USBSEL STM32_USBSEL_HSI48_CK', self.header)
        self.assertNotIn('#define STM32_USBSEL STM32_USBSEL_PLL3_Q_CK', self.header)

    def test_safety_outputs_inactive(self):
        program = '''
#include "hwdef.h"
static_assert((VAL_GPIOD_MODER & (3U << 24)) == (1U << 24), "PD12 must be output");
static_assert((VAL_GPIOD_ODR & (1U << 12)) == 0, "buzzer must start off");
static_assert((VAL_GPIOE_MODER & (3U << 6)) == (1U << 6), "PE3 must be output");
static_assert((VAL_GPIOE_ODR & (1U << 3)) == 0, "PE3 must start LOW");
static_assert((VAL_GPIOE_MODER & (3U << 4)) == (1U << 4), "PE2 must be output");
int main() { return 0; }
'''
        self.assertEqual(self.compile_and_run(program).returncode, 0)

    def test_no_motors_or_app_peripherals(self):
        self.assertNotIn('TIM3_CH1', self.hwdef)
        self.assertNotIn('PWM(', self.hwdef)
        self.assertNotIn('USART1', self.hwdef)
        self.assertIn('SERIAL_ORDER OTG1', self.hwdef)

    def test_flash_layout_matches_reserved_bl(self):
        self.assertRegex(self.hwdef, r'FLASH_BOOTLOADER_LOAD_KB\s+128')
        self.assertRegex(self.hwdef, r'FLASH_RESERVE_START_KB\s+0')
        self.assertIn('#define FLASH_BOOTLOADER_LOAD_KB 128', self.header)

    def test_diagnostic_disables_autonomous_ecc_recovery(self):
        program = '''
#include "hwdef.h"
#define STM32H7 1
#define CH_CFG_USE_HEAP 1
'''
        support = (ROOT / 'Tools/AP_Bootloader/support.h').read_text()
        start = support.index('#ifndef AP_FLASH_ECC_CHECK_ENABLED')
        end = support.index('#endif', start) + len('#endif')
        program += support[start:end]
        program += '''
static_assert(AP_FLASH_ECC_CHECK_ENABLED == 0, "diagnostic must not scan/erase flash");
static_assert(HAL_BOOTLOADER_READ_ONLY == 1, "diagnostic protocol must be read only");
int main() { return 0; }
'''
        self.assertEqual(self.compile_and_run(program).returncode, 0)
        self.assertNotIn('AP_FLASH_ECC_CHECK_ENABLED', self.prod_bl)
        self.assertNotIn('HAL_BOOTLOADER_READ_ONLY', self.prod_bl)

    def test_production_h7_ecc_default_is_preserved(self):
        support = (ROOT / 'Tools/AP_Bootloader/support.h').read_text()
        start = support.index('#ifndef AP_FLASH_ECC_CHECK_ENABLED')
        end = support.index('#endif', start) + len('#endif')
        program = '#define STM32H7 1\n#define CH_CFG_USE_HEAP 1\n'
        program += support[start:end]
        program += '''
#if AP_FLASH_ECC_CHECK_ENABLED
ECC_ENABLED
#else
ECC_DISABLED
#endif
'''
        result = subprocess.run(['g++', '-E', '-P', '-x', 'c++', '-'], input=program,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'ECC_ENABLED')


if __name__ == '__main__':
    unittest.main()
