import json
import glob
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
import os

#libs = ["scaluq", "qulacs", "qiskit-aer", "qiskit-aer-custatevec", "custatevec"]
#libnames = ["Sclauq", "Qulacs", "Qiskit-Aer", "Qiskit-Aer with cuStateVec", "cuStateVec"]
libs = ["scaluq", "qulacs", "custatevec", "qiskit-aer", "pennylane-lightning", "pennylane-lightning-kokkos"]
libnames = ["Scaluq", "Qulacs", "cuStateVec", "Qiskit-Aer", "Lightning", "Lightning-Kokkos"]
markers = ['P', 'o', '^', 's', 'D', 'X', '*']
colors = ['tab:red', 'tab:blue', 'tab:gray', "tab:green", "tab:purple", "tab:orange", "tab:brown"]
only_f64 = True

def load():
    filepaths = []

    for libidx, lib in enumerate(libs):
        path = f"./{lib}/*.json"
        flist = glob.glob(path)
        for filepath in flist:
            libname = libnames[libidx]
            basename = os.path.basename(filepath)
            prec = basename[:-5]
            if only_f64:
                if prec == 'f64':
                    filepaths.append((f'{libname}', filepath))
                elif prec == 'f64_st':
                    filepaths.append((f'{libname} (1 thread)', filepath))
            else:
                filepaths.append((f'{libname} ({prec})', filepath))

    dat = defaultdict(lambda: defaultdict(dict))
    for name, filepath in filepaths:
        print(filepath)
        data = json.load(open(filepath))
        items = data["benchmarks"]
        for item in items:
            group = item["group"]
            nqubits = int(item["params"]["nqubits"])
            # number of layer repetitions per timed call (default 100 for older
            # results that did not record it); each layer = nqubits * 3 gates
            # (CX, RX, RZ) -> normalize to milliseconds per single gate.
            niter = item.get("extra_info", {}).get("niter", 100)
            dat[group][name][nqubits] = item["stats"]["median"] / (nqubits * niter * 3) * 1000
    return dat


def _base_name(name):
    # "Scaluq (1 thread)" -> "Scaluq"; "Scaluq" -> "Scaluq"
    suffix = ' (1 thread)'
    return name[:-len(suffix)] if name.endswith(suffix) else name


def plot(dat, group, single):
    # single=False -> multi-thread curves (names without "(1 thread)")
    # single=True  -> single-thread curves (names with    "(1 thread)")
    dat_group = dat[group]
    names = [n for n in dat_group if n.endswith(' (1 thread)') == single]
    # draw Scaluq last so its (emphasized) curve sits on top
    names.sort(key=lambda n: _base_name(n) == "Scaluq")
    for name in names:
        base = _base_name(name)
        cid = libnames.index(base)
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        emph = base == "Scaluq"  # draw the proposed library on top, same weight
        plt.plot(xs, ys, label=base, c=colors[cid], marker=markers[cid],
                 linewidth=1.6, markersize=6,
                 zorder=5 if emph else 3)

    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("Number of qubits", fontsize=16)
    plt.ylabel("Execution time per gate [ms]", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)


if __name__ == "__main__":
    dat = load()

    for group in dat.keys():
        for single, suffix in [(False, "multithread"), (True, "singlethread")]:
            plt.rcParams["font.size"] = 18
            plt.figure(figsize=(7, 5))
            plot(dat, group, single)
            plt.legend(fontsize=14, loc='upper left')
            plt.tight_layout()
            #plt.savefig(f"./image/{group}_{suffix}.pdf")
            plt.savefig(f"./image/{group}_{suffix}.png", dpi=300)
            plt.clf()

