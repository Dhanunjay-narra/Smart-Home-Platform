#ifndef DRIVER_PZEM004T_H
#define DRIVER_PZEM004T_H

/**
 * @file driver_pzem004t.h
 * @brief Peacefair PZEM-004T Multi-Function AC Power & Energy Meter Module
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_PZEM004T_STATUS_OK = 0,
    DRIVER_PZEM004T_STATUS_ERROR = -1,
    DRIVER_PZEM004T_STATUS_BUSY = -2,
    DRIVER_PZEM004T_STATUS_TIMEOUT = -3
} driver_pzem004t_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_pzem004t_handle_t;

driver_pzem004t_status_t driver_pzem004t_init(driver_pzem004t_handle_t *handle);
driver_pzem004t_status_t driver_pzem004t_read(driver_pzem004t_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_pzem004t_status_t driver_pzem004t_write(driver_pzem004t_handle_t *handle, const uint8_t *data, uint16_t len);
driver_pzem004t_status_t driver_pzem004t_self_test(driver_pzem004t_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_PZEM004T_H
