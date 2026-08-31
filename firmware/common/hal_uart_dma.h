#ifndef HAL_UART_DMA_H
#define HAL_UART_DMA_H

/**
 * @file hal_uart_dma.h
 * @brief Hardware Abstraction Layer for Circular DMA-Buffered UART Serial
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_UART_DMA_STATUS_OK = 0,
    HAL_UART_DMA_STATUS_ERROR = -1,
    HAL_UART_DMA_STATUS_BUSY = -2,
    HAL_UART_DMA_STATUS_TIMEOUT = -3
} hal_uart_dma_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_uart_dma_handle_t;

hal_uart_dma_status_t hal_uart_dma_init(hal_uart_dma_handle_t *handle);
hal_uart_dma_status_t hal_uart_dma_read(hal_uart_dma_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_uart_dma_status_t hal_uart_dma_write(hal_uart_dma_handle_t *handle, const uint8_t *data, uint16_t len);
hal_uart_dma_status_t hal_uart_dma_self_test(hal_uart_dma_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_UART_DMA_H
