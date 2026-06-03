import os
import pytest
import random
import math
import qulacs
import qulacs.gate as mgate

# Upper qubit count (inclusive); lowered to 18 by the single-thread run.
nqubits_list = list(range(4, int(os.environ.get("NQUBITS_MAX", "27")) + 1))

# See multithread/scaluq/f64.py: per-gate time is OpenMP-overhead bound and
# independent of niter, so keep niter small to avoid inflating wall-clock time.
niter = 10

def benchfunc(circuit, state):
    for _ in range(niter):
        circuit.update_quantum_state(state)

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = niter
    circuit = qulacs.QuantumCircuit(nqubits)
    for i in range(nqubits):
        circuit.add_gate(mgate.CNOT(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = qulacs.StateVector(nqubits)
    benchfunc(circuit, state)  # warmup
    benchmark(benchfunc, circuit, state)
