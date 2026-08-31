#ifndef HAL_WATCHDOG_TIMER_H
#define HAL_WATCHDOG_TIMER_H

/**
 * @file hal_watchdog_timer.h
 * @brief Independent Hardware Watchdog (IWDG) and Task Liveness Monitor
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_WATCHDOG_TIMER_STATUS_OK = 0,
    HAL_WATCHDOG_TIMER_STATUS_ERROR = -1,
    HAL_WATCHDOG_TIMER_STATUS_BUSY = -2,
    HAL_WATCHDOG_TIMER_STATUS_TIMEOUT = -3
} hal_watchdog_timer_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_watchdog_timer_handle_t;

hal_watchdog_timer_status_t hal_watchdog_timer_init(hal_watchdog_timer_handle_t *handle);
hal_watchdog_timer_status_t hal_watchdog_timer_read(hal_watchdog_timer_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_watchdog_timer_status_t hal_watchdog_timer_write(hal_watchdog_timer_handle_t *handle, const uint8_t *data, uint16_t len);
hal_watchdog_timer_status_t hal_watchdog_timer_self_test(hal_watchdog_timer_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_WATCHDOG_TIMER_H
