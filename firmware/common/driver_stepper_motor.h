#ifndef DRIVER_STEPPER_MOTOR_H
#define DRIVER_STEPPER_MOTOR_H

/**
 * @file driver_stepper_motor.h
 * @brief A4988 / TMC2209 SilentStepStick Motorized Blind Stepper Driver
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_STEPPER_MOTOR_STATUS_OK = 0,
    DRIVER_STEPPER_MOTOR_STATUS_ERROR = -1,
    DRIVER_STEPPER_MOTOR_STATUS_BUSY = -2,
    DRIVER_STEPPER_MOTOR_STATUS_TIMEOUT = -3
} driver_stepper_motor_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_stepper_motor_handle_t;

driver_stepper_motor_status_t driver_stepper_motor_init(driver_stepper_motor_handle_t *handle);
driver_stepper_motor_status_t driver_stepper_motor_read(driver_stepper_motor_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_stepper_motor_status_t driver_stepper_motor_write(driver_stepper_motor_handle_t *handle, const uint8_t *data, uint16_t len);
driver_stepper_motor_status_t driver_stepper_motor_self_test(driver_stepper_motor_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_STEPPER_MOTOR_H
