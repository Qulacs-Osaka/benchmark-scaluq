set -eux
cd scaluq/
./exec.sh f64
cd -
cd pennylane-lightning-amdgpu/
./exec.sh f64
cd -
