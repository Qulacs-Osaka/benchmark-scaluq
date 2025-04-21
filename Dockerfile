FROM nvidia/cuda:12.6.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    git

# python libraries
RUN pip install pytest pytest-benchmark mkl-service

# Quantum SDK
RUN pip install "qiskit==1.1.0" "qiskit-aer-gpu==0.15.1" cuquantum-cu12 qulacs pennylane-lightning
# RUN pip install scaluq

WORKDIR /workspace

# Install Scaluq
# RUN git clone https://github.com/qulacs/scaluq.git && \
#     cd /workspace/scaluq && \
#     script/configure && \
#     env "PATH=$PATH" ninja -C build install && \
#     cd /workspace && \
#     rm -rf /workspace/scaluq

