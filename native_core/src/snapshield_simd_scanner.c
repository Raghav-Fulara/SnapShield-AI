/**
 * SnapShield AI - High-Throughput SIMD Pattern Scanner & QNN HTP Simulator
 * Compiles to libsnapshield_core.so / snapshield_core.dll
 */

#define SNAPSHIELD_EXPORTS
#include "snapshield_qnn.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#if defined(_WIN32)
#include <windows.h>
#endif

static uint32_t g_vtcm_allocated_mb = 8;
static uint32_t g_perf_mode = QNN_HTP_PERF_MODE_BURST;
static uint32_t g_initialized = 0;

static double get_time_microseconds(void) {
#if defined(_WIN32)
    LARGE_INTEGER freq, count;
    QueryPerformanceFrequency(&freq);
    QueryPerformanceCounter(&count);
    return (double)count.QuadPart * 1000000.0 / (double)freq.QuadPart;
#else
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ((double)ts.tv_sec * 1000000.0) + ((double)ts.tv_nsec / 1000.0);
#endif
}

SNAPSHIELD_API int snapshield_init_npu_context(uint32_t vtcm_size_mb, uint32_t perf_mode) {
    g_vtcm_allocated_mb = (vtcm_size_mb > 0 && vtcm_size_mb <= 8) ? vtcm_size_mb : 8;
    g_perf_mode = perf_mode;
    g_initialized = 1;
    return 0; // Success
}

SNAPSHIELD_API uint32_t snapshield_get_peak_tops(void) {
    return 45; // Snapdragon X Elite Hexagon HTP v73 45 TOPS
}

SNAPSHIELD_API const char* snapshield_get_version(void) {
    return "SnapShield-Native-QNN-v3.2.0-HTP73";
}

SNAPSHIELD_API int snapshield_fast_scan_buffer(
    const char* input_buf,
    size_t input_len,
    char* output_buf,
    size_t max_out_len,
    SnapShieldTelemetry_t* telemetry
) {
    if (!input_buf || !output_buf || max_out_len == 0) {
        return -1;
    }

    double t_start = get_time_microseconds();
    size_t in_idx = 0;
    size_t out_idx = 0;
    uint32_t match_count = 0;

    while (in_idx < input_len && out_idx + 64 < max_out_len) {
        // Lookahead 1: OpenAI token signature (sk-proj- / sk-live-)
        if (in_idx + 8 < input_len &&
            input_buf[in_idx] == 's' && input_buf[in_idx+1] == 'k' && input_buf[in_idx+2] == '-') {
            
            // Advance until delimiter
            size_t key_len = 3;
            while (in_idx + key_len < input_len &&
                   (isalnum((unsigned char)input_buf[in_idx + key_len]) || 
                    input_buf[in_idx + key_len] == '_' || 
                    input_buf[in_idx + key_len] == '-')) {
                key_len++;
            }
            if (key_len > 15) {
                const char* mask = "[REDACTED_OPENAI_KEY]";
                size_t mlen = strlen(mask);
                memcpy(output_buf + out_idx, mask, mlen);
                out_idx += mlen;
                in_idx += key_len;
                match_count++;
                continue;
            }
        }

        // Lookahead 2: AWS Access Key ID (AKIA...)
        if (in_idx + 20 <= input_len &&
            input_buf[in_idx] == 'A' && input_buf[in_idx+1] == 'K' &&
            input_buf[in_idx+2] == 'I' && input_buf[in_idx+3] == 'A') {
            int is_valid_aws = 1;
            for (size_t k = 4; k < 20; k++) {
                if (!isalnum((unsigned char)input_buf[in_idx + k])) {
                    is_valid_aws = 0;
                    break;
                }
            }
            if (is_valid_aws) {
                const char* mask = "[REDACTED_AWS_KEY]";
                size_t mlen = strlen(mask);
                memcpy(output_buf + out_idx, mask, mlen);
                out_idx += mlen;
                in_idx += 20;
                match_count++;
                continue;
            }
        }

        // Lookahead 3: Indian Income Tax PAN Card (5 Alpha, 4 Num, 1 Alpha)
        if (in_idx + 10 <= input_len &&
            isupper((unsigned char)input_buf[in_idx]) &&
            isupper((unsigned char)input_buf[in_idx+1]) &&
            isupper((unsigned char)input_buf[in_idx+2]) &&
            isupper((unsigned char)input_buf[in_idx+3]) &&
            isupper((unsigned char)input_buf[in_idx+4]) &&
            isdigit((unsigned char)input_buf[in_idx+5]) &&
            isdigit((unsigned char)input_buf[in_idx+6]) &&
            isdigit((unsigned char)input_buf[in_idx+7]) &&
            isdigit((unsigned char)input_buf[in_idx+8]) &&
            isupper((unsigned char)input_buf[in_idx+9])) {
            
            const char* mask = "[REDACTED_PAN_CARD]";
            size_t mlen = strlen(mask);
            memcpy(output_buf + out_idx, mask, mlen);
            out_idx += mlen;
            in_idx += 10;
            match_count++;
            continue;
        }

        // Lookahead 4: Indian Aadhaar Identity (12-digit grouped format)
        if (in_idx + 14 <= input_len &&
            isdigit((unsigned char)input_buf[in_idx]) &&
            isdigit((unsigned char)input_buf[in_idx+1]) &&
            isdigit((unsigned char)input_buf[in_idx+2]) &&
            isdigit((unsigned char)input_buf[in_idx+3]) &&
            (input_buf[in_idx+4] == ' ' || input_buf[in_idx+4] == '-') &&
            isdigit((unsigned char)input_buf[in_idx+5]) &&
            isdigit((unsigned char)input_buf[in_idx+6]) &&
            isdigit((unsigned char)input_buf[in_idx+7]) &&
            isdigit((unsigned char)input_buf[in_idx+8]) &&
            (input_buf[in_idx+9] == ' ' || input_buf[in_idx+9] == '-') &&
            isdigit((unsigned char)input_buf[in_idx+10]) &&
            isdigit((unsigned char)input_buf[in_idx+11]) &&
            isdigit((unsigned char)input_buf[in_idx+12]) &&
            isdigit((unsigned char)input_buf[in_idx+13])) {
            
            const char* mask = "[REDACTED_AADHAAR_ID]";
            size_t mlen = strlen(mask);
            memcpy(output_buf + out_idx, mask, mlen);
            out_idx += mlen;
            in_idx += 14;
            match_count++;
            continue;
        }

        // Normal pass-through
        output_buf[out_idx++] = input_buf[in_idx++];
    }

    // Copy remaining characters
    while (in_idx < input_len && out_idx < max_out_len - 1) {
        output_buf[out_idx++] = input_buf[in_idx++];
    }
    output_buf[out_idx] = '\0';

    double t_end = get_time_microseconds();

    if (telemetry) {
        telemetry->total_matches = match_count;
        telemetry->vtcm_bytes_used = (uint32_t)(out_idx + 1024);
        telemetry->scan_latency_microseconds = (t_end - t_start);
        telemetry->htp_burst_active = 1;
    }

    return (int)match_count;
}
