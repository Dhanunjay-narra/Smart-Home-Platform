#ifndef DRIVER_VL53L0X_H
#define DRIVER_VL53L0X_H

/**
 * @file driver_vl53l0x.h
 * @brief STMicroelectronics Time-of-Flight (ToF) Distance Ranging Sensor
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_VL53L0X_STATUS_OK = 0,
    DRIVER_VL53L0X_STATUS_ERROR = -1,
    DRIVER_VL53L0X_STATUS_BUSY = -2,
    DRIVER_VL53L0X_STATUS_TIMEOUT = -3
} driver_vl53l0x_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_vl53l0x_handle_t;

driver_vl53l0x_status_t driver_vl53l0x_init(driver_vl53l0x_handle_t *handle);
driver_vl53l0x_status_t driver_vl53l0x_read(driver_vl53l0x_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_vl53l0x_status_t driver_vl53l0x_write(driver_vl53l0x_handle_t *handle, const uint8_t *data, uint16_t len);
driver_vl53l0x_status_t driver_vl53l0x_self_test(driver_vl53l0x_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_VL53L0X_H
