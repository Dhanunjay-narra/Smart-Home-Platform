#ifndef DRIVER_WIEGAND_READER_H
#define DRIVER_WIEGAND_READER_H

/**
 * @file driver_wiegand_reader.h
 * @brief Dual-GPIO Interrupt Driven Wiegand 26/34 RFID Access Card Reader
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_WIEGAND_READER_STATUS_OK = 0,
    DRIVER_WIEGAND_READER_STATUS_ERROR = -1,
    DRIVER_WIEGAND_READER_STATUS_BUSY = -2,
    DRIVER_WIEGAND_READER_STATUS_TIMEOUT = -3
} driver_wiegand_reader_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_wiegand_reader_handle_t;

driver_wiegand_reader_status_t driver_wiegand_reader_init(driver_wiegand_reader_handle_t *handle);
driver_wiegand_reader_status_t driver_wiegand_reader_read(driver_wiegand_reader_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_wiegand_reader_status_t driver_wiegand_reader_write(driver_wiegand_reader_handle_t *handle, const uint8_t *data, uint16_t len);
driver_wiegand_reader_status_t driver_wiegand_reader_self_test(driver_wiegand_reader_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_WIEGAND_READER_H
