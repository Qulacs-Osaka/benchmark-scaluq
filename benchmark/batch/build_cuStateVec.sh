#!/usr/bin/bash
nvcc -O2 \
    -o cuStateVec cuStateVec.cu \
    -I${CUQUANTUM_ROOT}/include \
    -L${CUQUANTUM_ROOT}/lib \
    -L${CUQUANTUM_ROOT}/lib64 \
    -arch=sm_86 \
    -lcustatevec
