#ifndef KW41Z_THREAD_BORDER_ROUTER_BSP_H
#define KW41Z_THREAD_BORDER_ROUTER_BSP_H

/**
 * @file kw41z_thread_border_router_bsp.h
 * @brief Board Support Package for NXP KW41Z Multi-Protocol BLE & Thread Border Router
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
} kw41z_thread_border_router_bsp_info_t;

int kw41z_thread_border_router_bsp_init(void);
int kw41z_thread_border_router_bsp_get_info(kw41z_thread_border_router_bsp_info_t *info);
int kw41z_thread_border_router_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int kw41z_thread_border_router_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // KW41Z_THREAD_BORDER_ROUTER_BSP_H
