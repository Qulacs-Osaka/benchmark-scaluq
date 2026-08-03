import json
import glob
import matplotlib.pyplot as plt
from collections import defaultdict
import os

#libs = ["scaluq", "qulacs", "qiskit-aer", "qiskit-aer-custatevec", "custatevec"]
#libnames = ["Sclauq", "Qulacs", "Qiskit-Aer", "Qiskit-Aer with cuStateVec", "cuStateVec"]
libs = ["scaluq", "qulacs", "custatevec", "qiskit-aer", "pennylane-lightning-gpu"]
libnames = ["Scaluq", "Qulacs", "cuStateVec", "Qiskit-Aer", "Lightning-GPU"]
markers = ['P', 'o', '^', 's', 'D']
colors = ['tab:red', 'tab:blue', 'tab:gray', "tab:green", "tab:purple"]
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


def plot(dat, group):
    assert len(group) > 0
    dat_group = dat[group]
    names = list(dat_group.keys())
    names.sort(key=lambda n: n == "Scaluq")  # draw Scaluq last so it sits on top
    for name in names:
        cid = libnames.index(name)
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        # all libraries drawn uniformly; Scaluq only placed on top (zorder)
        plt.plot(xs, ys, label=name, c=colors[cid], marker=markers[cid],
                 linewidth=1.6, markersize=6,
                 zorder=5 if name == "Scaluq" else 3)

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
        plt.rcParams["font.size"] = 18
        plt.figure(figsize=(7, 5))
        plot(dat, group)
        plt.legend(fontsize=14, loc='upper left')
        plt.tight_layout()
        #plt.savefig(f"./image/{group}_gpu.pdf")
        plt.savefig(f"./image/{group}_gpu.png", dpi=300)
        plt.clf()

