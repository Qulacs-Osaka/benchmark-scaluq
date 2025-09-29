rm -f "run.json"
uv run python -m pytest run.py --benchmark-json="run.json" --benchmark-min-rounds=10
