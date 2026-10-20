# HDZeroHaloDiagBL — USB-only diagnostic bootloader

**HARDWARE_FLASH_ALLOWED = NO**

Isolated from `HDZeroHalo`. Uses the existing ChibiOS H7 `OSCILLATOR_HZ 0`
route (HSI64 → PLL, HSE off) and HSI48 USB. The image never jumps to
ArduCopter. See `Tools/HDZeroHalo/WP3_E_DIAG_BOOTLOADER.md`.

WP3-E2 disables autonomous ECC scanning/erase in this diagnostic bootloader
only. The USB protocol accepts GET_SYNC, GET_CHIP and GET_DEVICE scalar
information (arguments 1, 2, 3, 4 and 6). All other opcodes, including erase,
program, boot and boot-delay changes, return INSYNC/INVALID. Application
flash reads are not exposed. This is not an uploader target.

PE2 is controlled exclusively by the four diagnostic markers; ordinary
bootloader LED calls are inactive. Marker 4 indicates entry to the USB
configuration callback, not completed Windows enumeration. Confirm Windows
enumeration and any CDC request/response traffic separately. See
`Tools/HDZeroHalo/WP3_E2_DIAG_BOOTLOADER.md` for build and machine-code evidence.

```sh
./waf configure --board HDZeroHaloDiagBL --bootloader --out=build/wp3-e2-diag-final
./waf bootloader --out=build/wp3-e2-diag-final
```
