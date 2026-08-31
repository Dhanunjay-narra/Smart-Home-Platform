#ifndef DRIVER_ST7789_H
#define DRIVER_ST7789_H

/**
 * @file driver_st7789.h
 * @brief Sitronix ST7789 IPS 240x240 Color SPI LCD Display Driver
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_ST7789_STATUS_OK = 0,
    DRIVER_ST7789_STATUS_ERROR = -1,
    DRIVER_ST7789_STATUS_BUSY = -2,
    DRIVER_ST7789_STATUS_TIMEOUT = -3
} driver_st7789_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_st7789_handle_t;

driver_st7789_status_t driver_st7789_init(driver_st7789_handle_t *handle);
driver_st7789_status_t driver_st7789_read(driver_st7789_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_st7789_status_t driver_st7789_write(driver_st7789_handle_t *handle, const uint8_t *data, uint16_t len);
driver_st7789_status_t driver_st7789_self_test(driver_st7789_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_ST7789_H
