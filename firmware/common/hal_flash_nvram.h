#ifndef HAL_FLASH_NVRAM_H
#define HAL_FLASH_NVRAM_H

/**
 * @file hal_flash_nvram.h
 * @brief Wear-Leveling Non-Volatile Flash Key-Value Storage Partition
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_FLASH_NVRAM_STATUS_OK = 0,
    HAL_FLASH_NVRAM_STATUS_ERROR = -1,
    HAL_FLASH_NVRAM_STATUS_BUSY = -2,
    HAL_FLASH_NVRAM_STATUS_TIMEOUT = -3
} hal_flash_nvram_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_flash_nvram_handle_t;

hal_flash_nvram_status_t hal_flash_nvram_init(hal_flash_nvram_handle_t *handle);
hal_flash_nvram_status_t hal_flash_nvram_read(hal_flash_nvram_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_flash_nvram_status_t hal_flash_nvram_write(hal_flash_nvram_handle_t *handle, const uint8_t *data, uint16_t len);
hal_flash_nvram_status_t hal_flash_nvram_self_test(hal_flash_nvram_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_FLASH_NVRAM_H
