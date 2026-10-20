#pragma once

#include "hwdef.h"
#include <AP_Networking/AP_Networking_Config.h>

#ifndef AP_BOOTLOADER_FLASH_FROM_SD_ENABLED
#define AP_BOOTLOADER_FLASH_FROM_SD_ENABLED 0
#endif

#ifndef HAL_BOOTLOADER_NO_APP_JUMP
#define HAL_BOOTLOADER_NO_APP_JUMP 0
#endif

#ifndef HAL_BOOTLOADER_DIAG_LED
#define HAL_BOOTLOADER_DIAG_LED 0
#endif

#ifndef HAL_BOOTLOADER_READ_ONLY
#define HAL_BOOTLOADER_READ_ONLY 0
#endif

#if HAL_BOOTLOADER_READ_ONLY
#if !HAL_BOOTLOADER_NO_APP_JUMP || AP_FASTBOOT_ENABLED || HAL_BOOTLOADER_TIMEOUT != 0
#error "Read-only diagnostics must stay in the bootloader"
#endif
#if !defined(AP_FLASH_ECC_CHECK_ENABLED) || AP_FLASH_ECC_CHECK_ENABLED
#error "Read-only diagnostics must disable autonomous ECC recovery"
#endif
#endif

#ifndef AP_BOOTLOADER_NETWORK_ENABLED
#define AP_BOOTLOADER_NETWORK_ENABLED AP_NETWORKING_ENABLED
#endif
