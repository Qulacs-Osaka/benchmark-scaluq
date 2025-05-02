import pytest
import numpy as np
import pennylane as qml

# --- config ---
max_parallel_threads = 16
gpu = True
plugin = "lightning.gpu" if gpu else "lightning.qubit"

nqubits_list = range(4, 26)

def native_execute(benchmark, circuit):
    def evalfunc(circuit, params):
        circuit(params)
    benchmark(evalfunc, circuit)

def first_rotation(nqubits, params_first):
    qml.RX(params_first[0], range(nqubits))
    qml.RZ(params_first[1], range(nqubits))

def mid_rotation(nqubits, params_mid):
    qml.RZ(params_mid[0], range(nqubits))
    qml.RX(params_mid[1], range(nqubits))
    qml.RZ(params_mid[2], range(nqubits))

def last_rotation(nqubits, params_last):
    qml.RZ(params_last[0], range(nqubits))
    qml.RX(params_last[1], range(nqubits))

def entangler(nqubits, pairs):
    for a, b in pairs:
        qml.CNOT(wires=[a, b])

def generate_qcbm_circuit(nqubits, depth, pairs):
    dev = qml.device(plugin, wires=nqubits)
    @qml.qnode(dev)
    def make_circuit():
        params_first = np.random.rand(2)
        params_mid = np.random.rand(depth-1, 3)
        params_last = np.random.rand(2)
        first_rotation(nqubits, params_first)
        entangler(nqubits, pairs)
        for k in range(depth - 1):
            mid_rotation(nqubits, params_mid[k])
            entangler(nqubits, pairs)
        last_rotation(nqubits, params_last)
        return qml.state()
    circuit = qml.QNode(make_circuit, dev)
    return circuit

@pytest.mark.parametrize('nqubits', nqubits_list)
def test_qcbm_gf_exc(benchmark, nqubits):
    benchmark.group = "QCBMoptexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit)