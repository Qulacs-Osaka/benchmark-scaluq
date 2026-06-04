FROM ubuntu:24.04

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

# install qiskit-aer
## build and install qiskit-aer
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    libopenblas-dev \
    zlib1g-dev
RUN uv run python -m pip install cmake "conan<2.0.0" scikit-build pybind11 --break-system-packages
RUN git clone https://github.com/qiskit/qiskit-aer --depth=1 /tmp/qiskit-aer
RUN cd /tmp/qiskit-aer && \
    uv run --no-project python setup.py bdist_wheel && \
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
    uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/qulacs

# install scaluq
RUN git clone https://github.com/qulacs/scaluq /tmp/scaluq
RUN git -C /tmp/scaluq switch do-not-call-random_device-when-it-has-seed
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    ninja-build
RUN cd /tmp/scaluq && \
    SCALUQ_USE_TEST=OFF SCALUQ_USE_EXE=OFF uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/scaluq

# install PennyLane + Lightning (lightning.qubit) and Lightning-Kokkos
# (lightning.kokkos). The PyPI x86_64 wheels are prebuilt with the OpenMP
# backend (no source build needed), and both honor OMP_NUM_THREADS.
RUN uv run python -m pip install --break-system-packages \
    pennylane pennylane-lightning pennylane-lightning-kokkos

RUN uv run python -m pip install --break-system-packages matplotlib
