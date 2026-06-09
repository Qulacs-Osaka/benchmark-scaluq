FROM nvidia/cuda:12.6.3-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

# Pinned versions, matching the CPU (multithread) Dockerfile so the same library
# versions are compared on CPU and GPU (override with --build-arg to bump).
ARG QISKIT_AER_COMMIT=837c3ef3c39248aae936580360c22224dcefb265
ARG QULACS_COMMIT=4f6de32cca807ec4cabf1107e3806786cb953c56
ARG SCALUQ_COMMIT=0a8d36af4ed7ff9b6b63955bcdf4220e0aaf7a3a
# GPU-only pip packages: pin after the run once the resolved versions are known.

RUN apt-get update
RUN apt-get install -y \
    ca-certificates \
    curl \
    git \
    wget

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv python install 3.12 --default

# install pytest-benchmark
RUN uv run python -m pip install --break-system-packages pytest-benchmark

# install qiskit without default aer
RUN uv run python -m pip install --break-system-packages qiskit
RUN uv run python -m pip uninstall --break-system-packages qiskit-aer

# install qiskit-aer with cuquantum support
## install cuquantum
RUN wget https://developer.download.nvidia.com/compute/cuquantum/redist/cuquantum/linux-x86_64/cuquantum-linux-x86_64-23.03.0.20-archive.tar.xz
RUN tar xf cuquantum-linux-x86_64-23.03.0.20-archive.tar.xz
RUN mkdir -p /opt/nvidia/
RUN cp -r cuquantum-linux-x86_64-23.03.0.20-archive/ /opt/nvidia/cuquantum/
RUN rm -r cuquantum-linux-x86_64-23.03.0.20-archive.tar.xz cuquantum-linux-x86_64-23.03.0.20-archive/
# install qutensor
RUN wget https://developer.download.nvidia.com/compute/cutensor/redist/libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz
RUN tar xf libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz
RUN mkdir -p /opt/nvidia/
RUN cp -r libcutensor-linux-x86_64-1.7.0.1-archive/ /opt/nvidia/cutensor/
RUN rm -r libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz libcutensor-linux-x86_64-1.7.0.1-archive/
## build and install qiskit-aer
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    libopenblas-dev \
    zlib1g-dev
RUN uv run python -m pip install cmake "conan<2.0.0" scikit-build pybind11 --break-system-packages
RUN git clone https://github.com/qiskit/qiskit-aer /tmp/qiskit-aer
RUN git -C /tmp/qiskit-aer checkout "${QISKIT_AER_COMMIT}"
RUN cd /tmp/qiskit-aer && \
    uv run --no-project python setup.py bdist_wheel -- -DAER_THRUST_BACKEND=CUDA -DAER_CUDA_ARCH="8.0" -DCUQUANTUM_ROOT="/opt/nvidia/cuquantum" -DCUTENSOR_ROOT="/opt/nvidia/cutensor" -DAER_ENABLE_CUQUANTUM=true && \
    uv run --no-project python -m pip install --break-system-packages dist/*.whl --no-build-isolation
RUN uv run python -m pip uninstall --break-system-packages -y cmake
RUN rm -r /tmp/qiskit-aer

# install qulacs
RUN git clone https://github.com/qulacs/qulacs /tmp/qulacs
RUN git -C /tmp/qulacs checkout "${QULACS_COMMIT}"
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    libboost-dev
RUN cd /tmp/qulacs && \
    USE_GPU=Yes uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/qulacs

# install scaluq
RUN git clone https://github.com/qulacs/scaluq /tmp/scaluq
RUN git -C /tmp/scaluq checkout "${SCALUQ_COMMIT}"
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    ninja-build
RUN cd /tmp/scaluq && \
    SCALUQ_USE_CUDA=ON  SCALUQ_CUDA_ARCH=AMPERE80 SCALUQ_USE_TEST=OFF SCALUQ_USE_EXE=OFF SCALUQ_FLOAT16=ON SCALUQ_BFLOAT16=ON uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/scaluq

# install custatevec
RUN uv run --no-project python -m pip install --break-system-packages cupy-cuda12x cuquantum-python-cu12 custatevec-cu12
# 
# # install QuEST
# RUN git clone https://github.com/rrmeister/pyquest -b develop --depth=1 --recursive /tmp/pyquest
# RUN cd /tmp/pyquest && \
#     sed -i -e "s/'multithreaded': True,/'multithreaded': False,/" -e "s/'gpu_accelerated': False,/'gpu_accelerated': True,/" -e "s/'gpu_compute_capability': None,/'gpu_compute_capability': 80,/" setup.py && \
#     uv run --no-project python -m pip install --break-system-packages .
#     

ENV LD_LIBRARY_PATH /opt/nvidia/cuquantum/lib/12:/opt/nvidia/cutensor/lib/12:$LD_LIBRARY_PATH

RUN uv run python -m pip install --break-system-packages matplotlib
