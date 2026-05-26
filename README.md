# Benchmark codes for Scaluq

Source codes for benchmarking batched quantum circuit simulations with various numbers of qubits and batch sizes.

This repository compares [Scaluq](https://github.com/qulacs/scaluq) with several popular quantum circuit simulators and state vector libraries that support double-precision simulation.

Benchmarks are performed with:
- multi-thread execution
- GPU acceleration include execution of single circuit and batched circuits

## Benchmark circuits

The benchmark uses layered random quantum circuits consisting of nearest-neighbor entangling gates and random single-qubit rotations.

For each layer and each qubit `q`, the following operations are applied:

```math
\operatorname{CX}(q, (q + 1)\ \text{mod}\ n)
\rightarrow \operatorname{RX}(q, \theta_q)
\rightarrow \operatorname{RZ}(q, \phi_q)
```

where $\theta_q$ and $\phi_q$ are random angles sampled uniformly from `[0, 2π)`.

The resulting circuit forms a ring-type entangling structure because the last qubit is connected to the first qubit by a CX gate.

The same circuit is repeatedly applied to batched state vectors for performance measurements.

The benchmark codes are inspired by [the benchmark project by Roger-luo](https://github.com/yardstiq/quantum-benchmarks), although the benchmark circuits and implementations used in this repository are different.

Installed library versions and environment information are listed in the `systeminfo` directory.

Benchmark source codes are stored in the `benchmark` directory, and plotted figures are generated into the `image` directory.