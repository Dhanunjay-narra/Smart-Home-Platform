#ifndef STM32F407_CAN_GATEWAY_BSP_H
#define STM32F407_CAN_GATEWAY_BSP_H

/**
 * @file stm32f407_can_gateway_bsp.h
 * @brief Board Support Package for STMicroelectronics STM32F407VGT6 ARM Cortex-M4 Industrial Hub
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
} stm32f407_can_gateway_bsp_info_t;

int stm32f407_can_gateway_bsp_init(void);
int stm32f407_can_gateway_bsp_get_info(stm32f407_can_gateway_bsp_info_t *info);
int stm32f407_can_gateway_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int stm32f407_can_gateway_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // STM32F407_CAN_GATEWAY_BSP_H
