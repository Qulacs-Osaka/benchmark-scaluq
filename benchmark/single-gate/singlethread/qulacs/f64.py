import pytest
import itertools
import random
from scipy.stats import unitary_group
import math
from typing import Callable
import qulacs
import qulacs.gate as mgate

single_gates = [
    ("X", mgate.X),
    ("Y", mgate.Y),
    ("Z", mgate.Z),
    ("H", mgate.H),
    ("S", mgate.S),
    ("Sdag", mgate.Sdag),
    ("T", mgate.T),
    ("Tdag", mgate.Tdag)
]
single_angle_gates = [
    ("RX", mgate.RX),
    ("RY", mgate.RY),
    ("RZ", mgate.RZ)
]

def CH(c, t):
    h = mgate.H(t)
    g = mgate.to_matrix_gate(h)
    g.add_control_qubit(c, 0)
    return g

def dense2(t1, t2):
    mat = unitary_group.rvs(4)
    return mgate.DenseMatrix([t1, t2], mat)

double_gates = [
    ("CX", mgate.CNOT),
    #("CZ", mgate.CZ),
    #("SWAP", mgate.SWAP),
    #("CH", CH),
    #("2 qubits dense", dense2)
]

nqubits_list = range(4, 22)


def benchfunc(circuit, state):
    circuit.update_quantum_state(state)
    #cp.cuda.runtime.deviceSynchronize()

def create_params(gates: list[tuple[str, Callable[..., qulacs.QuantumGateBase]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

'''
single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = qulacs.QuantumCircuit(nqubits)
    for __ in range(100):
        for _ in range(nqubits-1):
            for i in range(nqubits):
                circuit.add_gate(factory(i))
    state = qulacs.StateVector(nqubits)
    benchmark(benchfunc, circuit, state)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = qulacs.QuantumCircuit(nqubits)
    for __ in range(100):
        for _ in range(nqubits-1):
            for i in range(nqubits):
                circuit.add_gate(factory(i, random.random() * math.pi * 2))
    state = qulacs.StateVector(nqubits)
    benchmark(benchfunc, circuit, state)
'''

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = qulacs.QuantumCircuit(nqubits)
    for __ in range(100):
        for t1 in range(nqubits):
            for t2 in range(nqubits):
                if t1 == t2: continue
                circuit.add_gate(factory(t1, t2))
    state = qulacs.StateVector(nqubits)
    benchmark(benchfunc, circuit, state)
