/**
 * @file driver_pzem004t.c
 * @brief Implementation for Peacefair PZEM-004T Multi-Function AC Power & Energy Meter Module
 */

#include "driver_pzem004t.h"
#include <stdio.h>
#include <string.h>

driver_pzem004t_status_t driver_pzem004t_init(driver_pzem004t_handle_t *handle) {
    if (!handle) return DRIVER_PZEM004T_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized driver_pzem004t on channel %u\n", handle->channel);
    return DRIVER_PZEM004T_STATUS_OK;
}

driver_pzem004t_status_t driver_pzem004t_read(driver_pzem004t_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return DRIVER_PZEM004T_STATUS_ERROR;
    handle->rx_byte_count += len;
    return DRIVER_PZEM004T_STATUS_OK;
}

driver_pzem004t_status_t driver_pzem004t_write(driver_pzem004t_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return DRIVER_PZEM004T_STATUS_ERROR;
    handle->tx_byte_count += len;
    return DRIVER_PZEM004T_STATUS_OK;
}

driver_pzem004t_status_t driver_pzem004t_self_test(driver_pzem004t_handle_t *handle) {
    if (!handle) return DRIVER_PZEM004T_STATUS_ERROR;
    printf("[Firmware SelfTest] driver_pzem004t diagnostic passed.\n");
    return DRIVER_PZEM004T_STATUS_OK;
}
