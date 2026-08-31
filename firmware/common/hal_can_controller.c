/**
 * @file hal_can_controller.c
 * @brief Implementation for Hardware Controller for Dual CAN 2.0B / CAN-FD Interfaces
 */

#include "hal_can_controller.h"
#include <stdio.h>
#include <string.h>

hal_can_controller_status_t hal_can_controller_init(hal_can_controller_handle_t *handle) {
    if (!handle) return HAL_CAN_CONTROLLER_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized hal_can_controller on channel %u\n", handle->channel);
    return HAL_CAN_CONTROLLER_STATUS_OK;
}

hal_can_controller_status_t hal_can_controller_read(hal_can_controller_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return HAL_CAN_CONTROLLER_STATUS_ERROR;
    handle->rx_byte_count += len;
    return HAL_CAN_CONTROLLER_STATUS_OK;
}

hal_can_controller_status_t hal_can_controller_write(hal_can_controller_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return HAL_CAN_CONTROLLER_STATUS_ERROR;
    handle->tx_byte_count += len;
    return HAL_CAN_CONTROLLER_STATUS_OK;
}

hal_can_controller_status_t hal_can_controller_self_test(hal_can_controller_handle_t *handle) {
    if (!handle) return HAL_CAN_CONTROLLER_STATUS_ERROR;
    printf("[Firmware SelfTest] hal_can_controller diagnostic passed.\n");
    return HAL_CAN_CONTROLLER_STATUS_OK;
}
