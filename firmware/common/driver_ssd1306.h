#ifndef DRIVER_SSD1306_H
#define DRIVER_SSD1306_H

/**
 * @file driver_ssd1306.h
 * @brief Solomon Systech SSD1306 128x64 I2C Graphic OLED Display Driver
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_SSD1306_STATUS_OK = 0,
    DRIVER_SSD1306_STATUS_ERROR = -1,
    DRIVER_SSD1306_STATUS_BUSY = -2,
    DRIVER_SSD1306_STATUS_TIMEOUT = -3
} driver_ssd1306_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_ssd1306_handle_t;

driver_ssd1306_status_t driver_ssd1306_init(driver_ssd1306_handle_t *handle);
driver_ssd1306_status_t driver_ssd1306_read(driver_ssd1306_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_ssd1306_status_t driver_ssd1306_write(driver_ssd1306_handle_t *handle, const uint8_t *data, uint16_t len);
driver_ssd1306_status_t driver_ssd1306_self_test(driver_ssd1306_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_SSD1306_H
