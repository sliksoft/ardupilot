"""Native regression probes using the diagnostic bootloader's actual function bodies.

AP_FLAKE8_CLEAN
"""

import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def function_text(source: str, signature: str) -> str:
    start = source.index(signature)
    opening = source.index('{', start)
    end = source.index('\n}', opening) + 2
    return source[start:end]


def function_text_including(source: str, signature: str, prefix: str) -> str:
    start = source.index(signature)
    prefix_at = source.rfind(prefix, 0, start)
    if prefix_at < 0:
        prefix_at = start
    opening = source.index('{', start)
    end = source.index('\n}', opening) + 2
    return source[prefix_at:end]


class HaloDiagSafetyTest(unittest.TestCase):
    def compile_and_run(self, program: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'probe.cpp'
            binary = Path(directory) / 'probe'
            source.write_text(program)
            built = subprocess.run(
                ['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-Werror',
                 str(source), '-o', str(binary)], capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_read_only_protocol_rejects_every_other_opcode(self) -> None:
        source = (ROOT / 'Tools/AP_Bootloader/bl_protocol.cpp').read_text()
        constants = '\n'.join(re.findall(r'^#define (?:PROTO_\w+|BL_PROTOCOL_VERSION)\s+[^\n]+', source, re.M))
        functions = '\n'.join(function_text(source, signature) for signature in (
            'static void\nsync_response(void)', 'static void\ninvalid_response(void)',
            'inline static bool\nwait_for_eoc(unsigned timeout)',
            'static void\ncout_word(uint32_t val)', 'void\nbootloader(unsigned timeout)'))
        self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#include <deque>
#include <vector>
#define HAL_BOOTLOADER_READ_ONLY 1
struct EndOfInput {};
static std::deque<int> input;
static std::vector<uint8_t> output;
static struct { uint32_t board_type, board_rev, fw_size, extf_size; }
    board_info = {1414, 0, 1703936, 0};
int16_t cin(unsigned) {
    if (input.empty()) { throw EndOfInput{}; }
    int value = input.front(); input.pop_front(); return value;
}
void cout(const uint8_t *data, uint32_t length) {
    output.insert(output.end(), data, data + length);
}
uint32_t get_mcu_id() { return 0x450; }
void lock_bl_port() {}
''' + constants + '\n' + functions + r'''
static void run(std::deque<int> bytes) {
    input = bytes; output.clear();
    try { bootloader(0); assert(false); } catch (const EndOfInput &) {}
}
int main() {
    for (int opcode = 0; opcode < 256; opcode++) {
        if (opcode == PROTO_GET_SYNC || opcode == PROTO_GET_DEVICE || opcode == PROTO_GET_CHIP) { continue; }
        run({opcode});
        assert((output == std::vector<uint8_t>{PROTO_INSYNC, PROTO_INVALID}));
    }
    run({PROTO_GET_SYNC, PROTO_EOC});
    assert((output == std::vector<uint8_t>{PROTO_INSYNC, PROTO_OK}));
    run({PROTO_GET_SYNC, 0});
    assert((output == std::vector<uint8_t>{PROTO_INSYNC, PROTO_INVALID}));
    const uint32_t values[] = {5, 1414, 0, 1703936, 0, 0};
    for (int arg = 0; arg < 256; arg++) {
        run({PROTO_GET_DEVICE, arg, PROTO_EOC});
        if (arg >= 1 && arg <= 6 && arg != PROTO_DEVICE_VEC_AREA) {
            uint32_t value = values[arg - 1];
            assert(output.size() == 6);
            for (unsigned i = 0; i < 4; i++) { assert(output[i] == ((value >> (8 * i)) & 255)); }
            assert(output[4] == PROTO_INSYNC && output[5] == PROTO_OK);
        } else {
            assert((output == std::vector<uint8_t>{PROTO_INSYNC, PROTO_INVALID}));
        }
    }
    run({PROTO_GET_DEVICE, -1});
    assert((output == std::vector<uint8_t>{PROTO_INSYNC, PROTO_INVALID}));
    run({PROTO_GET_CHIP, PROTO_EOC});
    assert((output == std::vector<uint8_t>{0x50, 4, 0, 0, PROTO_INSYNC, PROTO_OK}));
    run({PROTO_CHIP_ERASE, PROTO_PROG_MULTI, PROTO_BOOT, PROTO_GET_SYNC, PROTO_EOC});
    assert((output == std::vector<uint8_t>{0x12, 0x13, 0x12, 0x13, 0x12, 0x13, 0x12, 0x10}));
}
''')

    def test_strlen_survives_gcc_loop_distribute_patterns(self) -> None:
        support = (ROOT / 'Tools/AP_Bootloader/support.cpp').read_text()
        self.assertIn('no-tree-loop-distribute-patterns', support)
        strlen_src = function_text_including(
            support, 'size_t strlen(const char *s1)', '#if defined(__GNUC__)')
        self.assertNotIn('while (*s1++)', strlen_src)
        self.compile_and_run(r'''
#include <cassert>
#include <cstddef>
''' + strlen_src + r'''
int main() {
    assert(strlen("") == 0);
    assert(strlen("A") == 1);
    assert(strlen("ArduPilot") == 9);
    assert(strlen("%BOARD%") == 7);
    const char *product = "HDZeroHalo";
    assert(strlen(product) == 10);
    return 0;
}
''')

    def test_setup_usb_strings_completes_with_bootloader_strlen(self) -> None:
        support = (ROOT / 'Tools/AP_Bootloader/support.cpp').read_text()
        usb = (ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/common/usbcfg.c').read_text()
        strlen_src = function_text_including(
            support, 'size_t strlen(const char *s1)', '#if defined(__GNUC__)')
        setup_one = function_text(usb, 'static void setup_usb_string(USBDescriptor *desc, const char *str, uint8_t *b)')
        setup_all = function_text(usb, 'void setup_usb_strings(void)')
        self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#include <cstddef>
#define USB_DESC_MAX_STRLEN 100
#define USB_DESCRIPTOR_STRING 3
#define USB_DESC_BYTE(x) ((uint8_t)(x))
#define HAL_USB_STRING_MANUFACTURER "ArduPilot"
#define HAL_USB_STRING_PRODUCT "HDZeroHalo"
#define HAL_USB_STRING_SERIAL "1234"
struct USBDescriptor { uint8_t ud_size; const uint8_t *ud_string; };
static USBDescriptor vcom_strings[4];
static uint8_t vcom_buffers[3][2+2*USB_DESC_MAX_STRLEN];
void string_substitute(const char *str, char *str2) {
    while (*str) {
        *str2++ = *str++;
    }
    *str2 = 0;
}
''' + strlen_src + '\n' + setup_one + '\n' + setup_all + r'''
int main() {
    setup_usb_strings();
    assert(vcom_strings[1].ud_size == 2 + 2 * 9);
    assert(vcom_strings[2].ud_size == 2 + 2 * 10);
    assert(vcom_strings[3].ud_size == 2 + 2 * 4);
    assert(vcom_strings[1].ud_string[0] == 20);
    assert(vcom_strings[1].ud_string[1] == USB_DESCRIPTOR_STRING);
    assert(vcom_strings[1].ud_string[2] == 'A');
    return 0;
}
''')

    def test_reset_flag_led_priority(self) -> None:
        board = (ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/common/board.c').read_text()
        pulses = function_text(board, 'static unsigned halo_diag_reset_pulses(uint32_t rsr)')
        self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#define RCC_RSR_BORRSTF   (1U << 21)
#define RCC_RSR_PINRSTF   (1U << 22)
#define RCC_RSR_PORRSTF   (1U << 23)
#define RCC_RSR_SFTRSTF   (1U << 24)
#define RCC_RSR_IWDG1RSTF (1U << 26)
#define RCC_RSR_WWDG1RSTF (1U << 28)
#define RCC_RSR_LPWRRSTF  (1U << 30)
''' + pulses + r'''
int main() {
    const uint32_t power_on = RCC_RSR_PORRSTF | RCC_RSR_PINRSTF | RCC_RSR_BORRSTF;
    assert(halo_diag_reset_pulses(power_on) == 1);
    assert(halo_diag_reset_pulses(RCC_RSR_PINRSTF) == 1);
    assert(halo_diag_reset_pulses(RCC_RSR_BORRSTF) == 2);
    assert(halo_diag_reset_pulses(RCC_RSR_IWDG1RSTF | RCC_RSR_PINRSTF) == 3);
    assert(halo_diag_reset_pulses(RCC_RSR_WWDG1RSTF | RCC_RSR_PINRSTF) == 4);
    assert(halo_diag_reset_pulses(RCC_RSR_SFTRSTF | RCC_RSR_PINRSTF) == 5);
    assert(halo_diag_reset_pulses(RCC_RSR_LPWRRSTF) == 6);
    assert(halo_diag_reset_pulses(0) == 6);
    assert(halo_diag_reset_pulses(RCC_RSR_IWDG1RSTF | RCC_RSR_SFTRSTF) == 3);
    return 0;
}
''')

    def test_reset_snapshot_and_rmvf_across_successive_resets(self) -> None:
        common = ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/common'
        board = (common / 'board.c').read_text()
        watchdog = (common / 'watchdog.c').read_text()
        early = board[board.index('void __early_init(void)'):board.index('void __late_init(void)')]
        self.assertLess(early.index('halo_diag_capture_reset_flags();'), early.index('stm32_gpio_init();'))
        self.assertIn('section(".ram0.halo_reset_flags")', board)
        show = function_text(board, 'static void halo_diag_show_reset_cause(void)')
        self.assertNotIn('RCC->RSR', show)
        capture = function_text(board, 'static void halo_diag_capture_reset_flags(void)')
        getter = function_text(board, 'uint32_t halo_diag_get_reset_flags(void)')
        pulses = function_text(board, 'static unsigned halo_diag_reset_pulses(uint32_t rsr)')
        save = function_text(watchdog, 'void stm32_watchdog_save_reason(void)')
        self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#include <vector>
#define STM32H7 1
#define HAL_BOOTLOADER_DIAG_LED 1
#define RCC_RSR_RMVF      (1U << 16)
#define RCC_RSR_BORRSTF   (1U << 21)
#define RCC_RSR_PINRSTF   (1U << 22)
#define RCC_RSR_PORRSTF   (1U << 23)
#define RCC_RSR_SFTRSTF   (1U << 24)
#define RCC_RSR_IWDG1RSTF (1U << 26)
#define RCC_RSR_WWDG1RSTF (1U << 28)
#define RCC_RSR_LPWRRSTF  (1U << 30)
static volatile uint32_t halo_diag_reset_flags;
static uint32_t reset_reason, expected_snapshot;
static unsigned shown_pulses, reads;
static std::vector<uint32_t> writes;
struct Register {
    uint32_t flags = 0;
    bool clearing = false;
    operator uint32_t() {
        assert(writes.empty());
        reads++;
        return flags;
    }
    void operator=(uint32_t value) {
        assert(halo_diag_reset_flags == expected_snapshot);
        writes.push_back(value);
        if (value == RCC_RSR_RMVF) {
            flags = 0;
            clearing = true;
        } else {
            assert(value == 0 && clearing);
            clearing = false;
        }
    }
    void reset(uint32_t cause) {
        assert(!clearing);
        flags |= cause;
        expected_snapshot = flags;
        writes.clear();
        reads = 0;
    }
};
static struct { Register RSR; } rcc;
#define RCC (&rcc)
void halo_diag_led_long_pulses(unsigned count) { shown_pulses = count; }
''' + capture + '\n' + getter + '\n' + pulses + '\n' + show + '\n' + save + r'''
static void boot(uint32_t cause, unsigned expected_pulses) {
    rcc.RSR.reset(cause);
    halo_diag_capture_reset_flags();
    assert((writes == std::vector<uint32_t>{RCC_RSR_RMVF, 0}));
    assert(reads == 1 && rcc.RSR.flags == 0 && !rcc.RSR.clearing);
    reset_reason = 0; // CRT0 clears BSS; .ram0 snapshot is retained.
    stm32_watchdog_save_reason();
    assert(reset_reason == expected_snapshot);
    halo_diag_show_reset_cause();
    assert(shown_pulses == expected_pulses && reads == 1);
    assert(halo_diag_get_reset_flags() == expected_snapshot);
}
int main() {
    boot(RCC_RSR_PORRSTF | RCC_RSR_PINRSTF | RCC_RSR_BORRSTF, 1);
    boot(RCC_RSR_BORRSTF | RCC_RSR_PINRSTF, 2);
    boot(RCC_RSR_IWDG1RSTF | RCC_RSR_PINRSTF, 3);
    boot(RCC_RSR_SFTRSTF | RCC_RSR_PINRSTF, 5);
    const uint32_t causes[] = {
        RCC_RSR_PINRSTF, RCC_RSR_BORRSTF, RCC_RSR_PORRSTF | RCC_RSR_BORRSTF,
        RCC_RSR_IWDG1RSTF, RCC_RSR_WWDG1RSTF, RCC_RSR_SFTRSTF,
        RCC_RSR_LPWRRSTF, 0, RCC_RSR_IWDG1RSTF | RCC_RSR_SFTRSTF,
        RCC_RSR_WWDG1RSTF | RCC_RSR_BORRSTF,
        RCC_RSR_SFTRSTF | RCC_RSR_PORRSTF, RCC_RSR_LPWRRSTF | RCC_RSR_PINRSTF
    };
    const unsigned expected[] = {1, 2, 1, 3, 4, 5, 6, 6, 3, 4, 5, 6};
    for (unsigned first = 0; first < 12; first++) {
        for (unsigned second = 0; second < 12; second++) {
            boot(causes[first] | (1U << 17) | (1U << 19) | (1U << 20), expected[first]);
            boot(causes[second], expected[second]);
        }
    }
}
''')

    def test_production_reset_reason_still_uses_hardware(self) -> None:
        watchdog = (ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/common/watchdog.c').read_text()
        save = function_text(watchdog, 'void stm32_watchdog_save_reason(void)')
        self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#define STM32H7 1
#define HAL_BOOTLOADER_DIAG_LED 0
static uint32_t reset_reason;
static uint32_t hardware_reason = 0x04c00000;
#define WDG_RESET_STATUS hardware_reason
''' + save + r'''
int main() {
    stm32_watchdog_save_reason();
    assert(reset_reason == 0x04c00000);
    hardware_reason = 0;
    stm32_watchdog_save_reason();
    assert(reset_reason == 0x04c00000);
}
''')

    def test_generic_led_calls_preserve_diagnostic_marker_and_production_leds(self) -> None:
        support = (ROOT / 'Tools/AP_Bootloader/support.cpp').read_text()
        board = (ROOT / 'libraries/AP_HAL_ChibiOS/hwdef/common/board.c').read_text()
        functions = '\n'.join(function_text(support, signature) for signature in (
            'void led_on(unsigned led)', 'void led_off(unsigned led)', 'void led_toggle(unsigned led)'))
        markers = '\n'.join(function_text(board, signature) for signature in (
            'static void halo_diag_led_raw(int on)', 'static void halo_diag_delay(void)',
            'void halo_diag_led_marker(unsigned stage)'))
        for diagnostic in (0, 1):
            with self.subTest(diagnostic=diagnostic):
                self.compile_and_run(r'''
#include <cassert>
#include <cstdint>
#define STM32_HAS_GPIOE 1
#define HAL_LED_ON 0
#define HAL_GPIO_PIN_LED_BOOTLOADER 2
#define HAL_GPIO_PIN_LED_ACTIVITY 1
#define LED_BOOTLOADER 2
#define LED_ACTIVITY 1
#define __NOP() ((void)0)
static unsigned writes, marker_on_writes;
static uint32_t odr;
struct Register {
    void operator=(uint32_t value) {
        odr = (odr | (value & 0xffff)) & ~(value >> 16);
        if (value == (1U << 18)) { marker_on_writes++; }
    }
};
static struct { struct { Register W; } BSRR; } gpioe;
#define GPIOE (&gpioe)
void palWriteLine(unsigned, unsigned value) { writes++; odr = value ? 4 : 0; }
void palToggleLine(unsigned) { writes++; odr ^= 4; }
''' + f'\n#define HAL_BOOTLOADER_DIAG_LED {diagnostic}\n' + functions + '\n' + markers + r'''
int main() {
    for (unsigned stage = 1; stage <= 3; stage++) {
        marker_on_writes = 0;
        halo_diag_led_marker(stage);
        assert(marker_on_writes == stage && (odr & 4) != 0);
    }
    halo_diag_led_marker(4);
    assert((odr & 4) == 0);
    for (unsigned i = 0; i < 1000; i++) {
        led_on(LED_BOOTLOADER); led_off(LED_BOOTLOADER); led_toggle(LED_BOOTLOADER);
        led_on(LED_ACTIVITY); led_off(LED_ACTIVITY); led_toggle(LED_ACTIVITY);
    }
#if HAL_BOOTLOADER_DIAG_LED
    assert(writes == 0 && (odr & 4) == 0);
#else
    assert(writes == 6000);
    led_off(LED_BOOTLOADER); assert((odr & 4) != 0);
    led_on(LED_BOOTLOADER); assert((odr & 4) == 0);
    led_toggle(LED_BOOTLOADER); assert((odr & 4) != 0);
#endif
}
''')


if __name__ == '__main__':
    unittest.main()
