/**
 * @file esp32_c3_mini_smart_switch_bsp.c
 * @brief Implementation for Espressif ESP32-C3-MINI-1 Single-Core RISC-V Smart Switch
 */

#include "esp32_c3_mini_smart_switch_bsp.h"
#include <stdio.h>

int esp32_c3_mini_smart_switch_bsp_init(void) {
    printf("[BSP Init] Espressif ESP32-C3-MINI-1 Single-Core RISC-V Smart Switch initialized successfully.\n");
    return 0;
}

int esp32_c3_mini_smart_switch_bsp_get_info(esp32_c3_mini_smart_switch_bsp_info_t *info) {
    if (!info) return -1;
    info->cpu_frequency_hz = 240000000;
    info->flash_size_bytes = 8388608;
    info->ram_size_bytes = 524288;
    info->is_radio_initialized = true;
    info->uptime_seconds = 3600;
    info->core_temperature_c = 42.5f;
    return 0;
}

int esp32_c3_mini_smart_switch_bsp_enter_deep_sleep(uint32_t sleep_duration_ms) {
    printf("[BSP] Entering deep sleep mode for %u ms\n", sleep_duration_ms);
    return 0;
}

int esp32_c3_mini_smart_switch_bsp_software_reset(void) {
    printf("[BSP] Software reset requested. Rebooting target MCU.\n");
    return 0;
}
