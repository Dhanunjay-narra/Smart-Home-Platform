#ifndef EFM32_GECKO_ENVIRONMENTAL_BSP_H
#define EFM32_GECKO_ENVIRONMENTAL_BSP_H

/**
 * @file efm32_gecko_environmental_bsp.h
 * @brief Board Support Package for Silicon Labs EFM32GG11 Giant Gecko Environmental Weather Node
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
} efm32_gecko_environmental_bsp_info_t;

int efm32_gecko_environmental_bsp_init(void);
int efm32_gecko_environmental_bsp_get_info(efm32_gecko_environmental_bsp_info_t *info);
int efm32_gecko_environmental_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int efm32_gecko_environmental_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // EFM32_GECKO_ENVIRONMENTAL_BSP_H
