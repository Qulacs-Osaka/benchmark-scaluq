import pytest
import numpy as np
import uuid
import pennylane as qml
from pennylane import numpy as pnp

max_parallel_threads = 24
gpu = False


def native_execute(benchmark, circuit_func, nqubits, depth, pairs, fusion_enable, include_compile_time):
    # PennyLane-Lightningのオプション設定
    device_options = {
        "c_dtype": np.complex128,  # "double"精度
        "shots": None,             # 状態ベクトルモード（決定論的）
        "parallel": True,
        "threads": max_parallel_threads
    }
    
    if gpu:
        try:
            # GPU利用可能かチェック
            from pennylane_lightning.lightning_gpu import LightningGPU
            device = qml.device('lightning.gpu', wires=nqubits, **device_options)
        except (ImportError, RuntimeError):
            # GPUが利用できない場合はCPUにフォールバック
            print("警告: LightningGPUを利用できないため、LightningCPUを使用します")
            device = qml.device('lightning.qubit', wires=nqubits, **device_options)
    else:
        device = qml.device('lightning.qubit', wires=nqubits, **device_options)
    
    # PennyLaneではゲート融合が内部的に行われるが、
    # lightningバックエンドではコンパイル最適化の設定が一部異なる
    if fusion_enable:
        # ゲート融合を有効化（PennyLaneでは自動的に行われる場合が多い）
        pass
    else:
        # 最適化を無効化するためのオプション
        # 注: 完全に同等の設定はPennyLaneでは異なる場合があります
        pass
    
    @qml.qnode(device)
    def circuit():
        return circuit_func(nqubits, depth, pairs)
    
    if include_compile_time:
        # コンパイル時間を含む測定
        benchmark(circuit)
    else:
        # 一度コンパイルしてから測定
        # PennyLaneでは初回実行時にコンパイルが行われるため、一度実行しておく
        circuit()
        # 実行時間のみを測定
        benchmark(circuit)


def first_rotation(nqubits):
    for i in range(nqubits):
        qml.RX(np.random.rand(), wires=i)
        qml.RZ(np.random.rand(), wires=i)


def mid_rotation(nqubits):
    for i in range(nqubits):
        qml.RZ(np.random.rand(), wires=i)
        qml.RX(np.random.rand(), wires=i)
        qml.RZ(np.random.rand(), wires=i)


def last_rotation(nqubits):
    for i in range(nqubits):
        qml.RZ(np.random.rand(), wires=i)
        qml.RX(np.random.rand(), wires=i)


def entangler(pairs):
    for a, b in pairs:
        qml.CNOT(wires=[a, b])


def generate_qcbm_circuit(nqubits, depth, pairs):
    # PennyLaneでの回路構築関数
    def circuit(nqubits, depth, pairs):
        first_rotation(nqubits)
        entangler(pairs)
        
        for k in range(depth - 1):
            mid_rotation(nqubits)
            entangler(pairs)
            
        last_rotation(nqubits)
        
        # 状態ベクトルを返す
        return qml.state()
    
    return circuit


nqubit_list = range(4, 26)


"""
@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_gf_inc(benchmark, nqubits):
    benchmark.group = "QCBMoptinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit_func = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit_func, nqubits, 9, pairs, fusion_enable=True, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_gf_exc(benchmark, nqubits):
    benchmark.group = "QCBMoptexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit_func = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit_func, nqubits, 9, pairs, fusion_enable=True, include_compile_time=False)


"""
@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_nogf_inc(benchmark, nqubits):
    benchmark.group = "QCBMinc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit_func = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit_func, nqubits, 9, pairs, fusion_enable=False, include_compile_time=True)
"""


@pytest.mark.parametrize('nqubits', nqubit_list)
def test_qcbm_nogf_exc(benchmark, nqubits):
    benchmark.group = "QCBMexc"
    pairs = [(i, (i + 1) % nqubits) for i in range(nqubits)]
    circuit_func = generate_qcbm_circuit(nqubits, 9, pairs)
    native_execute(benchmark, circuit_func, nqubits, 9, pairs, fusion_enable=False, include_compile_time=False)