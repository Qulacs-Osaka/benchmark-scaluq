import pytest
import random
import math
import scaluq as scaluqbase
import scaluq.default.f64 as scaluq
import scaluq.default.f64.gate as mgate

nqubits_list = list(range(4, 28))

# Number of times the layer is applied per timed call. Kept small because
# Scaluq forces OpenMP, so even tiny states pay the thread fork/join cost on
# every gate; a large repeat count makes the whole sweep take hours without
# changing the per-gate value (plot.py divides by niter).
niter = 10

def benchfunc(circuit, state):
    for _ in range(niter):
        circuit.update_quantum_state(state, {})
    scaluqbase.synchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = niter
    circuit = scaluq.Circuit()
    for i in range(nqubits):
        circuit.add_gate(mgate.CX(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = scaluq.StateVector(nqubits)
    benchfunc(circuit, state)  # warmup
    benchmark(benchfunc, circuit, state)
