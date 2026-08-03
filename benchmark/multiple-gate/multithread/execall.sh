set -eux

export OMP_NUM_THREADS="${NTHREADS:-96}"
export OMP_PROC_BIND="true"

cd scaluq/
./exec.sh f64
cd -
cd qulacs/
./exec.sh f64
cd -
cd qiskit-aer/
./exec.sh f64
cd -
cd pennylane-lightning/
./exec.sh f64
cd -
cd pennylane-lightning-kokkos/
./exec.sh f64
cd -
