import pytest
import itertools
import random
from scipy.stats import unitary_group
import math
from typing import Callable
from qiskit import QuantumCircuit
from qiskit.circuit.library import UnitaryGate
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

single_gates = [
    ("X", lambda target, qc: qc.x(target)),
    ("Y", lambda target, qc: qc.y(target)),
    ("Z", lambda target, qc: qc.z(target)),
    ("H", lambda target, qc: qc.h(target)),
    ("S", lambda target, qc: qc.s(target)),
    ("Sdag", lambda target, qc: qc.sdg(target)),
    ("T", lambda target, qc: qc.t(target)),
    ("Tdag", lambda target, qc: qc.tdg(target)),
]
single_angle_gates = [
    ("RX", lambda target, angle, qc: qc.rx(angle, target)),
    ("RY", lambda target, angle, qc: qc.ry(angle, target)),
    ("RZ", lambda target, angle, qc: qc.rz(angle, target)),
]

def dense2(t1, t2, qc):
    mat = unitary_group.rvs(4)
    return qc.append(UnitaryGate(mat), [t1, t2])

double_gates = [
    ("CX", lambda control, target, qc: qc.cx(control, target)),
    #("CZ", lambda control, target, qc: qc.cz(control, target)),
    #("SWAP", lambda control, target, qc: qc.swap(control, target)),
    #("CH", lambda control, target, qc: qc.ch(control, target)),
    #("2 qubits dense", dense2)
]

nqubits_list = range(4, 26)

def transpile_on_gpu(qc):
    backend = AerSimulator(method="statevector", device="GPU", cuStateVec_enable=True)
    return backend, transpile(qc, backend)

def benchfunc(backend, qc):
    backend.run(qc, shots=1).result()

def create_params(gates: list[tuple[str, Callable[..., QuantumCircuit]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

'''
single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    for __ in range(100):
        for _ in range(nqubits-1):
            for i in range(nqubits):
                factory(i, qc)
    benchmark(benchfunc, *transpile_on_gpu(qc))

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    for __ in range(100):
        for _ in range(nqubits-1):
            for i in range(nqubits):
                factory(i, random.random() * math.pi * 2, qc)
    benchmark(benchfunc, *transpile_on_gpu(qc))
    '''

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    for __ in range(100):
        for t1 in range(nqubits):
            for t2 in range(nqubits):
                if t1 == t2:
                    continue
                factory(t1, t2, qc)
    benchmark(benchfunc, *transpile_on_gpu(qc))
