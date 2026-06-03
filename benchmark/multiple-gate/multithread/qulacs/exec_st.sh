# Single-thread run (see scaluq/exec_st.sh). Note: unlike the multi-thread
# exec.sh we do NOT set QULACS_PARALLEL_NQUBIT_THRESHOLD, so Qulacs uses its
# natural serial code path.
export OMP_NUM_THREADS=1
export NQUBITS_MAX="${NQUBITS_MAX:-18}"

rm -f "${1}_st.json"
PYTHONUNBUFFERED=1 uv run python -m pytest "$1.py" --benchmark-json="${1}_st.json" --benchmark-min-rounds=5 -q > "${1}_st.log" 2>&1
