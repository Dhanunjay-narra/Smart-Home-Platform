#ifndef DRIVER_LD2410_H
#define DRIVER_LD2410_H

/**
 * @file driver_ld2410.h
 * @brief Hi-Link LD2410 24GHz FMCW Human Presence Radar Sensor
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_LD2410_STATUS_OK = 0,
    DRIVER_LD2410_STATUS_ERROR = -1,
    DRIVER_LD2410_STATUS_BUSY = -2,
    DRIVER_LD2410_STATUS_TIMEOUT = -3
} driver_ld2410_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_ld2410_handle_t;

driver_ld2410_status_t driver_ld2410_init(driver_ld2410_handle_t *handle);
driver_ld2410_status_t driver_ld2410_read(driver_ld2410_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_ld2410_status_t driver_ld2410_write(driver_ld2410_handle_t *handle, const uint8_t *data, uint16_t len);
driver_ld2410_status_t driver_ld2410_self_test(driver_ld2410_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_LD2410_H
