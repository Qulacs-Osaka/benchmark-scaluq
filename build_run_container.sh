#!/bin/bash

if [ $# -lt 1 ]; then
  echo "Usage: $0 <Dockerfile>"
  exit 1
fi

DOCKERFILE_PATH="$1"

if [ ! -f "$DOCKERFILE_PATH" ]; then
  echo "Error: Dockerfile '$DOCKERFILE_PATH' not found."
  exit 1
fi

DIR="$(cd "$(dirname "$DOCKERFILE_PATH")" && pwd)"
FILENAME="$(basename "$DOCKERFILE_PATH")"
TAG_SUFFIX="$(echo "$FILENAME" | sed -E 's/^Dockerfile\.?//; s/[^a-zA-Z0-9]+/-/g' | tr '[:upper:]' '[:lower:]')"
IMAGE_NAME="quantum-benchmark${TAG_SUFFIX:+-$TAG_SUFFIX}"

echo "Building image: $IMAGE_NAME from $DOCKERFILE_PATH"

docker build --network=host -t "$IMAGE_NAME" -f "$DOCKERFILE_PATH" "$DIR"

docker run --rm -it \
  --gpus all \
  -v "$DIR":/workspace \
  -w /workspace \
  "$IMAGE_NAME" \
  bash
