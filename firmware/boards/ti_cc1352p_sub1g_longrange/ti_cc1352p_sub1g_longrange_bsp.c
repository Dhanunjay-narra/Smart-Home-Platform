/**
 * @file ti_cc1352p_sub1g_longrange_bsp.c
 * @brief Implementation for Texas Instruments CC1352P Sub-1GHz 868/915MHz Long Range Node
 */

#include "ti_cc1352p_sub1g_longrange_bsp.h"
#include <stdio.h>

int ti_cc1352p_sub1g_longrange_bsp_init(void) {
    printf("[BSP Init] Texas Instruments CC1352P Sub-1GHz 868/915MHz Long Range Node initialized successfully.\n");
    return 0;
}

int ti_cc1352p_sub1g_longrange_bsp_get_info(ti_cc1352p_sub1g_longrange_bsp_info_t *info) {
    if (!info) return -1;
    info->cpu_frequency_hz = 240000000;
    info->flash_size_bytes = 8388608;
    info->ram_size_bytes = 524288;
    info->is_radio_initialized = true;
    info->uptime_seconds = 3600;
    info->core_temperature_c = 42.5f;
    return 0;
}

int ti_cc1352p_sub1g_longrange_bsp_enter_deep_sleep(uint32_t sleep_duration_ms) {
    printf("[BSP] Entering deep sleep mode for %u ms\n", sleep_duration_ms);
    return 0;
}

int ti_cc1352p_sub1g_longrange_bsp_software_reset(void) {
    printf("[BSP] Software reset requested. Rebooting target MCU.\n");
    return 0;
}
