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
import cuquantum
import cuquantum.bindings.custatevec as custatevec
import sys
import atexit

dtype = cp.complex64
dtype_cuquantum = cuquantum.cudaDataType.CUDA_C_32F
compute_type = custatevec.ComputeType.COMPUTE_32F

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
    ("CX", lambda: mgate.X(0).get_matrix()),
    #("CZ", lambda: mgate.Z(0).get_matrix()),
    #("SWAP", lambda: [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]),
    #("CH", lambda: mgate.H(0).get_matrix()),
    #("2 qubits dense", dense2)
]

def random_state(nqubits):
    vec = scaluq.StateVector.Haar_random_state(nqubits).get_amplitudes()
    return cp.array(vec, dtype=dtype)

nqubits_list = range(4, 28)

handle = custatevec.create()
atexit.register(lambda: custatevec.destroy(handle))

def benchfunc_t1(nqubits, state, gate, exptr, exsz):
    for _ in range(nqubits-1):
        for i in range(nqubits):
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, gate, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [i], 1, [], [], 0, compute_type, exptr, exsz)
    cp.cuda.runtime.deviceSynchronize()

def benchfunc_t2(nqubits, state, gate, exptr, exsz):
    for t1 in range(nqubits):
        for t2 in range(nqubits):
            if t1 == t2: continue
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, gate, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [t1, t2], 2, [], [], 0, compute_type, exptr, exsz)
    cp.cuda.runtime.deviceSynchronize()

def benchfunc_t1c1(nqubits, state, gate, exptr, exsz):
    for t in range(nqubits):
        for c in range(nqubits):
            if t == c: continue
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, gate, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [t], 1, [c], [1], 1, compute_type, exptr, exsz)
    cp.cuda.runtime.deviceSynchronize()

def create_params(gates: list[tuple[str, Callable[..., list[list[int]]]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

'''
single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    state = random_state(nqubits)
    gate_lst = [x for row in factory() for x in row]
    gate = cp.array(gate_lst, dtype=dtype)
    extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, gate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 0, compute_type)
    if extra > 0:
        sp = cp.array([0]*extra, dtype=cp.uint8)
        benchmark(benchfunc_t1, nqubits, state.data.ptr, gate.data.ptr, sp.data.ptr, extra)
    else:
        benchmark(benchfunc_t1, nqubits, state.data.ptr, gate.data.ptr, 0, extra)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    state = random_state(nqubits)
    gate_lst = [x for row in factory(random.random() * math.pi * 2) for x in row]
    gate = cp.array(gate_lst, dtype=dtype)
    extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, gate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 0, compute_type)
    if extra > 0:
        sp = cp.array([0]*extra, dtype=cp.uint8)
        benchmark(benchfunc_t1, nqubits, state.data.ptr, gate.data.ptr, sp.data.ptr, extra)
    else:
        benchmark(benchfunc_t1, nqubits, state.data.ptr, gate.data.ptr, 0, extra)
'''

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    state = random_state(nqubits)
    gate_lst = [x for row in factory() for x in row]
    gate = cp.array(gate_lst, dtype=dtype)
    if name in ["CX", "CZ", "CH"]:
        extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, gate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 1, compute_type)
        if extra > 0:
            sp = cp.array([0]*extra, dtype=cp.uint8)
            benchmark(benchfunc_t1c1, nqubits, state.data.ptr, gate.data.ptr, sp.data.ptr, extra)
        else:
            benchmark(benchfunc_t1c1, nqubits, state.data.ptr, gate.data.ptr, 0, extra)
    else:
        extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, gate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 2, 0, compute_type)
        if extra > 0:
            sp = cp.array([0]*extra, dtype=cp.uint8)
            benchmark(benchfunc_t2, nqubits, state.data.ptr, gate.data.ptr, sp.data.ptr, extra)
        else:
            benchmark(benchfunc_t2, nqubits, state.data.ptr, gate.data.ptr, 0, extra)
