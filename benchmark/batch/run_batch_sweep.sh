#!/usr/bin/env bash
set -euo pipefail

CUSTATEVEC_BIN="./cuStateVec"
SCALUQ_BIN="./build/Scaluq"
CSV_PATH="batch_sweep.csv"

rm -f "$CSV_PATH"

NQ=16

echo "=== Batch sweep: n_qubits=${NQ}, n_batches = 1..1000 step 100 ==="

for NB in $(seq 1 100 400); do
    echo "--- custatevec: n_batches=${NB}"
    "$CUSTATEVEC_BIN" "$NQ" "$NB" "$CSV_PATH"

    echo "--- scaluq: n_batches=${NB}"
    "$SCALUQ_BIN" "$NQ" "$NB" "$CSV_PATH"
done

echo "✅ Done. Results saved to $CSV_PATH"
