# Single-thread run (see scaluq/exec_st.sh). OMP_NUM_THREADS=1 also makes
# AerSimulator's max_parallel_threads=1 (read from the env in f64.py), so it is
# single-threaded at every qubit count (no statevector_parallel_threshold step).
export OMP_NUM_THREADS=1
export NQUBITS_MAX="${NQUBITS_MAX:-27}"

rm -f "${1}_st.json"
PYTHONUNBUFFERED=1 uv run python -m pytest "$1.py" --benchmark-json="${1}_st.json" --benchmark-min-rounds=5 -q > "${1}_st.log" 2>&1
