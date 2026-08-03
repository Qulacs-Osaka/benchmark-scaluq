#!/bin/bash

# Before building, set your target CUDA architecture in CMakeLists.txt
# Example: set(CMAKE_CUDA_ARCHITECTURES 86) for RTX 3060

set -e
cd "$(dirname "$0")"

# Pin Scaluq to the same commit as the multiple-gate benchmark (random_device
# fix). Override with: SCALUQ_COMMIT=... ./build_Scaluq.sh
SCALUQ_COMMIT="${SCALUQ_COMMIT:-025565d2fef0ce260692d61d08b21bf1f7491ffd}"
if [ ! -d scaluq/ ]; then
    git clone https://github.com/qulacs/scaluq.git
fi
git -C scaluq checkout "$SCALUQ_COMMIT"

cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -D SCALUQ_CUDA_ARCH=80 -D Kokkos_ARCH_AMPERE80=ON
cmake --build build -j 8 # Executable will be created at build/Scaluq
