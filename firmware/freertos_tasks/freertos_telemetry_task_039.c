/**
 * @file freertos_telemetry_task_039.c
 * @brief Implementation of FreeRTOS Real-Time Task 039
 */

#include "freertos_telemetry_task_039.h"
#include <stdio.h>

int freertos_task_039_create(freertos_task_ctx_039_t *ctx) {
    if (!ctx) return -1;
    ctx->task_stack_size_words = 2048;
    ctx->task_priority = 3;
    ctx->execution_period_ms = 100;
    ctx->loop_counter = 0;
    ctx->stack_high_water_mark = 512;
    ctx->is_task_running = true;
    printf("[FreeRTOS Task 039] Task spawned with priority %u\n", ctx->task_priority);
    return 0;
}

int freertos_task_039_run_loop_iteration(freertos_task_ctx_039_t *ctx) {
    if (!ctx || !ctx->is_task_running) return -1;
    ctx->loop_counter++;
    return 0;
}

int freertos_task_039_delete(freertos_task_ctx_039_t *ctx) {
    if (!ctx) return -1;
    ctx->is_task_running = false;
    return 0;
}
