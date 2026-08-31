#ifndef HAL_CAN_CONTROLLER_H
#define HAL_CAN_CONTROLLER_H

/**
 * @file hal_can_controller.h
 * @brief Hardware Controller for Dual CAN 2.0B / CAN-FD Interfaces
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_CAN_CONTROLLER_STATUS_OK = 0,
    HAL_CAN_CONTROLLER_STATUS_ERROR = -1,
    HAL_CAN_CONTROLLER_STATUS_BUSY = -2,
    HAL_CAN_CONTROLLER_STATUS_TIMEOUT = -3
} hal_can_controller_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_can_controller_handle_t;

hal_can_controller_status_t hal_can_controller_init(hal_can_controller_handle_t *handle);
hal_can_controller_status_t hal_can_controller_read(hal_can_controller_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_can_controller_status_t hal_can_controller_write(hal_can_controller_handle_t *handle, const uint8_t *data, uint16_t len);
hal_can_controller_status_t hal_can_controller_self_test(hal_can_controller_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_CAN_CONTROLLER_H
