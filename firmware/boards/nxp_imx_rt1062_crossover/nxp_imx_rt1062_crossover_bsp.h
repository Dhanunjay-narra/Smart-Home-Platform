#ifndef NXP_IMX_RT1062_CROSSOVER_BSP_H
#define NXP_IMX_RT1062_CROSSOVER_BSP_H

/**
 * @file nxp_imx_rt1062_crossover_bsp.h
 * @brief Board Support Package for NXP i.MX RT1062 600MHz ARM Cortex-M7 Industrial Gateway
 * @copyright 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t cpu_frequency_hz;
    uint32_t flash_size_bytes;
    uint32_t ram_size_bytes;
    bool is_radio_initialized;
    uint32_t uptime_seconds;
    float core_temperature_c;
} nxp_imx_rt1062_crossover_bsp_info_t;

int nxp_imx_rt1062_crossover_bsp_init(void);
int nxp_imx_rt1062_crossover_bsp_get_info(nxp_imx_rt1062_crossover_bsp_info_t *info);
int nxp_imx_rt1062_crossover_bsp_enter_deep_sleep(uint32_t sleep_duration_ms);
int nxp_imx_rt1062_crossover_bsp_software_reset(void);

#ifdef __cplusplus
}
#endif

#endif // NXP_IMX_RT1062_CROSSOVER_BSP_H
