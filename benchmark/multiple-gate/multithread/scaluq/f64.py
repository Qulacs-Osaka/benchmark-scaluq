import pytest
import random
import math
import scaluq as scaluqbase
import scaluq.default.f64 as scaluq
import scaluq.default.f64.gate as mgate

nqubits_list = list(range(4, 28))

def niter_for(nqubits):
    # Repeat the layer many times for cheap small states and few times for
    # expensive large states, keeping each timed call's total work roughly
    # bounded. Many repeats at small nqubits amortize the fixed per-call cost
    # (synchronize(), the Python loop), so the per-gate value stays stable and
    # matches the original measurement; few repeats at large nqubits keep the
    # sweep fast. plot.py divides by the recorded niter, so the per-gate value
    # is unchanged by this choice.
    return max(1, min(100, 2 ** max(0, 18 - nqubits)))

def benchfunc(circuit, state, niter):
    for _ in range(niter):
        circuit.update_quantum_state(state, {})
    scaluqbase.synchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    niter = niter_for(nqubits)
    benchmark.extra_info["niter"] = niter
    circuit = scaluq.Circuit()
    for i in range(nqubits):
        circuit.add_gate(mgate.CX(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = scaluq.StateVector(nqubits)
    benchfunc(circuit, state, niter)  # warmup
    benchmark(benchfunc, circuit, state, niter)
