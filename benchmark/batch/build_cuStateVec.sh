nvcc -o cuStateVec cuStateVec.cu \
    -L${CUQUANTUM_ROOT}/lib \
    -L${CUQUANTUM_ROOT}/lib64 \
    -lcustatevec