#ifndef ESP32_C6_MATTER_HUB_BSP_H
#define ESP32_C6_MATTER_HUB_BSP_H

/**
 * @file esp32_c6_matter_hub_bsp.h
 * @brief Board Support Package for Espressif ESP32-C6 RISC-V 160MHz Thread & Matter Gateway
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
} esp32_c6_matter_hub_bsp_info_t;

int esp32_c6_matter_hub_bsp_init(void);
int esp32_c6_matter_hub_bsp_get_info(esp32_c6_matter_hub_bsp_info_t *info);
int esp32_c6_matter_hub_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int esp32_c6_matter_hub_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // ESP32_C6_MATTER_HUB_BSP_H
