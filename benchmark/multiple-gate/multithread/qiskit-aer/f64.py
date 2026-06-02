import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 28))

# Number of times the layer is repeated inside a single circuit / run(). Putting
# the repetitions into one circuit and running it once means the
# job-orchestration and the single device->host (save_statevector) copy are
# amortized over all gate applications instead of paid per layer. Use many
# layers for cheap small states and fewer for expensive large states (with a
# floor so the per-run overhead stays well-amortized). plot.py divides by this
# count, so the per-gate value is unchanged.
def nlayers_for(nqubits):
    return max(10, min(100, 2 ** max(0, 18 - nqubits)))

def transpile_on_cpu(qc):
    backend = AerSimulator(
        method="statevector",
        device="CPU",
        precision="double",
        fusion_enable=False,
        max_job_size=1,
        max_parallel_experiments=1,
        max_parallel_shots=1,
        # default threshold is 14 (<=14 qubits run single-threaded, which shows
        # up as a step between 14 and 15 qubits). Aer treats 0 as "auto" and
        # falls back to 14, so set it to 1: gate application is OpenMP-parallel
        # at every qubit count, matching Scaluq's always-on OpenMP.
        statevector_parallel_threshold=1,
    )
    return backend, transpile(qc, backend, optimization_level=0)

def benchfunc(backend, qc):
    backend.run(qc).result()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    nlayers = nlayers_for(nqubits)
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
    backend, tqc = transpile_on_cpu(qc)
    benchfunc(backend, tqc)  # warmup
    benchmark(benchfunc, backend, tqc)
