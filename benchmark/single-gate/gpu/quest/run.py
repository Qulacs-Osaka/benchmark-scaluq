import pytest
import itertools
import random
from scipy.stats import unitary_group
import math
from typing import Callable
import scaluq.default.f64.gate as mgate # only used to get a matrix
import pyquest
import pyquest.unitaries as unitaries

single_gates = [
    ("X", unitaries.X),
    ("Y", unitaries.Y),
    ("Z", unitaries.Z),
    ("H", unitaries.H),
    ("S", unitaries.S),
    ("Sdag", lambda target: unitaries.U(matrix=mgate.Sdag(0).get_matrix(), target=target)),
    ("T", unitaries.T),
    ("Sdag", lambda target: unitaries.U(matrix=mgate.Tdag(0).get_matrix(), target=target)),
]
single_angle_gates = [
    ("RX", unitaries.Rx),
    ("RY", unitaries.Ry),
    ("RZ", unitaries.Rz)
]

def CH(c, t):
    return unitaries.U(matrix=mgate.H(0).get_matrix(), target=t, controls=[c])

def dense2(t1, t2):
    mat = unitary_group.rvs(4)
    return unitaries.U(matrix=mat, targets=[t1, t2])

double_gates = [
    ("CX", lambda control, target: unitaries.X(target, controls=[control])),
    ("CZ", lambda control, target: unitaries.Z(target, controls=[control])),
    ("SWAP", lambda t1, t2: unitaries.Swap(targets=[t1, t2])),
    ("CH", CH),
    ("2 qubits dense", dense2)
]

nqubits_list = range(4, 20)


def benchfunc(op, reg):
    reg.apply_operator(op)

def create_params(gates: list[tuple[str, Callable[..., pyquest.BaseOperator]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    gate = factory(random.randint(0, nqubits - 1))
    state = pyquest.Register(nqubits)
    benchmark(benchfunc, gate, state)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    gate = factory(random.randint(0, nqubits - 1), random.random() * math.pi * 2)
    state = pyquest.Register(nqubits)
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
    state = pyquest.Register(nqubits)
    benchmark(benchfunc, gate, state)
