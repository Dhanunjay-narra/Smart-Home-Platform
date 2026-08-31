#ifndef MAX32660_PIEZO_BUZZER_NODE_BSP_H
#define MAX32660_PIEZO_BUZZER_NODE_BSP_H

/**
 * @file max32660_piezo_buzzer_node_bsp.h
 * @brief Board Support Package for Analog Devices MAX32660 Ultra-Low-Power Acoustic Siren Node
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
} max32660_piezo_buzzer_node_bsp_info_t;

int max32660_piezo_buzzer_node_bsp_init(void);
int max32660_piezo_buzzer_node_bsp_get_info(max32660_piezo_buzzer_node_bsp_info_t *info);
int max32660_piezo_buzzer_node_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int max32660_piezo_buzzer_node_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // MAX32660_PIEZO_BUZZER_NODE_BSP_H
