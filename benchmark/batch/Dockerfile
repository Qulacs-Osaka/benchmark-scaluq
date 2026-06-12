# Image for the batch benchmark (build/run Scaluq.cpp and cuStateVec.cu).
# Build with:
#   docker build -f Dockerfile -t bench-scaluq .
# then enter it via run_container.sh.
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# ninja-build is required by build_Scaluq.sh (cmake -G Ninja)
RUN apt-get update && apt-get install -y \
    git cmake make ninja-build wget tar

WORKDIR /opt

RUN wget https://developer.download.nvidia.com/compute/cuquantum/redist/cuquantum/linux-x86_64/cuquantum-linux-x86_64-24.08.0.5_cuda12-archive.tar.xz && \
    tar -xf cuquantum-linux-x86_64-24.08.0.5_cuda12-archive.tar.xz

ENV CUQUANTUM_ROOT=/opt/cuquantum-linux-x86_64-24.08.0.5_cuda12-archive

WORKDIR /workspace
