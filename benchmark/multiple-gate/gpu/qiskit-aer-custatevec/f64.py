import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 26))

def transpile_on_gpu(qc):
    backend = AerSimulator(method="statevector", device="GPU", precision="double", cuStateVec_enable=True)
    return backend, transpile(qc, backend)

def benchfunc(backend, qc):
    for _ in range(100):
        backend.run(qc).result()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    benchmark.group = 'circuit'
    qc = QuantumCircuit(nqubits)
    for i in range(nqubits):
        qc.cx(i, (i+1) % nqubits)
        qc.rx(random.uniform(0, math.pi * 2), i)
        qc.rz(random.uniform(0, math.pi * 2), i)
    qc.save_statevector()
    benchmark(benchfunc, *transpile_on_gpu(qc))
