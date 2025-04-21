FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    git curl

#install tools for benchmark
RUN pip install pytest pytest-benchmark

# install qiskit
RUN pip install qiskit qiskit-aer cuquantum-cu12 qulacs

# install pennylane-lightning
RUN pip install custatevec-cu12 pennylane-lightning-gpu

# install scaluq
# RUN pip install scaluq 

WORKDIR /workspace
