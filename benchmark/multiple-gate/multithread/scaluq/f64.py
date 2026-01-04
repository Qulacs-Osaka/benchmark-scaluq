import pytest
import random
import math
import scaluq as scaluqbase
import scaluq.default.f64 as scaluq
import scaluq.default.f64.gate as mgate

nqubits_list = list(range(4, 28))

def benchfunc(circuit, state):
    for _ in range(100):
        circuit.update_quantum_state(state, {})
    scaluqbase.synchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    benchmark.group = 'circuit'
    circuit = scaluq.Circuit(nqubits)
    for i in range(nqubits):
        circuit.add_gate(mgate.CX(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = scaluq.StateVector(nqubits)
    benchmark(benchfunc, circuit, state)
