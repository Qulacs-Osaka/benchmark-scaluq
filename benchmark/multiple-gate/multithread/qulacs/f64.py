import pytest
import random
import math
import qulacs
import qulacs.gate as mgate

nqubits_list = list(range(4, 28))

# See multithread/scaluq/f64.py: keep the per-call repeat count small so the
# sweep stays fast; plot.py divides by niter so the per-gate value is unchanged.
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
