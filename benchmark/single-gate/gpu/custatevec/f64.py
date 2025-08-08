import pytest
import itertools
import random
from scipy.stats import unitary_group
import scaluq.default.f64 as scaluq # only used for prepare vector
import scaluq.default.f64.gate as mgate # only used for prepare matrix
import math
from typing import Callable
import numpy as np
import cupy as cp
import cuquantum.bindings.custatevec as custatevec
import sys
import atexit

dtype = cp.complex128
compute_type = custatevec.ComputeType.COMPUTE_64F

single_gates = [
    ("X", lambda: mgate.X(0).get_matrix()),
    ("Y", lambda: mgate.Y(0).get_matrix()),
    ("Z", lambda: mgate.Z(0).get_matrix()),
    ("H", lambda: mgate.H(0).get_matrix()),
    ("S", lambda: mgate.S(0).get_matrix()),
    ("Sdag", lambda: mgate.Sdag(0).get_matrix()),
    ("T", lambda: mgate.T(0).get_matrix()),
    ("Tdag", lambda: mgate.Tdag(0).get_matrix()),
]
single_angle_gates = [
    ("RX", lambda angle: mgate.RX(0, angle).get_matrix()),
    ("RY", lambda angle: mgate.RY(0, angle).get_matrix()),
    ("RZ", lambda angle: mgate.RZ(0, angle).get_matrix()),
]

def dense2():
    mat = unitary_group.rvs(4)
    return mat

def controlled(mat):
    ret = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    for i in range(2):
        for j in range(2):
            ret[2+i][2+j] = mat[i][j]
    return ret

double_gates = [
    ("CX", lambda: controlled(mgate.X(0).get_matrix())),
    ("CZ", lambda: controlled(mgate.Z(0).get_matrix())),
    ("SWAP", lambda: [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]),
    ("CH", lambda: controlled(mgate.H(0).get_matrix())),
    ("2 qubits dense", dense2)
]

def random_state(nqubits):
    vec = scaluq.StateVector.Haar_random_state(nqubits).get_vector()
    return cp.array(vec, dtype=dtype)

nqubits_list = range(4, 20)

handle = custatevec.create()
atexit.register(lambda: custatevec.destroy(handle))

def benchfunc(nqubits, state, gate, targets, controls=[]):
    custatevec.apply_matrix(handle, state, dtype, nqubits, gate, dtype, custatevec.MatrixLayout.ROW, 0, targets, len(targets), controls, [1], len(controls), computeType, None, 0)

def create_params(gates: list[tuple[str, Callable[..., list[list[int]]]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    benchmark(benchfunc, nqubits, random_state(nqubits), cp.array(factory(), dtype=dtype), [random.randint(0, nqubits - 1)])

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    benchmark(benchfunc, nqubits, random_state(nqubits), cp.array(factory(random.random(), math.pi * 2), dtype=dtype), [random.randint(0, nqubits - 1)])

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    t1 = random.randint(0, nqubits - 1)
    t2 = random.randint(0, nqubits - 2)
    if(t2 == t1):
        t2 = nqubits - 1
    benchmark(benchfunc, nqubits, random_state(nqubits), cp.array(factory(), dtype=dtype), [t1, t2])
