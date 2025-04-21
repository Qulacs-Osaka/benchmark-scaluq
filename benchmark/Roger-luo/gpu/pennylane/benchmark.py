import pytest
import numpy as np
import pennylane as qml

# --- config ---
max_parallel_threads = 16
gpu = True
# CPUシミュレータ → "lightning.qubit", GPUシミュレータ → "lightning.gpu"
plugin = "lightning.gpu" if gpu else "lightning.qubit"

nqubits_list = range(4, 26)

def native_execute(benchmark, dev, include_compile_time):

    def evalfunc_include(circuit):

    def evalfunc_exclude(circuit):

    if include_compile_time:
        benchmark(evalfunc_include, circuit)
    else:
        benchmark(evalfunc_exclude, circuit)

def first_rotation(nqubits):
    qml.RX(np.random.rand(), range(nqubits))
    qml.RZ(np.random.rand(), range(nqubits))

def mid_rotation(nqubits):
    qml.RZ(np.random.rand(), range(nqubits))
    qml.RX(np.random.rand(), range(nqubits))
    qml.RZ(np.random.rand(), range(nqubits))

def last_rotation(nqubits):
    qml.RZ(np.random.rand(), range(nqubits))
    qml.RX(np.random.rand(), range(nqubits))

def entangler(nqubits, pairs):
    for a, b in pairs:
        qml.CNOT(wires=[a, b])

def generate_qcbm_circuit(nqubits, depth, pairs):
    dev = qml.device(plugin, wires=nqubits)
    first_rotation(nqubits)
    entangler(nqubits, pairs)
    for k in range(depth - 1):
        mid_rotation(nqubits)
        entangler(nqubits, pairs)
    last_rotation(nqubits)
