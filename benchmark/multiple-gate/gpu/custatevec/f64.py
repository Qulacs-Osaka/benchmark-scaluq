import pytest
import random
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
    vec = cp.zeros(2**nqubits, dtype=dtype)
    vec[0] = 1
    return vec

nqubits_list = list(range(4, 28))

# Repetitions per timed call (recorded so plot.py normalizes per gate).
niter = 100

handle = custatevec.create()
atexit.register(lambda: custatevec.destroy(handle))

def benchfunc(nqubits, state, xgate, rxthetas, rzthetas, exptr, exsz):
    for _ in range(niter):
        for i in range(nqubits):
            # CX(control=i, target=(i+1)%n): controlled dense X matrix
            custatevec.apply_matrix(handle, state, dtype_cuquantum, nqubits, xgate, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, [(i+1) % nqubits], 1, [i], [1], 1, compute_type, exptr, exsz)
            # RX(theta) = exp(-i theta/2 X); apply_pauli_rotation applies exp(i theta P)
            custatevec.apply_pauli_rotation(handle, state, dtype_cuquantum, nqubits, -rxthetas[i] / 2, [custatevec.Pauli.X], [i], 1, [], [], 0)
            # RZ(theta) = exp(-i theta/2 Z)
            custatevec.apply_pauli_rotation(handle, state, dtype_cuquantum, nqubits, -rzthetas[i] / 2, [custatevec.Pauli.Z], [i], 1, [], [], 0)
    cp.cuda.runtime.deviceSynchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = niter
    state = init_state(nqubits)
    xgate_lst = [[0, 1], [1, 0]]
    xgate = cp.array(xgate_lst, dtype=dtype)
    rxthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    rzthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]

    # only the CX (apply_matrix) path may require workspace; pauli rotation needs none
    extra = custatevec.apply_matrix_get_workspace_size(handle, dtype_cuquantum, nqubits, xgate.data.ptr, dtype_cuquantum, custatevec.MatrixLayout.ROW, 0, 1, 1, compute_type)
    if extra > 0:
        sp = cp.array([0]*extra, dtype=cp.uint8)
        exptr = sp.data.ptr
    else:
        exptr = 0
    args = (nqubits, state.data.ptr, xgate.data.ptr, rxthetas, rzthetas, exptr, extra)
    benchfunc(*args)  # warmup (CUDA context / kernel init)
    benchmark(benchfunc, *args)
