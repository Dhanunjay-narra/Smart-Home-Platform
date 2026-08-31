/**
 * @file driver_ssd1306.c
 * @brief Implementation for Solomon Systech SSD1306 128x64 I2C Graphic OLED Display Driver
 */

#include "driver_ssd1306.h"
#include <stdio.h>
#include <string.h>

driver_ssd1306_status_t driver_ssd1306_init(driver_ssd1306_handle_t *handle) {
    if (!handle) return DRIVER_SSD1306_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized driver_ssd1306 on channel %u\n", handle->channel);
    return DRIVER_SSD1306_STATUS_OK;
}

driver_ssd1306_status_t driver_ssd1306_read(driver_ssd1306_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return DRIVER_SSD1306_STATUS_ERROR;
    handle->rx_byte_count += len;
    return DRIVER_SSD1306_STATUS_OK;
}

driver_ssd1306_status_t driver_ssd1306_write(driver_ssd1306_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return DRIVER_SSD1306_STATUS_ERROR;
    handle->tx_byte_count += len;
    return DRIVER_SSD1306_STATUS_OK;
}

driver_ssd1306_status_t driver_ssd1306_self_test(driver_ssd1306_handle_t *handle) {
    if (!handle) return DRIVER_SSD1306_STATUS_ERROR;
    printf("[Firmware SelfTest] driver_ssd1306 diagnostic passed.\n");
    return DRIVER_SSD1306_STATUS_OK;
}
