#ifndef DRIVER_SERVO_LOCK_H
#define DRIVER_SERVO_LOCK_H

/**
 * @file driver_servo_lock.h
 * @brief Precision Micro-Servo Deadbolt Actuator Controller with Stall Detection
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_SERVO_LOCK_STATUS_OK = 0,
    DRIVER_SERVO_LOCK_STATUS_ERROR = -1,
    DRIVER_SERVO_LOCK_STATUS_BUSY = -2,
    DRIVER_SERVO_LOCK_STATUS_TIMEOUT = -3
} driver_servo_lock_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_servo_lock_handle_t;

driver_servo_lock_status_t driver_servo_lock_init(driver_servo_lock_handle_t *handle);
driver_servo_lock_status_t driver_servo_lock_read(driver_servo_lock_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_servo_lock_status_t driver_servo_lock_write(driver_servo_lock_handle_t *handle, const uint8_t *data, uint16_t len);
driver_servo_lock_status_t driver_servo_lock_self_test(driver_servo_lock_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_SERVO_LOCK_H
