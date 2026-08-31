#ifndef RP2040_PICO_W_NODE_BSP_H
#define RP2040_PICO_W_NODE_BSP_H

/**
 * @file rp2040_pico_w_node_bsp.h
 * @brief Board Support Package for Raspberry Pi Pico W Dual Cortex-M0+ Wireless Sensor Node
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
} rp2040_pico_w_node_bsp_info_t;

int rp2040_pico_w_node_bsp_init(void);
int rp2040_pico_w_node_bsp_get_info(rp2040_pico_w_node_bsp_info_t *info);
int rp2040_pico_w_node_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int rp2040_pico_w_node_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // RP2040_PICO_W_NODE_BSP_H
