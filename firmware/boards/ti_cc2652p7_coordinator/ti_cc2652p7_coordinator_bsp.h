#ifndef TI_CC2652P7_COORDINATOR_BSP_H
#define TI_CC2652P7_COORDINATOR_BSP_H

/**
 * @file ti_cc2652p7_coordinator_bsp.h
 * @brief Board Support Package for Texas Instruments CC2652P7 High-Power Zigbee 3.0 Coordinator
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
} ti_cc2652p7_coordinator_bsp_info_t;

int ti_cc2652p7_coordinator_bsp_init(void);
int ti_cc2652p7_coordinator_bsp_get_info(ti_cc2652p7_coordinator_bsp_info_t *info);
int ti_cc2652p7_coordinator_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int ti_cc2652p7_coordinator_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // TI_CC2652P7_COORDINATOR_BSP_H
