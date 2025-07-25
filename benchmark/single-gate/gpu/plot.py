import json
import glob
import matplotlib.pyplot as plt
from collections import defaultdict
import os

libs = ["scaluq", "qulacs", "qiskit-aer"]
libnames = ["Sclauq", "Qulacs", "Qiskit-Aer"]

def load():
    filepaths = []

    for libidx, lib in enumerate(libs):
        path = f"./{lib}/*.json"
        flist = glob.glob(path)
        for filepath in flist:
            libname = libnames[libidx]
            if lib == "scaluq":
                prec = os.path.basename(filepath)[:-5]
                filepaths.append((f'{libname} ({prec})', filepath))
            else:
                filepaths.append((f'{libname}', filepath))

    dat = defaultdict(lambda: defaultdict(dict))
    for name, filepath in filepaths:
        data = json.load(open(filepath))

        items = data["benchmarks"]
        for item in items:
            group = item["group"]
            nqubits = int(item["params"]["nqubits"])
            stats = item["stats"]
            dat[group][name][nqubits] = float(stats["min"])

    return dat


def plot(dat, group):
    assert len(group) > 0
    dat_group = dat[group]
    cmap = plt.get_cmap("tab10")
    for name in dat_group:
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        if name.count('('):
            cid = libnames.index(name[:name.index(' ')])
        else:
            cid = libnames.index(name)
        plt.plot(xs, ys, label=name, c=cmap(cid))

    plt.title(f"{group}")
    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("# of qubits", fontsize=16)
    plt.ylabel("Time [sec]", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)




if __name__ == "__main__":
    dat = load()

    for group in dat.keys():
        plt.figure(figsize=(12, 6))
        plot(dat, group)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1.0))
        plt.tight_layout()
        plt.savefig(f"./image/{group}.pdf")
        plt.savefig(f"./image/{group}.png")
        plt.clf()

