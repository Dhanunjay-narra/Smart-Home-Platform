#ifndef STM32G071_LOW_POWER_METER_BSP_H
#define STM32G071_LOW_POWER_METER_BSP_H

/**
 * @file stm32g071_low_power_meter_bsp.h
 * @brief Board Support Package for STMicroelectronics STM32G071RB Value-Line Energy Meter
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
} stm32g071_low_power_meter_bsp_info_t;

int stm32g071_low_power_meter_bsp_init(void);
int stm32g071_low_power_meter_bsp_get_info(stm32g071_low_power_meter_bsp_info_t *info);
int stm32g071_low_power_meter_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int stm32g071_low_power_meter_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // STM32G071_LOW_POWER_METER_BSP_H
