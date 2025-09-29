import cupy as cp

sizes = [1<<30, 4*(1<<30), 8*(1<<30)]
for s in sizes:
    try:
        m = cp.cuda.alloc_pinned_memory(s)
        print("pinned alloc ok:", s)
        del m
    except Exception as e:
        print("pinned alloc failed:", s, "err:", e)

