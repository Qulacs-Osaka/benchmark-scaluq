#!/usr/bin/bash
nvcc -O3 -DNDEBUG -o cuStateVec cuStateVec.cu \
    -I${CUQUANTUM_ROOT}/include \
    -L${CUQUANTUM_ROOT}/lib \
    -L${CUQUANTUM_ROOT}/lib64 \
    -arch=sm_80 \
    -lcustatevec
