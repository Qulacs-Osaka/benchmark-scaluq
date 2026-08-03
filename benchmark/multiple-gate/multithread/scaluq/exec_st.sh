# Single-thread run: OpenMP fork/join overhead dominates small states in the
# multi-thread run, so also measure single-thread performance for n <= 18.
export OMP_NUM_THREADS=1
export NQUBITS_MAX="${NQUBITS_MAX:-27}"

rm -f "${1}_st.json"
# Output goes to a log file so a dropped SSH / detached session can't kill the
# run with a broken pipe. Follow with: tail -f "${1}_st.log"
PYTHONUNBUFFERED=1 uv run python -m pytest "$1.py" --benchmark-json="${1}_st.json" --benchmark-min-rounds=5 -q > "${1}_st.log" 2>&1
