import pytest
import random
import scaluq.default.f64.gate as mgate # only used for prepare matrix
import math
import numpy as np
import cupy as cp
import cuquantum
import cuquantum.bindings.custatevec as custatevec
import atexit

dtype = cp.complex128
dtype_cuquantum = cuquantum.cudaDataType.CUDA_C_64F
compute_type = custatevec.ComputeType.COMPUTE_64F

def init_state(nqubits):
    vec = [0]*(2**nqubits)
    vec[0] = 1
    return cp.array(vec, dtype=dtype)

nqubits_list = list(range(4, 28))

handle = custatevec.create()
atexit.register(lambda: custatevec.destroy(handle))

def benchfunc(nqubits, state, xgate, rxgates, rzgates, exptr, exsz):
    for _ in range(100):
        for i in range(nqubits):
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, xgate, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [i], 1, [(i+1) % nqubits], [1], 1, compute_type, exptr, exsz)
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, rxgates[i], dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [i], 1, [], [], 0, compute_type, exptr, exsz)
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, rzgates[i], dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [i], 1, [], [], 0, compute_type, exptr, exsz)
    cp.cuda.runtime.deviceSynchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    benchmark.group = 'circuit'
    state = init_state(nqubits)
    xgate_lst = [[0, 1], [1, 0]]
    xgate = cp.array(xgate_lst, dtype=dtype)
    rxgates = []
    for i in range(nqubits):
        theta = random.uniform(0, math.pi * 2)
        cos = math.cos(theta/2)
        sin = math.sin(theta/2)
        rxgate_lst = [[cos + 0.j, -sin * 1.j], [-sin * 1.j, cos + 0.j]]
        rxgates.append(cp.array(rxgate_lst, dtype=dtype))
    rzgates = []
    for i in range(nqubits):
        theta = random.uniform(0, math.pi * 2)
        cos = math.cos(theta/2)
        sin = math.sin(theta/2)
        rzgate_lst = [[cos - sin * 1.j, 0], [0, cos + sin * 1.j]]
        rzgates.append(cp.array(rzgate_lst, dtype=dtype))

    extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, xgate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 1, compute_type)
    for rxgate in rxgates:
        extra = max(extra, custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, rxgate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 0, compute_type))
    for rzgate in rzgates:
        extra = max(extra, custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, rzgate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 0, compute_type))
    if extra > 0:
        sp = cp.array([0]*extra, dtype=cp.uint8)
        benchmark(benchfunc, nqubits, state.data.ptr, xgate.data.ptr, [rxgate.data.ptr for rxgate in rxgates], [rzgate.data.ptr for rzgate in rzgates], sp.data.ptr, extra)
    else:
        benchmark(benchfunc, nqubits, state.data.ptr, xgate.data.ptr, [rxgate.data.ptr for rxgate in rxgates], [rzgate.data.ptr for rzgate in rzgates], 0, extra)
