#ifndef DRIVER_BME680_H
#define DRIVER_BME680_H

/**
 * @file driver_bme680.h
 * @brief Bosch Sensortec BME680 Temperature, Humidity, Pressure & VOC Sensor
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_BME680_STATUS_OK = 0,
    DRIVER_BME680_STATUS_ERROR = -1,
    DRIVER_BME680_STATUS_BUSY = -2,
    DRIVER_BME680_STATUS_TIMEOUT = -3
} driver_bme680_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_bme680_handle_t;

driver_bme680_status_t driver_bme680_init(driver_bme680_handle_t *handle);
driver_bme680_status_t driver_bme680_read(driver_bme680_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_bme680_status_t driver_bme680_write(driver_bme680_handle_t *handle, const uint8_t *data, uint16_t len);
driver_bme680_status_t driver_bme680_self_test(driver_bme680_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_BME680_H
