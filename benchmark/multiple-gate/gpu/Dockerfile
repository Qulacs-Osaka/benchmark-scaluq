FROM nvidia/cuda:12.6.3-devel-ubuntu24.04

ENV DEBIAN_FRONTEND=noninteractive

# Pinned versions, matching the CPU (multithread) Dockerfile so the same library
# versions are compared on CPU and GPU (override with --build-arg to bump).
ARG QISKIT_AER_COMMIT=837c3ef3c39248aae936580360c22224dcefb265
ARG QULACS_COMMIT=4f6de32cca807ec4cabf1107e3806786cb953c56
ARG SCALUQ_COMMIT=025565d2fef0ce260692d61d08b21bf1f7491ffd
ARG PENNYLANE_VERSION=0.45.0
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

# Build and install Qiskit Aer with its standard CUDA backend.
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    libopenblas-dev \
    zlib1g-dev
RUN uv run python -m pip install cmake "conan<2.0.0" scikit-build pybind11 --break-system-packages
RUN git clone https://github.com/qiskit/qiskit-aer /tmp/qiskit-aer
RUN git -C /tmp/qiskit-aer checkout "${QISKIT_AER_COMMIT}"
RUN cd /tmp/qiskit-aer && \
    uv run --no-project python setup.py bdist_wheel -- -DAER_THRUST_BACKEND=CUDA -DAER_CUDA_ARCH="8.0" && \
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

# install PennyLane Lightning-GPU (cuStateVec) from its prebuilt wheel.
# NOTE: Lightning-Kokkos with the Kokkos CUDA backend was dropped -- building it
# from source did not finish in a reasonable time (Kokkos CUDA kernel
# compilation), and Scaluq already represents a Kokkos-CUDA implementation on
# GPU, so the lightning.kokkos-CUDA curve would be largely redundant.
RUN uv run python -m pip install --break-system-packages \
    "pennylane==${PENNYLANE_VERSION}" \
    "pennylane-lightning==${PENNYLANE_VERSION}" \
    "pennylane-lightning-gpu==${PENNYLANE_VERSION}"
#
# # install QuEST
# RUN git clone https://github.com/rrmeister/pyquest -b develop --depth=1 --recursive /tmp/pyquest
# RUN cd /tmp/pyquest && \
#     sed -i -e "s/'multithreaded': True,/'multithreaded': False,/" -e "s/'gpu_accelerated': False,/'gpu_accelerated': True,/" -e "s/'gpu_compute_capability': None,/'gpu_compute_capability': 80,/" setup.py && \
#     uv run --no-project python -m pip install --break-system-packages .
#     

RUN uv run python -m pip install --break-system-packages matplotlib
