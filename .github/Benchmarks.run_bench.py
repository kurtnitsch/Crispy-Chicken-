#!/usr/bin/env python3
import json, time, subprocess, platform, os, statistics, sys
OUT = sys.argv[1] if len(sys.argv)>1 else "bench_results.json"

def info():
    return {
        "git_commit": subprocess.getoutput("git rev-parse --short HEAD"),
        "dfx_version": subprocess.getoutput("dfx --version"),
        "cpu": platform.processor(),
        "platform": platform.platform(),
        "env": {k:v for k,v in os.environ.items() if k.startswith("DFX") or k.startswith("CI")}
    }

def run_latency(cmd, n=50):
    samples=[]
    for _ in range(n):
        t0=time.perf_counter()
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        samples.append((time.perf_counter()-t0)*1000.0) # ms
    return samples

# EXAMPLE: call a cli that performs a verified inference
samples = run_latency("python tools/invoke_inference.py --input examples/x.json", n=30)
data = {
    "meta": info(),
    "scenario": "verified_inference",
    "n": len(samples),
    "median_ms": statistics.median(samples),
    "p95_ms": sorted(samples)[int(0.95*len(samples))-1],
    "raw": samples
}
with open(OUT,"w") as f:
    json.dump(data, f, indent=2)
print("Wrote", OUT)
