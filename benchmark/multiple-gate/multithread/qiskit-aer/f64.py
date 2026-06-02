import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 28))

# Number of times the layer is repeated inside a single circuit / run().
# Other libraries apply the layer 100 times in an in-place loop; here we put the
# 100 repetitions into one circuit and run it once, so the job-orchestration and
# device->host (save_statevector) overhead is paid once and amortized over all
# gate applications instead of once per layer.
nlayers = 100

def transpile_on_cpu(qc):
    backend = AerSimulator(
        method="statevector",
        device="CPU",
        precision="double",
        fusion_enable=False,
        max_job_size=1,
        max_parallel_experiments=1,
        max_parallel_shots=1,
        # default threshold is 14 (<=14 qubits run single-threaded); set to 0 so
        # statevector gate application is OpenMP-parallel at every qubit count,
        # matching Scaluq's always-on OpenMP.
        statevector_parallel_threshold=0,
    )
    return backend, transpile(qc, backend, optimization_level=0)

def benchfunc(backend, qc):
    backend.run(qc).result()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    rxthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    rzthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    qc = QuantumCircuit(nqubits)
    for _ in range(nlayers):
        for i in range(nqubits):
            qc.cx(i, (i+1) % nqubits)
            qc.rx(rxthetas[i], i)
            qc.rz(rzthetas[i], i)
    qc.save_statevector()
    backend, tqc = transpile_on_cpu(qc)
    benchfunc(backend, tqc)  # warmup
    benchmark(benchfunc, backend, tqc)
