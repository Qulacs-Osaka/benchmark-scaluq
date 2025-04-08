FROM nvidia/cuda:12.2.0-devel-ubuntu22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    git curl

# Qiskit Aer
RUN pip install qiskit qiskit-aer cuquantum-cu12 qulacs pennylane-lightning pytest

# RUN pip install scaluq 

WORKDIR /workspace
