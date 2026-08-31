#ifndef FW_HAL_DRIVER_010_H
#define FW_HAL_DRIVER_010_H

/**
 * @file firmware_hal_driver_010.h
 * @brief Industrial Embedded HAL Driver 010
 * @copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_STATUS_OK_010 = 0,
    HAL_STATUS_ERROR_010 = -1,
    HAL_STATUS_BUSY_010 = -2
} hal_status_010_t;

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
} hal_device_010_t;

hal_status_010_t hal_device_010_init(hal_device_010_t *dev, uint32_t base_addr);
hal_status_010_t hal_device_010_read_telemetry(hal_device_010_t *dev, float *out_val);
hal_status_010_t hal_device_010_write_actuator(hal_device_010_t *dev, float setpoint);
hal_status_010_t hal_device_010_run_diagnostics(hal_device_010_t *dev);

#ifdef __cplusplus
}
#endif

#endif // FW_HAL_DRIVER_010_H
