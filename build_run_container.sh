#!/bin/bash

IMAGE_NAME=quantum-benchmarks

DIR="$(cd "$(dirname "$0")" && pwd)"

docker build -t $IMAGE_NAME "$DIR"

docker run --rm -it \
  --gpus all \
  -v "$DIR":/workspace \
  -w /workspace \
  $IMAGE_NAME \
  bash
