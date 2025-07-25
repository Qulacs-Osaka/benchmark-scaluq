import pytest
import itertools
import random
from scipy.stats import unitary_group
import math
from typing import Callable
from qiskit import QuantumCircuit
from qiskit.quantum_info import random_statevector
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
    ("CZ", lambda control, target, qc: qc.cz(control, target)),
    ("SWAP", lambda control, target, qc: qc.swap(control, target)),
    ("CH", lambda control, target, qc: qc.ch(control, target)),
    ("2 qubits dense", dense2)
]

nqubits_list = range(4, 20)


def benchfunc(qc):
    backend = AerSimulator(method="statevector")
    qc = transpile(qc, backend)
    backend.run(qc, shots=1).result()

def create_params(gates: list[tuple[str, Callable[..., QuantumCircuit]]]):
    return map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(gates, nqubits_list))

single_params = create_params(single_gates)
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    qc.initialize(random_statevector(2**nqubits), list(range(nqubits)))
    factory(random.randint(0, nqubits - 1), qc)
    benchmark(benchfunc, qc)

single_angle_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_angle_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], single_angle_params)
def test_SingleAngle(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    qc.initialize(random_statevector(2**nqubits), list(range(nqubits)))
    factory(random.randint(0, nqubits - 1), random.random() * math.pi * 2, qc)
    benchmark(benchfunc, qc)

double_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(double_gates, nqubits_list))
@pytest.mark.parametrize(["name", "factory", "nqubits"], double_params)
def test_Double(benchmark, name, factory, nqubits):
    benchmark.group = name
    qc = QuantumCircuit(nqubits)
    qc.initialize(random_statevector(2**nqubits), list(range(nqubits)))
    t1 = random.randint(0, nqubits - 1)
    t2 = random.randint(0, nqubits - 2)
    if(t2 == t1):
        t2 = nqubits - 1
    factory(t1, t2, qc)
    benchmark(benchfunc, qc)
