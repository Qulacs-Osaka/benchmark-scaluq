#!/usr/bin/env bash
set -euo pipefail

CUSTATEVEC_BIN="./custatevec_bench"
SCALUQ_BIN="./scaluq_bench"
CSV_PATH="qubits_sweep.csv"

# remove old data
rm -f "$CSV_PATH"

BATCHES=1024

echo "=== Qubits sweep: n_qubits = 4..16, n_batches = ${BATCHES} ==="

for NQ in {4..16}; do
    echo "--- custatevec: n_qubits=${NQ}, n_batches=${BATCHES}"
    "$CUSTATEVEC_BIN" "$NQ" "$BATCHES"

    echo "--- scaluq: n_qubits=${NQ}, n_batches=${BATCHES}"
    "$SCALUQ_BIN" "$NQ" "$BATCHES"
done

# rename file
mv results.csv "$CSV_PATH"
echo "Done. Results saved to $CSV_PATH"
