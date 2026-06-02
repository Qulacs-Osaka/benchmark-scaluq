set -eux

# Thread count for the multi-thread benchmark, shared by all libraries
# (Scaluq/Kokkos, Qulacs, Qiskit-Aer) so the comparison is fair. This machine
# has 32 physical cores / 64 hyperthreads, but some cores are used by other
# processes, so we pin to the physical core count (avoiding hyperthreads). Tune
# this single value as needed; a lower count also reduces the per-gate OpenMP
# fork/join overhead that dominates small qubit counts. Override from the shell
# with: NTHREADS=16 ./execall.sh
export OMP_NUM_THREADS="${NTHREADS:-32}"

cd scaluq/
./exec.sh f64
cd -
cd qulacs/
./exec.sh f64
cd -
cd qiskit-aer/
./exec.sh f64
cd -
