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
RUN git clone https://github.com/qulacs/scaluq --depth=1 /tmp/scaluq
RUN apt-get update
RUN apt-get install -y \
    build-essential \
    cmake \
    ninja-build
RUN cd /tmp/scaluq && \
    CALUQ_USE_TEST=OFF SCALUQ_USE_EXE=OFF SCALUQ_FLOAT16=ON SCALUQ_BFLOAT16=ON uv run --no-project python -m pip install --break-system-packages .
RUN rm -r /tmp/scaluq

# 
# # install QuEST
# RUN git clone https://github.com/rrmeister/pyquest -b develop --depth=1 --recursive /tmp/pyquest
# RUN cd /tmp/pyquest && \
#     sed -i -e "s/'multithreaded': True,/'multithreaded': False,/" -e "s/'gpu_accelerated': False,/'gpu_accelerated': True,/" -e "s/'gpu_compute_capability': None,/'gpu_compute_capability': 80,/" setup.py && \
#     uv run --no-project python -m pip install --break-system-packages .
#     

ENV LD_LIBRARY_PATH /opt/nvidia/cuquantum/lib/12:/opt/nvidia/cutensor/lib/12:$LD_LIBRARY_PATH

RUN uv run python -m pip install --break-system-packages matplotlib
