uv run python -m pytest "$1.py" --benchmark-json="$1.json" --benchmark-min-rounds=1 --benchmark-warmup=on
