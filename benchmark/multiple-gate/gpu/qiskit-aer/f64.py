import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 28))

# See multithread/qiskit-aer/f64.py: the 100 layer repetitions go into one
# circuit and one run(), so orchestration + the single device->host
# save_statevector copy are amortized over all gate applications.
nlayers = 100

def transpile_on_gpu(qc):
    backend = AerSimulator(method="statevector", device="GPU", precision="double", cuStateVec_enable=False, fusion_enable=False)
    return backend, transpile(qc, backend, optimization_level=0)

def benchfunc(backend, qc):
    backend.run(qc).result()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = nlayers
    rxthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    rzthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    qc = QuantumCircuit(nqubits)
    for _ in range(nlayers):
        for i in range(nqubits):
            qc.cx(i, (i+1) % nqubits)
            qc.rx(rxthetas[i], i)
            qc.rz(rzthetas[i], i)
    qc.save_statevector()
    backend, tqc = transpile_on_gpu(qc)
    benchfunc(backend, tqc)  # warmup
    benchmark(benchfunc, backend, tqc)
