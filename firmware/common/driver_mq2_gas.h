#ifndef DRIVER_MQ2_GAS_H
#define DRIVER_MQ2_GAS_H

/**
 * @file driver_mq2_gas.h
 * @brief MQ-2 Combustible Gas & Smoke Semiconductor Detector Driver
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    DRIVER_MQ2_GAS_STATUS_OK = 0,
    DRIVER_MQ2_GAS_STATUS_ERROR = -1,
    DRIVER_MQ2_GAS_STATUS_BUSY = -2,
    DRIVER_MQ2_GAS_STATUS_TIMEOUT = -3
} driver_mq2_gas_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} driver_mq2_gas_handle_t;

driver_mq2_gas_status_t driver_mq2_gas_init(driver_mq2_gas_handle_t *handle);
driver_mq2_gas_status_t driver_mq2_gas_read(driver_mq2_gas_handle_t *handle, uint8_t *buffer, uint16_t len);
driver_mq2_gas_status_t driver_mq2_gas_write(driver_mq2_gas_handle_t *handle, const uint8_t *data, uint16_t len);
driver_mq2_gas_status_t driver_mq2_gas_self_test(driver_mq2_gas_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_MQ2_GAS_H
