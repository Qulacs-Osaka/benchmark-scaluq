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
    ret = mgate.to_matrix_gate(mgate.H(t))
    ret.add_control_qubit(c, 1)
    return ret

def dense2(t1, t2):
    mat = unitary_group.rvs(4)
    return mgate.DenseMatrix([t1, t2], mat)

double_gates = [
    ("CX", mgate.CNOT),
    ("CZ", mgate.CZ),
    ("SWAP", mgate.SWAP),
    ("CH", CH),
    ("2 qubits dense", dense2)
]

nqubits_list = range(4, 20)


def benchfunc(gate, state):
    gate.update_quantum_state(state)

def create_params(gates: list[tuple[str, Callable[..., qulacs.QuantumGateBase]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    gate = factory(random.randint(0, nqubits - 1))
    state = qulacs.StateVector(nqubits)
    state.set_Haar_random_state()
    benchmark(benchfunc, gate, state)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    gate = factory(random.randint(0, nqubits - 1), random.random() * math.pi * 2)
    state = qulacs.StateVector(nqubits)
    state.set_Haar_random_state()
    benchmark(benchfunc, gate, state)

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    t1 = random.randint(0, nqubits - 1)
    t2 = random.randint(0, nqubits - 2)
    if(t2 == t1):
        t2 = nqubits - 1
    gate = factory(t1, t2)
    state = qulacs.StateVector(nqubits)
    state.set_Haar_random_state()
    benchmark(benchfunc, gate, state)
