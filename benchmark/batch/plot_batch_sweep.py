#!/usr/bin/env python3
import sys
import pandas as pd
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <csv_file>")
    sys.exit(1)

plt.rcParams.update(
    {
        "font.size": 12,
        "axes.labelsize": 14,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 14,
    }
)

csv_file = sys.argv[1]
df = pd.read_csv(csv_file)

name_map = {
    "scaluq": "Proposal",
    "custatevec": "cuStateVec",
}

style_map = {
    "scaluq": dict(color="red", marker="P", linestyle="-"),
    "custatevec": dict(color="gray", marker="^", linestyle="-"),
}

plt.figure(figsize=(6, 4))

for impl in ["scaluq", "custatevec"]:
    sub = df[df["impl"] == impl].sort_values("n_batches")
    if sub.empty:
        continue

    plt.plot(
        sub["n_batches"],
        sub["per_iteration_ms"],
        label=name_map[impl],
        **style_map[impl],
    )

plt.xlabel("Number of batches")
plt.ylabel("Execution time per iteration [ms]")
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.legend()
plt.tight_layout()
plt.savefig("batch_sweep.png", dpi=300)
