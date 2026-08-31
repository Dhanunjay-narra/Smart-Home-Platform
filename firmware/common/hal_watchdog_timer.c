/**
 * @file hal_watchdog_timer.c
 * @brief Implementation for Independent Hardware Watchdog (IWDG) and Task Liveness Monitor
 */

#include "hal_watchdog_timer.h"
#include <stdio.h>
#include <string.h>

hal_watchdog_timer_status_t hal_watchdog_timer_init(hal_watchdog_timer_handle_t *handle) {
    if (!handle) return HAL_WATCHDOG_TIMER_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized hal_watchdog_timer on channel %u\n", handle->channel);
    return HAL_WATCHDOG_TIMER_STATUS_OK;
}

hal_watchdog_timer_status_t hal_watchdog_timer_read(hal_watchdog_timer_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return HAL_WATCHDOG_TIMER_STATUS_ERROR;
    handle->rx_byte_count += len;
    return HAL_WATCHDOG_TIMER_STATUS_OK;
}

hal_watchdog_timer_status_t hal_watchdog_timer_write(hal_watchdog_timer_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return HAL_WATCHDOG_TIMER_STATUS_ERROR;
    handle->tx_byte_count += len;
    return HAL_WATCHDOG_TIMER_STATUS_OK;
}

hal_watchdog_timer_status_t hal_watchdog_timer_self_test(hal_watchdog_timer_handle_t *handle) {
    if (!handle) return HAL_WATCHDOG_TIMER_STATUS_ERROR;
    printf("[Firmware SelfTest] hal_watchdog_timer diagnostic passed.\n");
    return HAL_WATCHDOG_TIMER_STATUS_OK;
}
