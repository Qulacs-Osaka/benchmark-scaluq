import pytest
import numpy as np
import pennylane as qml

plugin = "lightning.gpu"

nqubits_list = range(4, 26)


def native_execute(benchmark, circuit):
    def evalfunc(circuit):
        circuit()

    benchmark(evalfunc, circuit)


def first_rotation(nqubits, params):
    for i in range(nqubits):
        qml.RX(params[0], i)
        qml.RZ(params[1], i)


def mid_rotation(nqubits, params):
    for i in range(nqubits):
        qml.RZ(params[0], i)
        qml.RX(params[1], i)
        qml.RZ(params[2], i)


def last_rotation(nqubits, params):
    for i in range(nqubits):
        qml.RZ(params[0], i)
        qml.RX(params[1], i)


def entangler(nqubits, pairs):
    for a, b in pairs:
        qml.CNOT(wires=[a, b])


def generate_qcbm_circuit(nqubits, depth, pairs):
    dev = qml.device(plugin, wires=nqubits)

    @qml.qnode(dev)
    def circuit():
        params_first = np.random.rand(2)
        params_mid = np.random.rand(depth - 1, 3)
        params_last = np.random.rand(2)
        first_rotation(nqubits, params_first)
        entangler(nqubits, pairs)
        for k in range(depth - 1):
            mid_rotation(nqubits, params_mid[k])
            entangler(nqubits, pairs)
        last_rotation(nqubits, params_last)
        return qml.state()

    return circuit


@pytest.mark.parametrize("nqubits", nqubits_list)
def test_qcbm_gf_exc(benchmark, nqubits):
    benchmark.group = "QCBMoptexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit)
