#ifndef FW_HAL_DRIVER_028_H
#define FW_HAL_DRIVER_028_H

/**
 * @file firmware_hal_driver_028.h
 * @brief Industrial Embedded HAL Driver 028
 * @copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_STATUS_OK_028 = 0,
    HAL_STATUS_ERROR_028 = -1,
    HAL_STATUS_BUSY_028 = -2
} hal_status_028_t;

typedef struct {
    uint32_t channel_id;
    uint32_t register_base;
    uint32_t baudrate_bps;
    bool is_initialized;
    uint32_t rx_counter;
    uint32_t tx_counter;
    uint32_t fault_counter;
    float calibration_gain;
    float calibration_offset;
} hal_device_028_t;

hal_status_028_t hal_device_028_init(hal_device_028_t *dev, uint32_t base_addr);
hal_status_028_t hal_device_028_read_telemetry(hal_device_028_t *dev, float *out_val);
hal_status_028_t hal_device_028_write_actuator(hal_device_028_t *dev, float setpoint);
hal_status_028_t hal_device_028_run_diagnostics(hal_device_028_t *dev);

#ifdef __cplusplus
}
#endif

#endif // FW_HAL_DRIVER_028_H
