export OMP_NUM_THREADS=1
pytest "$1.py" --benchmark-json="$1.json" --benchmark-min-rounds=5
