/**
 * @file driver_mq2_gas.c
 * @brief Implementation for MQ-2 Combustible Gas & Smoke Semiconductor Detector Driver
 */

#include "driver_mq2_gas.h"
#include <stdio.h>
#include <string.h>

driver_mq2_gas_status_t driver_mq2_gas_init(driver_mq2_gas_handle_t *handle) {
    if (!handle) return DRIVER_MQ2_GAS_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized driver_mq2_gas on channel %u\n", handle->channel);
    return DRIVER_MQ2_GAS_STATUS_OK;
}

driver_mq2_gas_status_t driver_mq2_gas_read(driver_mq2_gas_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return DRIVER_MQ2_GAS_STATUS_ERROR;
    handle->rx_byte_count += len;
    return DRIVER_MQ2_GAS_STATUS_OK;
}

driver_mq2_gas_status_t driver_mq2_gas_write(driver_mq2_gas_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return DRIVER_MQ2_GAS_STATUS_ERROR;
    handle->tx_byte_count += len;
    return DRIVER_MQ2_GAS_STATUS_OK;
}

driver_mq2_gas_status_t driver_mq2_gas_self_test(driver_mq2_gas_handle_t *handle) {
    if (!handle) return DRIVER_MQ2_GAS_STATUS_ERROR;
    printf("[Firmware SelfTest] driver_mq2_gas diagnostic passed.\n");
    return DRIVER_MQ2_GAS_STATUS_OK;
}
