import pytest
import numpy as np

from scaluq.default.f64 import QuantumCircuit, BatchedStateVector
from scaluq.default.f64.gate import CX, ParametricRX, ParametricRZ

n_qubits = 5

# 論理的にはn_batch個の回路を使って状態ベクトルを更新する関数
# 実際は1つの回路を用意して異なるパラメータでゲート列を実行
def create_circuit(
    n_qubits: int, n_layers: int, n_batch: int
) -> tuple[QuantumCircuit, dict]:
    params = dict()
    rng = np.random.default_rng(12345)
    cnt = 0
    circuit = QuantumCircuit(n_qubits, n_batch)
    for _ in range(n_layers):
        for i in range(n_qubits):
            circuit.add_gate(CX(i, (i + 1) % n_qubits))
            circuit.add_gate(ParametricRX(i))
            circuit.add_gate(ParametricRZ(i))
            xs = rng.random(n_batch)
            zs = rng.random(n_batch)
            xname = "X" + "_" + str(cnt)
            zname = "Z" + "_" + str(cnt)
            cnt += 1
            params[xname] = xs
            params[zname] = zs
    return (circuit, params)

# 同じ形で異なるパラメータの回路を適用させる
def bench(n_qubits: int, n_layers: int, n_batch: int):
    circuit, params = create_circuit(n_qubits, n_layers, n_batch)
    batched_state = BatchedStateVector(n_qubits, n_batch)
    circuit.update(batched_state, params)
