export OMP_NUM_THREADS=1
pytest run.py --benchmark-json="run.json" --benchmark-min-rounds=5
