#ifndef DRIVER_PERIPHERAL_013_H
#define DRIVER_PERIPHERAL_013_H

/**
 * @file embedded_driver_peripheral_013.h
 * @brief Embedded Hardware Driver 013 for High-Reliability Smart Home Nodes
 * @copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint16_t peripheral_id;
    uint32_t base_address;
    uint8_t irq_number;
    bool is_dma_enabled;
    uint32_t transaction_count;
    uint32_t error_count;
} driver_peripheral_013_t;

int driver_peripheral_013_init(driver_peripheral_013_t *dev);
int driver_peripheral_013_read(driver_peripheral_013_t *dev, uint8_t *dest, uint16_t len);
int driver_peripheral_013_write(driver_peripheral_013_t *dev, const uint8_t *src, uint16_t len);
int driver_peripheral_013_self_test(driver_peripheral_013_t *dev);

#ifdef __cplusplus
}
#endif

#endif // DRIVER_PERIPHERAL_013_H
