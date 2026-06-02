import os
import pytest
import random
import math
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

nqubits_list = list(range(4, 28))

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
        # NOTE: Aer's default statevector_parallel_threshold=14 makes <=14 qubits
        # run single-threaded (very fast here, ~0.02 ms/gate) and >=15 qubits run
        # multi-threaded (~9 ms/gate, dominated by OpenMP fork/join overhead on a
        # high-core machine), producing a step between 14 and 15 qubits. Forcing
        # it on (threshold=1) removes the step but makes <=14 qubits ~200x slower,
        # so the threading policy is better controlled via OMP_NUM_THREADS (see
        # exec.sh) than by forcing this threshold.
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
