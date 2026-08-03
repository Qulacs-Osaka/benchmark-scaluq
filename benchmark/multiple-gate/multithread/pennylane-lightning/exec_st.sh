# Single-thread run. NOTE: this only sets OMP_NUM_THREADS=1; lightning.qubit is
# still the OpenMP-enabled wheel, so it may carry per-region OpenMP overhead and
# is NOT a true no-OpenMP build like scaluq (host_serial) / qulacs (USE_OMP=No).
export OMP_NUM_THREADS=1
export NQUBITS_MAX="${NQUBITS_MAX:-27}"

rm -f "${1}_st.json"
PYTHONUNBUFFERED=1 uv run python -m pytest "$1.py" --benchmark-json="${1}_st.json" --benchmark-min-rounds=5 -q > "${1}_st.log" 2>&1
