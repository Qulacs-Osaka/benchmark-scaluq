#include <cuda_runtime_api.h> // cudaMalloc, cudaMemcpy, etc.
#include <cuComplex.h>        // cuDoubleComplex
#include <custatevec.h>       // custatevecApplyMatrix
#include <stdio.h>            // printf
#include <stdlib.h>           // EXIT_FAILURE
#include <random>             // std::random_device, std::mt19937, std::uniform_real_distribution
#include <chrono>
#include <iostream>
#include <vector>

// batch個のゲートを作る関数
void make_rx(cuDoubleComplex *matrices, std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        matrices[4 * i + 0] = {cos(angle), 0};
        matrices[4 * i + 1] = {0, -sin(angle)};
        matrices[4 * i + 2] = {0, -sin(angle)};
        matrices[4 * i + 3] = {cos(angle), 0};
    }
}

void make_rz(cuDoubleComplex *matrices, std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        matrices[4 * i + 0] = {cos(angle), -sin(angle)};
        matrices[4 * i + 1] = matrices[4 * i + 2] = {0, 0};
        matrices[4 * i + 3] = {cos(angle), sin(angle)};
    }
}

void initialize_states(cuDoubleComplex *states, int n_qubits, int n_batches)
{
    int dim = 1 << n_qubits;
    for (int i = 0; i < n_batches; i++)
    {
        cuDoubleComplex *head = states + i * dim;
        head[0] = {1, 0};
        for (int j = 1; j < dim; j++)
        {
            head[j] = {0, 0};
        }
    }
}

int main()
{
    const int n_qubits = 3;
    const int dim = (1 << n_qubits);
    const int n_targets = 1;
    const int n_controls = 1;
    const int n_batches = 10;

    cuDoubleComplex h_states[n_batches * dim];
    initialize_states(h_states, n_qubits, n_batches);
    cuDoubleComplex *d_states;
    cudaMalloc((void **)&d_states, n_batches * n_qubits * sizeof(cuDoubleComplex));
    cudaMemcpy(d_states, h_states, n_batches * n_qubits * sizeof(cuDoubleComplex), cudaMemcpyHostToDevice);

    static custatevecHandle_t handle;
    custatevecCreate(&handle);

    void *extra_workspace = nullptr;
    size_t extra_workspace_size_in_bytes = 0;
    int mat_indices[n_batches];
    for (int i = 0; i < n_batches; i++)
        mat_indices[i] = i;
    cuDoubleComplex *matrices[n_batches];
    int targets[] = {0};
    cuDoubleComplex cnot_matrix[4] = {{0, 0}, {1, 0}, {1, 0}, {0, 0}};
    std::vector<double>

        auto start = std::chrono::steady_clock::now();

    // check the size of external workspace
    custatevecApplyMatrixBatchedGetWorkspaceSize(
        handle,
        CUDA_C_64F,
        n_qubits,
        n_batches,
        dim,
        CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
        mat_indices,
        matrices,
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        false,
        n_batches,
        n_targets,
        n_controls,
        CUSTATEVEC_COMPUTE_64F,
        &extra_workspace_size_in_bytes);

    if (extra_workspace_size_in_bytes > 0)
        cudaMalloc(&extra_workspace, extra_workspace_size_in_bytes);

    custatevecApplyMatrixBatched(
        handle,
        d_states,
        CUDA_C_64F,
        n_qubits,
        n_batches,
        dim,
        CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
        mat_indices,
        matrices,
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        false,
        n_batches,
        targets,
        n_targets,
        nullptr,
        nullptr,
        n_controls,
        CUSTATEVEC_COMPUTE_64F,
        extra_workspace,
        extra_workspace_size_in_bytes);

    if (extra_workspace_size_in_bytes)
        cudaFree(extra_workspace);

    auto end = std::chrono::steady_clock::now();

    std::cout << "collapse time: " << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count() << " [ms]" << std::endl;

    std::random_device seed_gen;
    std::mt19937 mt_engine(seed_gen());
    std::uniform_real_distribution<double> dist;
}
