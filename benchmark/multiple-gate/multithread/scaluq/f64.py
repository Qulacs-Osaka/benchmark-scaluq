import os
import pytest
import random
import math
import scaluq as scaluqbase
if os.environ.get("OMP_NUM_THREADS", "32") == "1":
    from scaluq.host_serial.f64 import StateVector
else:
    from scaluq.default.f64 import StateVector
from scaluq.default.f64 import Circuit
import scaluq.default.f64.gate as mgate

# Upper qubit count (inclusive). The single-thread run (exec_st.sh) lowers this
# to 18 since single-thread large states are too slow to be interesting.
nqubits_list = list(range(4, int(os.environ.get("NQUBITS_MAX", "27")) + 1))

# On this environment the per-gate time is dominated by Scaluq's per-gate OpenMP
# fork/join overhead (~ms, roughly constant across qubit counts), so the
# measured per-gate value is independent of niter. Keep niter small: a larger
# value only multiplies the wall-clock time without changing the result.
niter = 10

def benchfunc(circuit, state):
    for _ in range(niter):
        circuit.update_quantum_state(state, {}, 0)
    scaluqbase.synchronize()

@pytest.mark.parametrize("nqubits", nqubits_list)
def test(benchmark, nqubits):
    random.seed(nqubits)
    benchmark.group = 'circuit'
    benchmark.extra_info["niter"] = niter
    circuit = Circuit()
    for i in range(nqubits):
        circuit.add_gate(mgate.CX(i, (i+1) % nqubits))
        circuit.add_gate(mgate.RX(i, random.uniform(0, math.pi * 2)))
        circuit.add_gate(mgate.RZ(i, random.uniform(0, math.pi * 2)))
    state = StateVector(nqubits)
    benchfunc(circuit, state)  # warmup
    benchmark(benchfunc, circuit, state)
