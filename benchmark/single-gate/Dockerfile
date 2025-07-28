FROM nvidia/cuda:12.6.3-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

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
## install qutensor
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
RUN git clone https://github.com/qiskit/qiskit-aer --depth=1 /tmp/qiskit-aer
RUN cd /tmp/qiskit-aer && \
    uv run --no-project python setup.py bdist_wheel -- -DAER_THRUST_BACKEND=CUDA -DCUQUANTUM_ROOT="/opt/nvidia/cuquantum" -DCUTENSOR_ROOT="/opt/nvidia/cutensor" -DAER_ENABLE_CUQUANTUM=true -DCUQUANTUM_STATIC=true && \
    uv run --no-project python -m pip install --break-system-packages dist/*.whl --no-build-isolation
RUN uv run python -m pip uninstall --break-system-packages -y cmake
RUN rm -r /tmp/qiskit-aer

# install qulacs
RUN git clone https://github.com/qulacs/qulacs --depth=1 /tmp/qulacs
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    libboost-dev
RUN cd /tmp/qulacs && \
    USE_GPU=Yes uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/qulacs

# install scaluq
RUN git clone https://github.com/qulacs/scaluq --depth=1 /tmp/scaluq
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    ninja-build
RUN cd /tmp/scaluq && \
    SCALUQ_USE_CUDA=OFF SCALUQ_USE_TEST=OFF SCALUQ_USE_EXE=OFF SCALUQ_FLOAT16=ON SCALUQ_BFLOAT16=ON uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/scaluq

