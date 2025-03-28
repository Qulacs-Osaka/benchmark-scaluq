# Benchmark codes for Scaluq
Source codes for benchmarking the execution times of 10-layer random circuits with several numbers of qubits.

This repository shows a compoarison between [Scaluq](https://github.com/qulacs/scaluq) and several popular existing quantum circuit simulators that have the interfaces of Python or Julia and support simulation with double-precision.

Times are measured with single-thread, multi-thread, and GPU acceralation. If an option of circuit optimization such as gate fusion is provided, we check times with and without circuit optimization.

The benchmark codes are created based on [the benchmark project by Roger-luo](https://github.com/yardstiq/quantum-benchmarks).

The versions of installed libraries and relevant information are listed in the text files at systeminfo. The benchmark codes are saved in benchmark folder. The results are plotted in image folder by plot.py.