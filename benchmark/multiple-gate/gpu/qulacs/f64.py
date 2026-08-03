import pytest
import random
import math
import qulacs
import qulacs.gate as mgate

nqubits_list = list(range(4, 28))

# Repetitions per timed call (recorded so plot.py normalizes per gate).
niter = 100

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
    state = qulacs.StateVectorGpu(nqubits)
    benchfunc(circuit, state)  # warmup
    benchmark(benchfunc, circuit, state)
