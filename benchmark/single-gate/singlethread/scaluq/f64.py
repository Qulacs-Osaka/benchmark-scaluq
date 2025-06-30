import pytest
from scaluq.default.f64 import *
from scaluq.default.f64.gate import *
import itertools
import random

single_gates = [
    ("X", X),
    ("Y", Y),
    ("Z", Z),
    ("H", H),
    ("S", S),
    ("Sdag", Sdag),
    ("T", T),
    ("Tdag", Tdag)
]

nqubits_list = range(4, 20)

single_params = map(lambda p: pytest.param(p[0][0], p[0][1], p[1]), itertools.product(single_gates, nqubits_list))

def benchfunc(gate, state):
    gate.update_quantum_state(state)

@pytest.mark.parametrize(["name", "factory", "nqubits"], single_params)
def test_Single(benchmark, name, factory, nqubits):
    benchmark.group = name
    gate = factory(random.randint(0, nqubits - 1))
    state = StateVector.Haar_random_state(nqubits)
    benchmark(benchfunc, gate, state)
