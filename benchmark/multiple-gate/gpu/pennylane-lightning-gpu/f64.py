import os
import pytest
import random
import math
import pennylane as qml
from pennylane.tape import QuantumScript

# PennyLane Lightning-GPU device (cuStateVec-backed).
device_name = "lightning.gpu"

nqubits_list = list(range(4, int(os.environ.get("NQUBITS_MAX", "27")) + 1))


def nlayers_for(nqubits):
    # Each dev.execute re-initializes |0> and re-applies all gates, so put many
    # layer repetitions into one execution to amortize the per-execution
    # overhead. plot.py divides by this recorded count.
    return max(10, min(100, 2 ** max(0, 18 - nqubits)))


def make_tape(nqubits, nlayers, rxthetas, rzthetas):
    ops = []
    for _ in range(nlayers):
        for i in range(nqubits):
            ops.append(qml.CNOT(wires=[i, (i + 1) % nqubits]))
            ops.append(qml.RX(rxthetas[i], wires=i))
            ops.append(qml.RZ(rzthetas[i], wires=i))
    # scalar expectation -> full gate evolution without a 2**n host copy
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
    benchfunc(dev, tape)  # warmup (CUDA context / kernel init)
    benchmark(benchfunc, dev, tape)
