import pytest
import itertools
import random
from scipy.stats import unitary_group
import math
from typing import Callable
import scaluq as scaluqbase
import scaluq.default.f16 as scaluq
import scaluq.default.f16.gate as mgate

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
    return mgate.H(t, controls=[c])

def dense2(t1, t2):
    mat = unitary_group.rvs(4)
    return mgate.DenseMatrix([t1, t2], mat)

double_gates = [
    ("CX", mgate.CX),
    #("CZ", mgate.CZ),
    #("SWAP", mgate.Swap),
    #("CH", CH),
    #("2 qubits dense", dense2)
]

nqubits_list = range(4, 28)


def benchfunc(circuit, state):
    circuit.update_quantum_state(state)
    scaluqbase.synchronize()

def create_params(gates: list[tuple[str, Callable[..., scaluq.Gate]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

'''
single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = scaluq.Circuit(nqubits)
    for _ in range(nqubits-1):
        for i in range(nqubits):
            circuit.add_gate(factory(i))
    state = scaluq.StateVector.Haar_random_state(nqubits)
    benchmark(benchfunc, circuit, state)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = scaluq.Circuit(nqubits)
    for _ in range(nqubits-1):
        for i in range(nqubits):
            circuit.add_gate(factory(i, random.random() * math.pi * 2))
    state = scaluq.StateVector.Haar_random_state(nqubits)
    benchmark(benchfunc, circuit, state)
'''

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    circuit = scaluq.Circuit(nqubits)
    for t1 in range(nqubits):
        for t2 in range(nqubits):
            if t1 == t2: continue
            circuit.add_gate(factory(t1, t2))
    state = scaluq.StateVector.Haar_random_state(nqubits)
    benchmark(benchfunc, circuit, state)
