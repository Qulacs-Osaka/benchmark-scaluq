#!/usr/bin/env bash
set -euo pipefail

CUSTATEVEC_BIN="./cuStateVec"
SCALUQ_BIN="./build/Scaluq"

CSV_PATH="batch_sweep.csv"
: > "$CSV_PATH"
echo "impl,n_qubits,n_batches,n_iterations,seed,per_iteration_ms" >> "$CSV_PATH"

NQ=16

echo "=== Batch sweep: n_qubits=${NQ}, n_batches = 1..300 step 50 ==="

# warmup
"$CUSTATEVEC_BIN" "$NQ" 50 /tmp/warmup_custatevec.csv
"$SCALUQ_BIN" "$NQ" 50 /tmp/warmup_scaluq.csv

for NB in $(seq 0 50 300); do
    NB=$((NB == 0 ? 1 : NB))

    echo "--- custatevec: n_batches=${NB}"
    "$CUSTATEVEC_BIN" "$NQ" "$NB" "$CSV_PATH"

    echo "--- scaluq: n_batches=${NB}"
    "$SCALUQ_BIN" "$NQ" "$NB" "$CSV_PATH"
done

echo "✅ Done. Results saved to $CSV_PATH"
