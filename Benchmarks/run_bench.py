#!/usr/bin/env python3
"""
Crispy Chicken Benchmark Harness
--------------------------------
Measures:
- Model load time
- Inference latency (native / verified)
- Swarm coordination latency
- Proof verification latency
- Memory usage
Outputs JSON + CSV
"""

import os, time, json, csv, subprocess, statistics, platform, psutil
from datetime import datetime

OUT_JSON = "bench_results.json"
OUT_CSV = "bench_results.csv"
N_RUNS = 30
WARMUP = 3

# ---------------- Meta Info ----------------
def get_meta():
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "git_commit": subprocess.getoutput("git rev-parse --short HEAD"),
        "dfx_version": subprocess.getoutput("dfx --version"),
        "platform": platform.platform(),
        "cpu": platform.processor(),
        "cores": os.cpu_count(),
        "memory_gb": round(psutil.virtual_memory().total/1e9,2)
    }

# ---------------- Helpers ----------------
def run_cmd(cmd):
    """Run a shell command and return runtime in ms"""
    start = time.perf_counter()
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return (time.perf_counter()-start)*1000

def calc_stats(samples):
    return {
        "n": len(samples),
        "median_ms": statistics.median(samples),
        "mean_ms": statistics.mean(samples),
        "stdev_ms": statistics.stdev(samples) if len(samples)>1 else 0,
        "p95_ms": sorted(samples)[int(0.95*len(samples))-1],
        "raw": samples
    }

# ---------------- Benchmark Scenarios ----------------
def bench_model_load():
    samples=[]
    for i in range(N_RUNS+WARMUP):
        ms = run_cmd("python benchmarks/tools/load_model.py")
        if i>=WARMUP: samples.append(ms)
    return calc_stats(samples)

def bench_inference(verified=True):
    mode = "--verified" if verified else "--native"
    samples=[]
    for i in range(N_RUNS+WARMUP):
        ms = run_cmd(f"python benchmarks/tools/invoke_inference.py {mode}")
        if i>=WARMUP: samples.append(ms)
    return calc_stats(samples)

def bench_swarm_coord():
    samples=[]
    for i in range(N_RUNS+WARMUP):
        ms = run_cmd("python benchmarks/tools/swarm_message.py")
        if i>=WARMUP: samples.append(ms)
    return calc_stats(samples)

def bench_proof_verification():
    samples=[]
    for i in range(N_RUNS+WARMUP):
        ms = run_cmd("python benchmarks/tools/verify_proof.py")
        if i>=WARMUP: samples.append(ms)
    return calc_stats(samples)

# ---------------- Main ----------------
def main():
    results = {"meta": get_meta(), "benchmarks": {}}

    print("[*] Running Crispy Chicken Benchmarks...")
    results["benchmarks"]["model_load"] = bench_model_load()
    results["benchmarks"]["inference_native"] = bench_inference(verified=False)
    results["benchmarks"]["inference_verified"] = bench_inference(verified=True)
    results["benchmarks"]["swarm_coord"] = bench_swarm_coord()
    results["benchmarks"]["proof_verification"] = bench_proof_verification()

    # Save JSON
    with open(OUT_JSON,"w") as f: json.dump(results,f,indent=2)
    print(f"[+] JSON results saved to {OUT_JSON}")

    # Save CSV
    with open(OUT_CSV,"w",newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["scenario","median_ms","mean_ms","stdev_ms","p95_ms","n"])
        for k,v in results["benchmarks"].items():
            writer.writerow([k,v["median_ms"],v["mean_ms"],v["stdev_ms"],v["p95_ms"],v["n"]])
    print(f"[+] CSV results saved to {OUT_CSV}")

if __name__=="__main__":
    main()
