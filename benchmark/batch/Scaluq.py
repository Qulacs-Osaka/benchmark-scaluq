import pytest
import numpy as np

from scaluq.default.f64 import QuantumCircuit, BatchedStateVector
from scaluq.default.f64.gate import CX, ParametricRX, ParametricRZ

n_qubits = 5
PARAMETRICX_NAME = "paramx"
PARAMETRICZ_NAME = "paramz"


# TODO: パラメータの異なる同じ回路を実行する関数を用意
def execute_circuits(n_qubits: int, depth: int, n_batch: int):
    circuit = create_circuit(n_qubits, depth, n_batch)
    state = BatchedStateVector(n_qubits, n_batch)


# 論理：n_batch個の回路を使って状態ベクトルを更新する
# 実際：1つの回路を用意して異なるパラメータでゲート列を実行
def create_circuit(
    n_qubits: int, depth: int, n_batch: int
) -> tuple[QuantumCircuit, dict]:
    params = dict()
    rng = np.random.default_rng(12345)
    cnt = 0
    circuit = QuantumCircuit(n_qubits, n_batch)
    for _ in range(depth):
        for i in range(n_qubits):
            circuit.add_gate(CX(i, (i + 1) % n_qubits))
            circuit.add_gate(ParametricRX(i))
            circuit.add_gate(ParametricRZ(i))
            xs = rng.random(n_batch)
            zs = rng.random(n_batch)
            xname = PARAMETRICX_NAME + "_" + str(cnt)
            zname = PARAMETRICZ_NAME + "_" + str(cnt)
            cnt += 1
            params[xname] = xs
            params[zname] = zs
    return circuit


# 実際はpytestで実行できる関数を用意、以下は実験用
def main(n_qubits: int, depth: int, n_batch: int):
    circuit, params = create_circuit(n_qubits, depth, n_batch)
    batched_state = BatchedStateVector(n_qubits, n_batch)
    circuit.update(batched_state, params)
