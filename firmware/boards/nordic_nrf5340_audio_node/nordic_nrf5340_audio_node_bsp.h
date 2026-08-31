#ifndef NORDIC_NRF5340_AUDIO_NODE_BSP_H
#define NORDIC_NRF5340_AUDIO_NODE_BSP_H

/**
 * @file nordic_nrf5340_audio_node_bsp.h
 * @brief Board Support Package for Nordic nRF5340 Dual-Core Bluetooth LE Audio Streaming Endpoint
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
} nordic_nrf5340_audio_node_bsp_info_t;

int nordic_nrf5340_audio_node_bsp_init(void);
int nordic_nrf5340_audio_node_bsp_get_info(nordic_nrf5340_audio_node_bsp_info_t *info);
int nordic_nrf5340_audio_node_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int nordic_nrf5340_audio_node_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // NORDIC_NRF5340_AUDIO_NODE_BSP_H
