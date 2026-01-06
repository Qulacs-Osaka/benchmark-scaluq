import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 28))

def transpile_on_cpu(qc):
    backend = AerSimulator(method="statevector", device="CPU", precision="double", fusion_enable=False, max_job_size=1)
    return backend, transpile(qc, backend, optimization_level=0)

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
    benchmark(benchfunc, *transpile_on_cpu(qc))
