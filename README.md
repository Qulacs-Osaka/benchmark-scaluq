# Benchmark codes for Scaluq

This repository contains source codes for benchmarking the execution times of 10-layer random quantum circuits with varying numbers of qubits.

We compare [Scaluq](https://github.com/qulacs/scaluq) against several popular quantum circuit simulators that provide Python or Julia interfaces and support double-precision simulation.

Execution times are measured under three settings:
- Single-thread CPU execution
- Multi-thread CPU execution
- GPU acceleration (if available)

If a simulator provides options for circuit optimization (e.g., gate fusion), we report results both with and without optimization.

The benchmark codes are based on [the benchmark project by Roger-luo](https://github.com/yardstiq/quantum-benchmarks).

## Batch execution comparison (Scaluq vs cuStateVec)

In addition to single-circuit benchmarks, we also provide performance comparisons for batch execution of multiple circuits. This highlights the unique capability of Scaluq to process a batch of independent quantum states efficiently, using either CPU or GPU.

As of now, among the evaluated simulators, only cuStateVec also supports batch-style simulation at the library level.

We measure the following aspects in batch execution:
- add later...
<!-- - Total execution time for processing N random circuits
- Per-circuit average execution time
- Memory usage (GPU/CPU)
- Scaling behavior as the batch size increases -->

These results are available in the `batch/` directory.

## Repository structure

- `benchmark/`: Benchmark codes for each simulator
    - `Roger-luo/`: Benchmark codes for single-circuit execution
    - `batch/`: Benchmark codes for batch execution (Scaluq and cuStateVec)
- `systeminfo/`: Text files describing installed library versions and system specs
- `image/`: Plots generated from benchmark results
- `plot.py`: Script to generate plots from output data

