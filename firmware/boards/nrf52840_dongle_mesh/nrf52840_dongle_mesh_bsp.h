#ifndef NRF52840_DONGLE_MESH_BSP_H
#define NRF52840_DONGLE_MESH_BSP_H

/**
 * @file nrf52840_dongle_mesh_bsp.h
 * @brief Board Support Package for Nordic Semiconductor nRF52840 USB Dongle Bluetooth Mesh Coordinator
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
} nrf52840_dongle_mesh_bsp_info_t;

int nrf52840_dongle_mesh_bsp_init(void);
int nrf52840_dongle_mesh_bsp_get_info(nrf52840_dongle_mesh_bsp_info_t *info);
int nrf52840_dongle_mesh_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int nrf52840_dongle_mesh_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // NRF52840_DONGLE_MESH_BSP_H
