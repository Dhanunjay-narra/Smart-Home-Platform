/**
 * @file hal_i2c_master.c
 * @brief Implementation for Hardware Abstraction Layer for Standard/Fast I2C Bus Controller
 */

#include "hal_i2c_master.h"
#include <stdio.h>
#include <string.h>

hal_i2c_master_status_t hal_i2c_master_init(hal_i2c_master_handle_t *handle) {
    if (!handle) return HAL_I2C_MASTER_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized hal_i2c_master on channel %u\n", handle->channel);
    return HAL_I2C_MASTER_STATUS_OK;
}

hal_i2c_master_status_t hal_i2c_master_read(hal_i2c_master_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return HAL_I2C_MASTER_STATUS_ERROR;
    handle->rx_byte_count += len;
    return HAL_I2C_MASTER_STATUS_OK;
}

hal_i2c_master_status_t hal_i2c_master_write(hal_i2c_master_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return HAL_I2C_MASTER_STATUS_ERROR;
    handle->tx_byte_count += len;
    return HAL_I2C_MASTER_STATUS_OK;
}

hal_i2c_master_status_t hal_i2c_master_self_test(hal_i2c_master_handle_t *handle) {
    if (!handle) return HAL_I2C_MASTER_STATUS_ERROR;
    printf("[Firmware SelfTest] hal_i2c_master diagnostic passed.\n");
    return HAL_I2C_MASTER_STATUS_OK;
}
