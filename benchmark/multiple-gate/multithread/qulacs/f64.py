import pytest
import random
import math
import qulacs
import qulacs.gate as mgate

nqubits_list = list(range(4, 28))

def niter_for(nqubits):
    # See multithread/scaluq/f64.py: many repeats for cheap small states (stable
    # per-gate value), few repeats for expensive large states (fast sweep).
    # plot.py divides by the recorded niter so the per-gate value is unchanged.
    return max(1, min(100, 2 ** max(0, 18 - nqubits)))

def benchfunc(circuit, state, niter):
    for _ in range(niter):
        circuit.update_quantum_state(state)

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    niter = niter_for(nqubits)
    benchmark.extra_info["niter"] = niter
    circuit = qulacs.QuantumCircuit(nqubits)
    for i in range(nqubits):
        circuit.add_gate(mgate.CNOT(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = qulacs.StateVector(nqubits)
    benchfunc(circuit, state, niter)  # warmup
    benchmark(benchfunc, circuit, state, niter)
