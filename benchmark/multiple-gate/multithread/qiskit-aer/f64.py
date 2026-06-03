import os
import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

# Upper qubit count (inclusive); lowered to 18 by the single-thread run.
nqubits_list = list(range(4, int(os.environ.get("NQUBITS_MAX", "27")) + 1))

# Match the thread count used by the OpenMP-based libraries (set via
# OMP_NUM_THREADS in exec.sh); 0 lets Aer use all cores.
max_parallel_threads = int(os.environ.get("OMP_NUM_THREADS", "0"))

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
        max_parallel_threads=max_parallel_threads,
        # Force OpenMP gate application at every qubit count, matching Scaluq's
        # and Qulacs' always-on parallelism (Aer's default threshold of 14 would
        # otherwise run <=14 qubits single-threaded, creating a step at 14/15).
        # In the single-thread run OMP_NUM_THREADS=1 -> max_parallel_threads=1,
        # so this stays effectively serial there. (This was briefly removed
        # because, when oversubscribing 64 hyperthreads, forced parallelism made
        # small circuits ~200x slower; pinning OMP_NUM_THREADS to 32 physical
        # cores removed that pathology, so it is cheap again.)
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
