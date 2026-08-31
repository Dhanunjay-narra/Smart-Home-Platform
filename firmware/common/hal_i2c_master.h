#ifndef HAL_I2C_MASTER_H
#define HAL_I2C_MASTER_H

/**
 * @file hal_i2c_master.h
 * @brief Hardware Abstraction Layer for Standard/Fast I2C Bus Controller
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_I2C_MASTER_STATUS_OK = 0,
    HAL_I2C_MASTER_STATUS_ERROR = -1,
    HAL_I2C_MASTER_STATUS_BUSY = -2,
    HAL_I2C_MASTER_STATUS_TIMEOUT = -3
} hal_i2c_master_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_i2c_master_handle_t;

hal_i2c_master_status_t hal_i2c_master_init(hal_i2c_master_handle_t *handle);
hal_i2c_master_status_t hal_i2c_master_read(hal_i2c_master_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_i2c_master_status_t hal_i2c_master_write(hal_i2c_master_handle_t *handle, const uint8_t *data, uint16_t len);
hal_i2c_master_status_t hal_i2c_master_self_test(hal_i2c_master_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_I2C_MASTER_H
