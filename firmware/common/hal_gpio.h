#ifndef HAL_GPIO_H
#define HAL_GPIO_H
#include <stdint.h>
#include <stdbool.h>

int hal_gpio_init(uint8_t pin, uint8_t mode);
int hal_gpio_write(uint8_t pin, uint8_t level);
uint8_t hal_gpio_read(uint8_t pin);
#endif
