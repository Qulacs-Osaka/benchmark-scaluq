import json
import glob
import matplotlib.pyplot as plt
from collections import defaultdict
import os

# libs = ["scaluq", "qulacs", "qiskit-aer", "project-q"]
# libnames = ["Sclauq", "Qulacs", "Qiskit-Aer", "Project Q"]
libs = ["scaluq", "qulacs"]
libnames = ["Proposal", "Qulacs"]
markers = ['P', 'o']
f64_only = True

def load():
    filepaths = []

    for libidx, lib in enumerate(libs):
        path = f"./{lib}/*.json"
        flist = glob.glob(path)
        for filepath in flist:
            libname = libnames[libidx]
            basename = os.path.basename(filepath)
            prec = basename[:-5]
            if f64_only:
                if prec == 'f64':
                    filepaths.append((f'{libname}', filepath))
            else:
                filepaths.append((f'{libname} ({prec})', filepath))

    cpuinfo = None
    dat1 = defaultdict(lambda: defaultdict(dict))
    for name, filepath in filepaths:
        print(filepath)
        data = json.load(open(filepath))
        cpu = f'{data["machine_info"]["cpu"]["brand_raw"]} {data["machine_info"]["cpu"]["count"]}T'
        assert cpuinfo == None or cpuinfo == cpu
        cpuinfo = cpu
        items = data["benchmarks"]
        for item in items:
            group = item["group"]
            nqubits = int(item["params"]["nqubits"])
            stats = item["stats"]
            dat1[group][name][nqubits] = stats["mean"]
    dat = defaultdict(lambda: defaultdict(dict))
    for group in dat1:
        for name in dat1[group]:
            for nqubits in dat1[group][name]:
                dat[group][name][nqubits] = dat1[group][name][nqubits] / (nqubits * (nqubits - 1) * 100) * 1000
    return dat, cpuinfo


def plot(dat, group, cpu):
    assert len(group) > 0
    dat_group = dat[group]
    cmap = plt.get_cmap("tab10")
    for name in dat_group:
        print(name)
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        linestyle = 'solid'
        if ' (' in name:
            cid = libnames.index(name[:name.index(' (')])
        else:
            cid = libnames.index(name)
        if name.count('(f64)'):
            linestyle = 'solid'
        if name.count('(f32)'):
            linestyle = 'dashed'
        if name.count('(f16)'):
            linestyle = 'dashdot'
        if name.count('(bf16)'):
            linestyle = 'dotted'
        plt.plot(xs, ys, label=name, c=cmap(cid), linestyle=linestyle, marker=markers[cid])

    plt.title(f"{group} Gate apply@{cpu}")
    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("Number of qubits", fontsize=16)
    plt.ylabel("Execution time per iteration [ms]", fontsize=16)
    plt.xticks(list(range(5, 26, 5)), fontsize=16)
    plt.yticks(fontsize=16)




if __name__ == "__main__":
    dat, cpu = load()

    for group in dat.keys():
        if group != 'CX':
            continue
        plt.figure(figsize=(7, 5))
        plot(dat, group, cpu)
        plt.legend(fontsize=18)
        plt.tight_layout()
        plt.savefig(f"./image/{group}.pdf")
        plt.savefig(f"./image/{group}.png", dpi=300)
        plt.clf()

