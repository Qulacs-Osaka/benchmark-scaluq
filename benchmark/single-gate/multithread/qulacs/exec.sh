rm -f "run.json"
QULACS_PARALLEL_NQUBIT_THRESHOLD=1 uv run python -m pytest run.py --benchmark-json="run.json" --benchmark-min-rounds=10
