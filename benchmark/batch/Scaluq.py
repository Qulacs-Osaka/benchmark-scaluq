import pytest
import numpy as np

from scaluq.default.f64 import QuantumCircuit
from scaluq.default.f64.gate import CX, ParametricRX, ParametricRZ

n_qubits = 5
LENGTH = 100

# TODO: パラメータの異なる同じ回路を実行する関数を用意


# 論理：n_batch個の回路を使って状態ベクトルを更新する
# 実際：1つの回路を用意して異なるパラメータでゲート列を実行
def create_circuit(n_batch: int, depth: int, n_batch: int) -> QuantumCircuit:
    params = None
    circuit = QuantumCircuit(n_qubits, n_batch)
    for _ in range(depth):
        for i in range(n_qubits):
            circuit.add_gate(CX(i, (i + 1) % n_qubits))
            circuit.add_gate(ParametricRX(i))
            circuit.add_gate(ParametricRZ(i))
    return circuit


# 実際はpytestで実行できる関数を用意、以下は実験用
def main(n_qubits: int, depth: int, n_batch: int):
    circuit = create_circuit(n_qubits, depth, n_batch)
    rng = np.random.default_rng(12345)
    xs = rng.random(LENGTH)
    ys = rng.random(LENGTH)
    params = None
    circuit.update(params)
