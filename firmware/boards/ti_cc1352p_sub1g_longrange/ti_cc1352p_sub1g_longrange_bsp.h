#ifndef TI_CC1352P_SUB1G_LONGRANGE_BSP_H
#define TI_CC1352P_SUB1G_LONGRANGE_BSP_H

/**
 * @file ti_cc1352p_sub1g_longrange_bsp.h
 * @brief Board Support Package for Texas Instruments CC1352P Sub-1GHz 868/915MHz Long Range Node
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t cpu_frequency_hz;
    uint32_t flash_size_bytes;
    uint32_t ram_size_bytes;
    bool is_radio_initialized;
    uint32_t uptime_seconds;
    float core_temperature_c;
} ti_cc1352p_sub1g_longrange_bsp_info_t;

int ti_cc1352p_sub1g_longrange_bsp_init(void);
int ti_cc1352p_sub1g_longrange_bsp_get_info(ti_cc1352p_sub1g_longrange_bsp_info_t *info);
int ti_cc1352p_sub1g_longrange_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int ti_cc1352p_sub1g_longrange_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // TI_CC1352P_SUB1G_LONGRANGE_BSP_H
