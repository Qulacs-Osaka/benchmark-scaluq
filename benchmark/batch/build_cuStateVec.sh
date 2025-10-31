#!/usr/bin/bash
nvcc -o cuStateVec cuStateVec.cu \
    -I${CUQUANTUM_ROOT}/include \
    -L${CUQUANTUM_ROOT}/lib \
    -L${CUQUANTUM_ROOT}/lib64 \
    -lcustatevec

nvcc -o test_cuStateVec test_cuStateVec.cu \
    -I${CUQUANTUM_ROOT}/include \
    -L${CUQUANTUM_ROOT}/lib \
    -L${CUQUANTUM_ROOT}/lib64 \
    -lcustatevec
