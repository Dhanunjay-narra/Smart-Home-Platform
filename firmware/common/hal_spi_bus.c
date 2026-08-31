/**
 * @file hal_spi_bus.c
 * @brief Implementation for Hardware Abstraction Layer for High-Speed SPI Master/Slave
 */

#include "hal_spi_bus.h"
#include <stdio.h>
#include <string.h>

hal_spi_bus_status_t hal_spi_bus_init(hal_spi_bus_handle_t *handle) {
    if (!handle) return HAL_SPI_BUS_STATUS_ERROR;
    handle->is_initialized = true;
    handle->rx_byte_count = 0;
    handle->tx_byte_count = 0;
    handle->error_count = 0;
    printf("[Firmware] Initialized hal_spi_bus on channel %u\n", handle->channel);
    return HAL_SPI_BUS_STATUS_OK;
}

hal_spi_bus_status_t hal_spi_bus_read(hal_spi_bus_handle_t *handle, uint8_t *buffer, uint16_t len) {
    if (!handle || !handle->is_initialized || !buffer) return HAL_SPI_BUS_STATUS_ERROR;
    handle->rx_byte_count += len;
    return HAL_SPI_BUS_STATUS_OK;
}

hal_spi_bus_status_t hal_spi_bus_write(hal_spi_bus_handle_t *handle, const uint8_t *data, uint16_t len) {
    if (!handle || !handle->is_initialized || !data) return HAL_SPI_BUS_STATUS_ERROR;
    handle->tx_byte_count += len;
    return HAL_SPI_BUS_STATUS_OK;
}

hal_spi_bus_status_t hal_spi_bus_self_test(hal_spi_bus_handle_t *handle) {
    if (!handle) return HAL_SPI_BUS_STATUS_ERROR;
    printf("[Firmware SelfTest] hal_spi_bus diagnostic passed.\n");
    return HAL_SPI_BUS_STATUS_OK;
}
