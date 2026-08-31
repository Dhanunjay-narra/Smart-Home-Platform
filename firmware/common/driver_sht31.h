#ifndef DRIVER_SHT31_H
#define DRIVER_SHT31_H

/**
 * @file driver_sht31.h
 * @brief Sensirion SHT31-DIS High-Accuracy Temperature & Relative Humidity Sensor
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_SHT31_STATUS_OK = 0,
    DRIVER_SHT31_STATUS_ERROR = -1,
    DRIVER_SHT31_STATUS_BUSY = -2,
    DRIVER_SHT31_STATUS_TIMEOUT = -3
} driver_sht31_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_sht31_handle_t;

driver_sht31_status_t driver_sht31_init(driver_sht31_handle_t *handle);
driver_sht31_status_t driver_sht31_read(driver_sht31_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_sht31_status_t driver_sht31_write(driver_sht31_handle_t *handle, const uint8_t *data, uint16_t len);
driver_sht31_status_t driver_sht31_self_test(driver_sht31_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_SHT31_H
