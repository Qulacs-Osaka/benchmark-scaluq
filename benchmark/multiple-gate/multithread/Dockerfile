FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Pinned versions used in the benchmark (override with --build-arg to bump).
ARG QISKIT_AER_COMMIT=837c3ef3c39248aae936580360c22224dcefb265
ARG QULACS_COMMIT=4f6de32cca807ec4cabf1107e3806786cb953c56
ARG SCALUQ_COMMIT=0a8d36af4ed7ff9b6b63955bcdf4220e0aaf7a3a
ARG PENNYLANE_VERSION=0.45.0

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
RUN git clone https://github.com/qiskit/qiskit-aer /tmp/qiskit-aer
RUN git -C /tmp/qiskit-aer checkout "${QISKIT_AER_COMMIT}"
RUN cd /tmp/qiskit-aer && \
    uv run --no-project python setup.py bdist_wheel && \
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
    uv run --no-project python -m pip install --break-system-packages .
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
    SCALUQ_USE_TEST=OFF SCALUQ_USE_EXE=OFF uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/scaluq

# install PennyLane + Lightning (lightning.qubit) and Lightning-Kokkos
# (lightning.kokkos). The PyPI x86_64 wheels are prebuilt with the OpenMP
# backend (no source build needed), and both honor OMP_NUM_THREADS.
RUN uv run python -m pip install --break-system-packages \
    "pennylane==${PENNYLANE_VERSION}" \
    "pennylane-lightning==${PENNYLANE_VERSION}" \
    "pennylane-lightning-kokkos==${PENNYLANE_VERSION}"

RUN uv run python -m pip install --break-system-packages matplotlib
