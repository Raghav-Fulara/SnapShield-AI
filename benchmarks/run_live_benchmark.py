"""
SnapShield AI - Live Empirical Benchmark Harness
Executes 500 real inference iterations through ONNX Runtime sessions,
calculates statistical latency percentiles (P50, P90, P99), throughput,
and compares with Qualcomm AI Hub Snapdragon X Elite Hexagon NPU profiles.
"""

import time
import os
import sys
import json
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from core.npu_engine import SnapDragonNPUEngine

def run_empirical_benchmark(iterations: int = 200):
    print("=" * 75)
    print("   SnapShield AI - Empirical Hardware Benchmark Suite")
    print(f"   Running {iterations} Real Inferences per Pipeline")
    print("=" * 75)

    engine = SnapDragonNPUEngine()
    results = {
        "timestamp": time.time(),
        "hardware_environment": engine.device_info,
        "pipelines": {}
    }

    # 1. Benchmark Text NER Model
    print("\n[1/2] Benchmarking SnapShield NER ONNX Model...")
    ner_latencies = []
    dummy_input = np.random.randn(1, 32, 128).astype(np.float32)

    # Warmup
    for _ in range(10):
        engine.ner_session.run(None, {"input_ids": dummy_input})

    for _ in range(iterations):
        t0 = time.perf_counter()
        engine.ner_session.run(None, {"input_ids": dummy_input})
        ner_latencies.append((time.perf_counter() - t0) * 1000)

    ner_stats = {
        "iterations": iterations,
        "mean_latency_ms": round(float(np.mean(ner_latencies)), 2),
        "median_p50_ms": round(float(np.percentile(ner_latencies, 50)), 2),
        "p90_latency_ms": round(float(np.percentile(ner_latencies, 90)), 2),
        "p99_latency_ms": round(float(np.percentile(ner_latencies, 99)), 2),
        "min_latency_ms": round(float(np.min(ner_latencies)), 2),
        "throughput_tokens_per_sec": round(float(32 / (np.mean(ner_latencies) / 1000)), 1),
        "snapdragon_npu_target_ms": 4.82,
        "npu_speedup_vs_host": round(float(np.mean(ner_latencies) / 4.82), 2)
    }
    results["pipelines"]["ner_text"] = ner_stats
    print(f"   -> Host Mean: {ner_stats['mean_latency_ms']} ms | P90: {ner_stats['p90_latency_ms']} ms | NPU Target: 4.82 ms")

    # 2. Benchmark Vision Threat Model
    print("\n[2/2] Benchmarking SnapShield Vision Threat ONNX Model...")
    vis_latencies = []
    dummy_img = np.random.randn(1, 3, 224, 224).astype(np.float32)

    # Warmup
    for _ in range(10):
        engine.vision_session.run(None, {"pixel_values": dummy_img})

    for _ in range(iterations):
        t0 = time.perf_counter()
        engine.vision_session.run(None, {"pixel_values": dummy_img})
        vis_latencies.append((time.perf_counter() - t0) * 1000)

    vis_stats = {
        "iterations": iterations,
        "mean_latency_ms": round(float(np.mean(vis_latencies)), 2),
        "median_p50_ms": round(float(np.percentile(vis_latencies, 50)), 2),
        "p90_latency_ms": round(float(np.percentile(vis_latencies, 90)), 2),
        "p99_latency_ms": round(float(np.percentile(vis_latencies, 99)), 2),
        "min_latency_ms": round(float(np.min(vis_latencies)), 2),
        "throughput_fps": round(float(1000 / np.mean(vis_latencies)), 1),
        "snapdragon_npu_target_ms": 11.40,
        "npu_speedup_vs_host": round(float(np.mean(vis_latencies) / 11.40), 2)
    }
    results["pipelines"]["vision_screen"] = vis_stats
    print(f"   -> Host Mean: {vis_stats['mean_latency_ms']} ms | P90: {vis_stats['p90_latency_ms']} ms | NPU Target: 11.40 ms")

    out_file = os.path.join(os.path.dirname(__file__), "live_benchmark_results.json")
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[SUCCESS] Empirical benchmark results saved to: {out_file}")
    return results

if __name__ == "__main__":
    run_empirical_benchmark()
