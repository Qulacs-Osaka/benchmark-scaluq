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
            basename = os.path.basename(filepath)
            prec = basename[:-5]
            filepaths.append((f'{libname} ({prec})', filepath))

    cpuinfo = None
    dat1 = defaultdict(lambda: defaultdict(dict))
    for name, filepath in filepaths:
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
                dat[group][name][nqubits] = dat1[group][name][nqubits] / (nqubits * (nqubits - 1) * 100)
    return dat, cpuinfo


def plot(dat, group, cpu):
    assert len(group) > 0
    dat_group = dat[group]
    cmap = plt.get_cmap("tab10")
    for name in dat_group:
        xs = list(sorted(dat_group[name].keys()))
        ys = [dat_group[name][x] for x in xs]
        linestyle = 'solid'
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
        plt.plot(xs, ys, label=name, c=cmap(cid), linestyle=linestyle)

    plt.title(f"{group} {cpu}")
    plt.yscale("log")
    plt.grid(which='major', color='black', linestyle='-', alpha=0.3)
    plt.grid(which='minor', color='black', linestyle='-', alpha=0.1)
    plt.xlabel("# of qubits", fontsize=16)
    plt.ylabel("Time [sec]", fontsize=16)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)




if __name__ == "__main__":
    dat, cpu = load()

    for group in dat.keys():
        if group != 'CX':
            continue
        plt.figure(figsize=(12, 6))
        plot(dat, group, cpu)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1.0))
        plt.tight_layout()
        plt.savefig(f"./image/{group}.pdf")
        plt.savefig(f"./image/{group}.png")
        plt.clf()

