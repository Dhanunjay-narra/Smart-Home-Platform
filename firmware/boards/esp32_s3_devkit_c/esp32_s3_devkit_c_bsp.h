#ifndef ESP32_S3_DEVKIT_C_BSP_H
#define ESP32_S3_DEVKIT_C_BSP_H

/**
 * @file esp32_s3_devkit_c_bsp.h
 * @brief Board Support Package for Espressif ESP32-S3-DevKitC-1 Dual-Core 240MHz Wi-Fi & BLE 5
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
} esp32_s3_devkit_c_bsp_info_t;

int esp32_s3_devkit_c_bsp_init(void);
int esp32_s3_devkit_c_bsp_get_info(esp32_s3_devkit_c_bsp_info_t *info);
int esp32_s3_devkit_c_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int esp32_s3_devkit_c_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // ESP32_S3_DEVKIT_C_BSP_H
