# from qiskit_aer import AerSimulator

# simulator = AerSimulator(method='statevector', device='GPU')
# print(simulator.available_devices())



import pytest
import numpy as np
import uuid
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.compiler import transpile

max_parallel_threads = 24
gpu = False
method = "statevector" if not gpu else "statevector_gpu"


def native_execute(benchmark, circuit, include_compile_time):

    simulator = AerSimulator(method='statevector', device='GPU')
    print(simulator.available_devices())

    def evalfunc_include(sim, circuit):
        circuit_transpiled = transpile(circuit, backend=sim)
        result = sim.run(circuit_transpiled).result()
        print(result)

    def evalfunc_exclude(sim, circuit_transpiled):
        sim.run(circuit_transpiled)

    if include_compile_time:
        pass
        # benchmark(evalfunc_include, simulator, circuit)
    else:
        pass
        # circuit_transpiled = transpile(circuit, backend=simulator)
        # benchmark(evalfunc_exclude, simulator, circuit_transpiled)
    
    evalfunc_include(simulator, circuit)


def first_rotation(circuit, nqubits):
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def mid_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    circuit.rz(np.random.rand(), range(nqubits))
    return circuit


def last_rotation(circuit, nqubits):
    circuit.rz(np.random.rand(), range(nqubits))
    circuit.rx(np.random.rand(), range(nqubits))
    return circuit


def entangler(circuit, pairs):
    for a, b in pairs:
        circuit.cx(a, b)
    return circuit


def generate_qcbm_circuit(nqubits, depth, pairs):
    circuit = QuantumCircuit(nqubits)
    first_rotation(circuit, nqubits)
    entangler(circuit, pairs)
    for k in range(depth - 1):
        mid_rotation(circuit, nqubits)
        entangler(circuit, pairs)
    last_rotation(circuit, nqubits)
    return circuit

def main():
    nqubits = 20
    depth = 10
    pairs = [(i, i + 1) for i in range(nqubits - 1)]
    circuit = generate_qcbm_circuit(nqubits, depth, pairs)
    include_compile_time = False

    # Run the benchmark
    benchmark = None  # Replace with actual benchmark object
    native_execute(benchmark, circuit, include_compile_time)

if __name__ == "__main__":
    main()