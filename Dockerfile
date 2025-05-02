FROM nvidia/cuda:12.6.3-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 python3-pip \
    git cmake make

#install tools for benchmark
RUN pip install numpy pytest pytest-benchmark mkl-service

# install qiskit
RUN pip install "qiskit==1.1.0" "qiskit-aer-gpu==0.15.1" cuquantum-cu12 qulacs

# install pennylane-lightning
RUN pip install custatevec-cu12 pennylane-lightning-gpu

# install scaluq
# RUN pip install scaluq 

WORKDIR /workspace

# Install Scaluq
# RUN git clone https://github.com/qulacs/scaluq.git && \
#     cd /workspace/scaluq && \
#     script/configure && \
#     env "PATH=$PATH" ninja -C build install && \
#     cd /workspace && \
#     rm -rf /workspace/scaluq

