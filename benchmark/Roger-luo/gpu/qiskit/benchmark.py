import pytest
import numpy as np
import uuid
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

max_parallel_threads = 24
gpu = True

nqubits_list = range(4, 26)

def native_execute(benchmark, circuit, fusion_enable, include_compile_time):
    backend_options = {
        "method": "statevector",
        "device": "GPU" if gpu else "CPU",
        "precision": "double",
        "enable_truncation": False,
        "max_parallel_threads": max_parallel_threads,
        "fusion_enable": True,
        "fusion_threshold": 14,
        "fusion_max_qubit": 5,
    }
    if not fusion_enable:
        backend_options["fusion_enable"] = False
        backend_options["fusion_threshold"] = 30
        backend_options["fusion_max_qubit"] = 0

    backend = AerSimulator()
    backend.set_options(**backend_options)

    def evalfunc_include(backend, circuit):
        experiment = transpile(circuit, backend=backend)
        backend.run(experiment, shots=1)

    def evalfunc_exclude(backend, experiment):
        backend.run(experiment, shots=1)

    if include_compile_time:
        benchmark(evalfunc_include, backend, circuit)
    else:
        experiment = transpile(circuit, backend=backend)
        benchmark(evalfunc_exclude, backend, experiment)


def first_rotation(circuit, nqubits):
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def mid_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def last_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    return circuit


def entangler(circuit, pairs):
    for a, b in pairs:
        circuit.cx(a, b)
    return circuit


def generate_qcbm_circuit(nqubits, depth, pairs):
    circuit = QuantumCircuit(nqubits)
    first_rotation(circuit, nqubits)
    entangler(circuit, pairs)
    for k in range(depth - 1):
        mid_rotation(circuit, nqubits)
        entangler(circuit, pairs)
    last_rotation(circuit, nqubits)
    return circuit


"""
@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm_gf_inc(benchmark, nqubits):
    benchmark.group = "QCBMoptinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=True, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm_gf_exc(benchmark, nqubits):
    benchmark.group = "QCBMoptexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=True, include_compile_time=False)


"""
@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm_nogf_inc(benchmark, nqubits):
    benchmark.group = "QCBMinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=False, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm_nogf_exc(benchmark, nqubits):
    benchmark.group = "QCBMexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit, fusion_enable=False, include_compile_time=False)