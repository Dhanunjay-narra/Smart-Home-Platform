#ifndef HAL_SPI_BUS_H
#define HAL_SPI_BUS_H

/**
 * @file hal_spi_bus.h
 * @brief Hardware Abstraction Layer for High-Speed SPI Master/Slave
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_SPI_BUS_STATUS_OK = 0,
    HAL_SPI_BUS_STATUS_ERROR = -1,
    HAL_SPI_BUS_STATUS_BUSY = -2,
    HAL_SPI_BUS_STATUS_TIMEOUT = -3
} hal_spi_bus_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_spi_bus_handle_t;

hal_spi_bus_status_t hal_spi_bus_init(hal_spi_bus_handle_t *handle);
hal_spi_bus_status_t hal_spi_bus_read(hal_spi_bus_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_spi_bus_status_t hal_spi_bus_write(hal_spi_bus_handle_t *handle, const uint8_t *data, uint16_t len);
hal_spi_bus_status_t hal_spi_bus_self_test(hal_spi_bus_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_SPI_BUS_H
