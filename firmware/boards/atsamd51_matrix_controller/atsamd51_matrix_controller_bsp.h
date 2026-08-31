#ifndef ATSAMD51_MATRIX_CONTROLLER_BSP_H
#define ATSAMD51_MATRIX_CONTROLLER_BSP_H

/**
 * @file atsamd51_matrix_controller_bsp.h
 * @brief Board Support Package for Microchip ATSAMD51J19A 120MHz Cortex-M4F RGB LED Controller
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
} atsamd51_matrix_controller_bsp_info_t;

int atsamd51_matrix_controller_bsp_init(void);
int atsamd51_matrix_controller_bsp_get_info(atsamd51_matrix_controller_bsp_info_t *info);
int atsamd51_matrix_controller_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int atsamd51_matrix_controller_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // ATSAMD51_MATRIX_CONTROLLER_BSP_H
