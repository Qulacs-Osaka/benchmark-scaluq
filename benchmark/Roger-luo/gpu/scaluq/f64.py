import pytest
import numpy as np
from scaluq import X, T, H, CNOT, ParametricRZ, ParametricRX, DenseMatrix
from scaluq.f64.gate import *

# import mkl
# mkl.set_num_threads(1)

nqubits_list = range(4, 26)

def first_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add_gate(RX(k, np.random.rand()))
        circuit.add_gate(RZ(k, np.random.rand()))


def mid_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add_gate(RZ(k, np.random.rand()))
        circuit.add_gate(RX(k, np.random.rand()))
        circuit.add_gate(RZ(k, np.random.rand()))


def last_rotation(circuit, nqubits):
    for k in range(nqubits):
        circuit.add_gate(RZ(k, np.random.rand()))
        circuit.add_gate(RX(k, np.random.rand()))

def entangler(circuit, nqubits, pairs):
    for a, b in pairs:
        circuit.add_gate(CNOT(a, b))

def build_circuit(nqubits, depth, pairs):
    circuit = Circuit(nqubits)
    first_rotation(circuit, nqubits)
    entangler(circuit, nqubits, pairs)
    for _ in range(depth):
        mid_rotation(circuit, nqubits)
        entangler(circuit, nqubits, pairs)

    last_rotation(circuit, nqubits)
    return circuit

def benchfunc_noopt(circuit, nqubits):
    st = StateVector(nqubits)
    circuit.update_quantum_state(st)

# def benchfunc(qco, circuit, nqubits):
#     st = StateVector(nqubits)
#     qco.optimize_light(circuit)
#     circuit.update_quantum_state(st)

# @pytest.mark.parametrize("nqubits", nqubits_list)
# def test_QCBMopt(benchmark, nqubits):
#     benchmark.group = "QCBMopt"
#     pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
#     circuit = build_circuit(nqubits, 9, pairs)
#     qco = QCO()
#     benchmark(benchfunc, qco, circuit, nqubits)

@pytest.mark.parametrize("nqubits", nqubits_list)
def test_QCBM(benchmark, nqubits):
    benchmark.group = "QCBM"
    pairs = [(i, (i+1) % nqubits) for i in range(nqubits)]
    circuit = build_circuit(nqubits, 9, pairs)
    benchmark(benchfunc_noopt, circuit, nqubits)