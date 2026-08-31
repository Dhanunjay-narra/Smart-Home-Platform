#ifndef FW_HAL_DRIVER_044_H
#define FW_HAL_DRIVER_044_H

/**
 * @file firmware_hal_driver_044.h
 * @brief Industrial Embedded HAL Driver 044
 * @copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_STATUS_OK_044 = 0,
    HAL_STATUS_ERROR_044 = -1,
    HAL_STATUS_BUSY_044 = -2
} hal_status_044_t;

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
} hal_device_044_t;

hal_status_044_t hal_device_044_init(hal_device_044_t *dev, uint32_t base_addr);
hal_status_044_t hal_device_044_read_telemetry(hal_device_044_t *dev, float *out_val);
hal_status_044_t hal_device_044_write_actuator(hal_device_044_t *dev, float setpoint);
hal_status_044_t hal_device_044_run_diagnostics(hal_device_044_t *dev);

#ifdef __cplusplus
}
#endif

#endif // FW_HAL_DRIVER_044_H
