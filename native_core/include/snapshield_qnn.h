/**
 * SnapShield AI - Qualcomm QNN & SIMD Hardware Acceleration Header
 * Target: Qualcomm Snapdragon X Elite (Hexagon HTP v73 / 45 TOPS)
 * Platform: Windows on ARM64 / Cross-Platform POSIX
 */

#ifndef SNAPSHIELD_QNN_H
#define SNAPSHIELD_QNN_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32) || defined(__CYGWIN__)
  #ifdef SNAPSHIELD_EXPORTS
    #define SNAPSHIELD_API __declspec(dllexport)
  #else
    #define SNAPSHIELD_API __declspec(dllimport)
  #endif
#else
  #define SNAPSHIELD_API __attribute__((visibility("default")))
#endif

/* Qualcomm Hexagon Tensor Processor (HTP) Architecture Constants */
#define QNN_HTP_ARCH_V73            0x0073
#define QNN_HTP_VTCM_MAX_BYTES      (8 * 1024 * 1024) /* 8MB VTCM */
#define QNN_HTP_PERF_MODE_BURST     0x01
#define QNN_HTP_PRECISION_INT8      0x08

/* Scan Entity Types */
typedef enum {
    ENTITY_TYPE_NONE = 0,
    ENTITY_TYPE_OPENAI_KEY = 1,
    ENTITY_TYPE_AWS_KEY = 2,
    ENTITY_TYPE_AADHAAR = 3,
    ENTITY_TYPE_PAN = 4,
    ENTITY_TYPE_DATABASE_URL = 5,
    ENTITY_TYPE_CREDIT_CARD = 6
} SnapShieldEntityType_t;

typedef struct {
    SnapShieldEntityType_t type;
    size_t start_offset;
    size_t length;
    char token_tag[32];
} SnapShieldMatch_t;

typedef struct {
    uint32_t total_matches;
    uint32_t vtcm_bytes_used;
    double scan_latency_microseconds;
    uint32_t htp_burst_active;
} SnapShieldTelemetry_t;

/* Native API Prototypes */
SNAPSHIELD_API int snapshield_init_npu_context(uint32_t vtcm_size_mb, uint32_t perf_mode);
SNAPSHIELD_API int snapshield_fast_scan_buffer(const char* input_buf, size_t input_len, char* output_buf, size_t max_out_len, SnapShieldTelemetry_t* telemetry);
SNAPSHIELD_API const char* snapshield_get_version(void);
SNAPSHIELD_API uint32_t snapshield_get_peak_tops(void);

#ifdef __cplusplus
}
#endif

#endif /* SNAPSHIELD_QNN_H */
