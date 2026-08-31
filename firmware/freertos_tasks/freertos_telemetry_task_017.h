#ifndef FREERTOS_TASK_017_H
#define FREERTOS_TASK_017_H

/**
 * @file freertos_telemetry_task_017.h
 * @brief FreeRTOS Deterministic Sensor Acquisition Task 017
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
} freertos_task_ctx_017_t;

int freertos_task_017_create(freertos_task_ctx_017_t *ctx);
int freertos_task_017_run_loop_iteration(freertos_task_ctx_017_t *ctx);
int freertos_task_017_delete(freertos_task_ctx_017_t *ctx);

#ifdef __cplusplus
}
#endif

#endif // FREERTOS_TASK_017_H
