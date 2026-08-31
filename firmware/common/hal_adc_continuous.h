#ifndef HAL_ADC_CONTINUOUS_H
#define HAL_ADC_CONTINUOUS_H

/**
 * @file hal_adc_continuous.h
 * @brief Hardware Abstraction Layer for DMA Continuous Scanning ADC Channels
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    HAL_ADC_CONTINUOUS_STATUS_OK = 0,
    HAL_ADC_CONTINUOUS_STATUS_ERROR = -1,
    HAL_ADC_CONTINUOUS_STATUS_BUSY = -2,
    HAL_ADC_CONTINUOUS_STATUS_TIMEOUT = -3
} hal_adc_continuous_status_t;

typedef struct {
    uint8_t channel;
    uint32_t baudrate;
    bool is_initialized;
    uint32_t rx_byte_count;
    uint32_t tx_byte_count;
    uint32_t error_count;
} hal_adc_continuous_handle_t;

hal_adc_continuous_status_t hal_adc_continuous_init(hal_adc_continuous_handle_t *handle);
hal_adc_continuous_status_t hal_adc_continuous_read(hal_adc_continuous_handle_t *handle, uint8_t *buffer, uint16_t len);
hal_adc_continuous_status_t hal_adc_continuous_write(hal_adc_continuous_handle_t *handle, const uint8_t *data, uint16_t len);
hal_adc_continuous_status_t hal_adc_continuous_self_test(hal_adc_continuous_handle_t *handle);

#ifdef __cplusplus
}
#endif

#endif // HAL_ADC_CONTINUOUS_H
