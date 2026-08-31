#ifndef RPI_CM4_EDGE_GATEWAY_OS_BSP_H
#define RPI_CM4_EDGE_GATEWAY_OS_BSP_H

/**
 * @file rpi_cm4_edge_gateway_os_bsp.h
 * @brief Board Support Package for Raspberry Pi Compute Module 4 Quad-Core Edge Gateway Host BSP
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
} rpi_cm4_edge_gateway_os_bsp_info_t;

int rpi_cm4_edge_gateway_os_bsp_init(void);
int rpi_cm4_edge_gateway_os_bsp_get_info(rpi_cm4_edge_gateway_os_bsp_info_t *info);
int rpi_cm4_edge_gateway_os_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int rpi_cm4_edge_gateway_os_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // RPI_CM4_EDGE_GATEWAY_OS_BSP_H
