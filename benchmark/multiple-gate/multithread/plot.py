import json
import glob
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
import os

#libs = ["scaluq", "qulacs", "qiskit-aer", "qiskit-aer-custatevec", "custatevec"]
#libnames = ["Sclauq", "Qulacs", "Qiskit-Aer", "Qiskit-Aer with cuStateVec", "cuStateVec"]
libs = ["scaluq", "qulacs", "custatevec", "qiskit-aer"]
libnames = ["Scaluq", "Qulacs", "cuStateVec", "Qiskit-Aer"]
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


def plot(dat, group):
    assert len(group) > 0
    dat_group = dat[group]
    cmap = plt.get_cmap("tab10")
    for name in dat_group:
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        linestyle = 'solid'
        if name.count('('):
            cid = libnames.index(name[:name.index(' (')])
            if name.count('(f64)'):
                linestyle = 'solid'
            if name.count('(f32)'):
                linestyle = 'dashed'
            if name.count('(f16)'):
                linestyle = 'dashdot'
            if name.count('(bf16)'):
                linestyle = 'dotted'
            if name.count('(cuStateVec)'):
                linestyle = 'dashed'
            if name.count('(1 thread)'):
                linestyle = 'dashed'
        else:
            cid = libnames.index(name)
        # Only the multi-thread (solid) curves go in the legend; the dashed
        # single-thread curves are explained by a separate line-style legend.
        label = '_nolegend_' if name.count('(1 thread)') else name
        plt.plot(xs, ys, label=label, c=colors[cid], linestyle=linestyle, marker=markers[cid])

    #plt.title(f"{group} Gate apply@Nvidia A100 40 GB")
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
        plt.figure(figsize=(8, 6))
        plot(dat, group)
        # Library legend (multi-thread / solid curves only), top-left corner.
        lib_legend = plt.legend(fontsize=15, loc='upper left')
        plt.gca().add_artist(lib_legend)
        # Separate legend explaining the line styles, bottom-right corner.
        style_handles = [
            Line2D([0], [0], color='black', linestyle='solid', label='32 threads'),
            Line2D([0], [0], color='black', linestyle='dashed', label='1 thread'),
        ]
        plt.legend(handles=style_handles, fontsize=14, loc='lower right')
        plt.tight_layout()
        #plt.savefig(f"./image/{group}.pdf")
        plt.savefig(f"./image/{group}.png", dpi=300)
        plt.clf()

