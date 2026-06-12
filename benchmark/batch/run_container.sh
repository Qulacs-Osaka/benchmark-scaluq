# Build the image first (once):
#   docker build -f Dockerfile -t bench-scaluq .
docker run --rm -it --gpus all -v "$(pwd):/workspace" -w /workspace bench-scaluq
