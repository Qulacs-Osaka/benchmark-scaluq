#!/bin/bash

# Before building, set your target CUDA architecture in CMakeLists.txt
# Example: set(CMAKE_CUDA_ARCHITECTURES 86) for RTX 3060

set -e 
cd "$(dirname "$0")"

if [ ! -d scaluq/ ]; then
    git clone https://github.com/qulacs/scaluq.git
fi

cmake -B build -G Ninja -D SCALUQ_CUDA_ARCH=86 -D Kokkos_ARCH_AMPERE86=ON
cmake --build build -j 8 # Executable will be created at build/Scaluq