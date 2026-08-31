#ifndef STM32L476_ENERGY_HARVESTER_BSP_H
#define STM32L476_ENERGY_HARVESTER_BSP_H

/**
 * @file stm32l476_energy_harvester_bsp.h
 * @brief Board Support Package for STMicroelectronics STM32L476RG Ultra-Low-Power Solar Harvester
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
} stm32l476_energy_harvester_bsp_info_t;

int stm32l476_energy_harvester_bsp_init(void);
int stm32l476_energy_harvester_bsp_get_info(stm32l476_energy_harvester_bsp_info_t *info);
int stm32l476_energy_harvester_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int stm32l476_energy_harvester_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // STM32L476_ENERGY_HARVESTER_BSP_H
