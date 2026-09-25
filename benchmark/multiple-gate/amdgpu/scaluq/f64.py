import pytest
import random
import math
import scaluq as scaluqbase
from scaluq import StateVector, Circuit
from scaluq import gate
prec = 'f64'
space = 'default'

nqubits_list = list(range(4, 28))

# Repetitions per timed call (recorded so plot.py normalizes per gate). Kept
# high on GPU to amortize kernel-launch latency before the single synchronize.
niter = 100

def benchfunc(circuit, state):
    for _ in range(niter):
        # pass a fixed seed (3rd arg) so the default std::random_device read is
        # avoided each call (requires the seed-handling fix in scaluq 025565d)
        circuit.update_quantum_state(state, {}, 0)
    scaluqbase.synchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = niter
    circuit = Circuit()
    for i in range(nqubits):
        circuit.add_gate(gate.CX(i, (i+1) % nqubits, precision=prec))
        circuit.add_gate(gate.RX(i, random.uniform(0, math.pi * 2), precision=prec))
        circuit.add_gate(gate.RZ(i, random.uniform(0, math.pi * 2), precision=prec))
    state = StateVector(nqubits, precision=prec, space=space)
    benchfunc(circuit, state)  # warmup
    benchmark(benchfunc, circuit, state)
