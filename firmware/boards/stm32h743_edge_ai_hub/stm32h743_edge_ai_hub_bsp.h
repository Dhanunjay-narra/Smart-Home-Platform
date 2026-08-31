#ifndef STM32H743_EDGE_AI_HUB_BSP_H
#define STM32H743_EDGE_AI_HUB_BSP_H

/**
 * @file stm32h743_edge_ai_hub_bsp.h
 * @brief Board Support Package for STMicroelectronics STM32H743IIT6 ARM Cortex-M7 High Performance Audio Hub
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
} stm32h743_edge_ai_hub_bsp_info_t;

int stm32h743_edge_ai_hub_bsp_init(void);
int stm32h743_edge_ai_hub_bsp_get_info(stm32h743_edge_ai_hub_bsp_info_t *info);
int stm32h743_edge_ai_hub_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int stm32h743_edge_ai_hub_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // STM32H743_EDGE_AI_HUB_BSP_H
