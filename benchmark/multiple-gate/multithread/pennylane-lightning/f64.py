import os
import pytest
import random
import math
import pennylane as qml
from pennylane.tape import QuantumScript

# PennyLane Lightning device. lightning.qubit uses OpenMP-parallel gate kernels
# on CPU by default and honors OMP_NUM_THREADS (set in exec.sh before the Python
# process starts, since the runtime initializes on import).
device_name = "lightning.qubit"

nqubits_list = list(range(4, int(os.environ.get("NQUBITS_MAX", "27")) + 1))


def nlayers_for(nqubits):
    # Like Qiskit-Aer, each dev.execute re-initializes |0> and re-applies all
    # gates, so we put many layer repetitions into one tape/execution to amortize
    # the per-execution overhead. Many layers for cheap small states, fewer (with
    # a floor) for expensive large ones. plot.py divides by this recorded count.
    return max(10, min(100, 2 ** max(0, 18 - nqubits)))


def make_tape(nqubits, nlayers, rxthetas, rzthetas):
    ops = []
    for _ in range(nlayers):
        for i in range(nqubits):
            ops.append(qml.CNOT(wires=[i, (i + 1) % nqubits]))
            ops.append(qml.RX(rxthetas[i], wires=i))
            ops.append(qml.RZ(rzthetas[i], wires=i))
    # A scalar expectation forces full gate evolution but avoids copying the
    # 2**n statevector back to host (which qml.state() would do).
    return QuantumScript(ops, [qml.expval(qml.PauliZ(0))])


def benchfunc(dev, tape):
    dev.execute(tape)


@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    nlayers = nlayers_for(nqubits)
    benchmark.extra_info["niter"] = nlayers
    rxthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    rzthetas = [random.uniform(0, math.pi * 2) for _ in range(nqubits)]
    dev = qml.device(device_name, wires=nqubits)
    tape = make_tape(nqubits, nlayers, rxthetas, rzthetas)
    benchfunc(dev, tape)  # warmup
    benchmark(benchfunc, dev, tape)
