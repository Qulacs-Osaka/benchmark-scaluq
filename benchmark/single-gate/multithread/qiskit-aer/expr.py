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

nqubits = 16
qc = QuantumCircuit(nqubits)
qc.initialize(random_statevector(2**nqubits), list(range(nqubits)))
'''
for __ in range(100):
    for t1 in range(nqubits):
        for t2 in range(nqubits):
            if t1 == t2:
                continue
            qc.cx(t1, t2)
'''
qc.save_statevector()
backend = AerSimulator(method="statevector", device="GPU", cuStateVec_enable=True)
qcc = transpile(qc, backend)
print(qc.size())
print(qcc.size())
print(backend.run(qcc, shots=1).result())
