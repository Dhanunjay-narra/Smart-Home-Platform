#ifndef FREERTOS_TASK_016_H
#define FREERTOS_TASK_016_H

/**
 * @file freertos_telemetry_task_016.h
 * @brief FreeRTOS Deterministic Sensor Acquisition Task 016
 * @copyright (c) 2026 Dhanunjay Narra. All Rights Reserved.
 */

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    uint32_t task_stack_size_words;
    uint32_t task_priority;
    uint32_t execution_period_ms;
    uint32_t loop_counter;
    uint32_t stack_high_water_mark;
    bool is_task_running;
} freertos_task_ctx_016_t;

int freertos_task_016_create(freertos_task_ctx_016_t *ctx);
int freertos_task_016_run_loop_iteration(freertos_task_ctx_016_t *ctx);
int freertos_task_016_delete(freertos_task_ctx_016_t *ctx);

#ifdef __cplusplus
}
#endif

#endif // FREERTOS_TASK_016_H
