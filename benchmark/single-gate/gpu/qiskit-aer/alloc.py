import cupy as cp

def test_alloc():
    # 単位は要素数（complex128）
    for k in range(10, 30):
        n = 2**k
        try:
            a = cp.empty(n, dtype=cp.complex128)
            print("alloc ok:", k, "->", n, "elements")
            del a
        except Exception as e:
            print("alloc failed at k=", k, "n=", n, "err=", e)
            break

test_alloc()
print("mem info:", cp.cuda.runtime.memGetInfo())

