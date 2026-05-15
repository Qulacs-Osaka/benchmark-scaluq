rm -f "$1.json"
QULACS_PARALLEL_NQUBIT_THRESHOLD=1 uv run python -m pytest "$1.py" --benchmark-json="$1.json" --benchmark-min-rounds=10
