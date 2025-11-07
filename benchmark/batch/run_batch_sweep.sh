#!/usr/bin/env bash
set -euo pipefail

CUSTATEVEC_BIN="./custatevec_bench"
SCALUQ_BIN="./scaluq_bench"
CSV_PATH="batch_sweep.csv"

rm -f "$CSV_PATH"

NQ=16

echo "=== Batch sweep: n_qubits=${NQ}, n_batches = 1..1000 step 100 ==="

for NB in $(seq 1 100 1000); do
    echo "--- custatevec: n_batches=${NB}"
    "$CUSTATEVEC_BIN" "$NQ" "$NB"

    echo "--- scaluq: n_batches=${NB}"
    "$SCALUQ_BIN" "$NQ" "$NB"
done

mv results.csv "$CSV_PATH"
echo "✅ Done. Results saved to $CSV_PATH"
