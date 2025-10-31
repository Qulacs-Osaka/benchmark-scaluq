#include <cuda_runtime_api.h>
#include <cuComplex.h>
#include <custatevec.h>
#include <stdio.h>
#include <stdlib.h>
#include <random>
#include <chrono>
#include <iostream>
#include <vector>
#include <cmath>

#define CUDA_CHECK(err)                                                                                                         \
    {                                                                                                                           \
        cudaError_t e = err;                                                                                                    \
        if (e != cudaSuccess)                                                                                                   \
        {                                                                                                                       \
            std::cerr << "CUDA Error: " << cudaGetErrorString(e) << " in " << __FILE__ << " at line " << __LINE__ << std::endl; \
            exit(EXIT_FAILURE);                                                                                                 \
        }                                                                                                                       \
    }

void make_rx(cuDoubleComplex (*matrix)[4], std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        (*matrix)[0] = {cos(angle), 0};
        (*matrix)[1] = {0, -sin(angle)};
        (*matrix)[2] = {0, -sin(angle)};
        (*matrix)[3] = {cos(angle), 0};
    }
}

void make_rz(cuDoubleComplex (*matrix)[4], std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        (*matrix)[0] = {cos(angle), -sin(angle)};
        (*matrix)[1] = (*matrix)[2] = {0, 0};
        (*matrix)[3] = {cos(angle), sin(angle)};
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

__global__ void set_basis0_heads(cuDoubleComplex* states, size_t dim, int n_batches){
  int b = blockIdx.x*blockDim.x + threadIdx.x;
  if(b < n_batches){
    states[static_cast<size_t>(b)*dim + 0] = make_cuDoubleComplex(1.0, 0.0);
  }
}

int main()
{
    static custatevecHandle_t handle;
    custatevecCreate(&handle);
    cudaDeviceSynchronize();

    auto start_init = std::chrono::steady_clock::now();

    const int n_qubits = 26;
    const int n_layers = 100;
    const int dim = (1 << n_qubits);
    const int n_targets = 1;
    const int n_controls = 1;
    const int n_batches = 1;
    int target_index[1];
    int control_index[1];
    const int control_value[1] = {1};

    cuDoubleComplex *d_states;
    CUDA_CHECK(cudaMalloc((void **)&d_states, n_batches * dim * sizeof(cuDoubleComplex)));
    CUDA_CHECK(cudaMemset(d_states, 0, (size_t)n_batches*dim*sizeof(cuDoubleComplex)));
    {
        int threads=128, blocks=(n_batches+threads-1)/threads;
        set_basis0_heads<<<blocks, threads>>>(d_states, (size_t)dim, n_batches);
        CUDA_CHECK(cudaGetLastError());
    }

    cuDoubleComplex x_matrix[4] = {{0, 0}, {1, 0}, {1, 0}, {0, 0}};
    cuDoubleComplex pxs[n_layers * n_qubits][4];
    cuDoubleComplex pzs[n_layers * n_qubits][4];
    std::random_device rd;
    std::uint64_t seed = 0;
    std::mt19937 mt(seed);
    std::uniform_real_distribution<double> distribution(0.0, 2.0 * M_PI);
    std::vector<double> angles1(1), angles2(1);
    for (int i = 0; i < n_layers * n_qubits; i++)
    {
        angles1[0] = distribution(mt);
        angles2[0] = distribution(mt);
        make_rx(&pxs[i], angles1);
        make_rz(&pzs[i], angles2);
    }

    void *extra_workspace_cx = nullptr;
    void *extra_workspace_param = nullptr;
    size_t extra_workspace_size_in_bytes_cx = 0;
    size_t extra_workspace_size_in_bytes_param = 0;

    custatevecApplyMatrixGetWorkspaceSize(
        handle,
        CUDA_C_64F,
        n_qubits,
        x_matrix,
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        0,
        n_targets,
        n_controls,
        CUSTATEVEC_COMPUTE_64F,
        &extra_workspace_size_in_bytes_cx);
    if (extra_workspace_size_in_bytes_cx > 0)
        CUDA_CHECK(cudaMalloc(&extra_workspace_cx, extra_workspace_size_in_bytes_cx));

    custatevecApplyMatrixGetWorkspaceSize(
        handle,
        CUDA_C_64F,
        n_qubits,
        pxs[0],
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        0,
        n_targets,
        0,
        CUSTATEVEC_COMPUTE_64F,
        &extra_workspace_size_in_bytes_param);
    if (extra_workspace_size_in_bytes_param > 0)
        CUDA_CHECK(cudaMalloc(&extra_workspace_param, extra_workspace_size_in_bytes_param));

    cudaDeviceSynchronize();
    auto end_init = std::chrono::steady_clock::now();
    float diff_init = std::chrono::duration<float, std::milli>(end_init-start_init).count();

    cudaDeviceSynchronize();
    auto start_upd = std::chrono::steady_clock::now();

    for (int layer = 0; layer < n_layers; layer++)
    {
        for (int q = 0; q < n_qubits; q++)
        {
            // target_index[0] = (q + 1) % n_qubits;
            // control_index[0] = q;
            // custatevecApplyMatrix(
            //     handle,
            //     d_states,
            //     CUDA_C_64F,
            //     n_qubits,
            //     x_matrix,
            //     CUDA_C_64F,
            //     CUSTATEVEC_MATRIX_LAYOUT_ROW,
            //     0,
            //     target_index,
            //     n_targets,
            //     control_index,
            //     control_value,
            //     n_controls,
            //     CUSTATEVEC_COMPUTE_64F,
            //     extra_workspace_cx,
            //     extra_workspace_size_in_bytes_cx);

            target_index[0] = q;
            custatevecApplyMatrix(
                handle,
                d_states,
                CUDA_C_64F,
                n_qubits,
                pxs[layer * n_qubits + q],
                CUDA_C_64F,
                CUSTATEVEC_MATRIX_LAYOUT_ROW,
                0,
                target_index,
                n_targets,
                nullptr,
                nullptr,
                0,
                CUSTATEVEC_COMPUTE_64F,
                extra_workspace_param,
                extra_workspace_size_in_bytes_param);

            // custatevecApplyMatrix(
            //     handle,
            //     d_states,
            //     CUDA_C_64F,
            //     n_qubits,
            //     pzs[layer * n_qubits + q],
            //     CUDA_C_64F,
            //     CUSTATEVEC_MATRIX_LAYOUT_ROW,
            //     0,
            //     target_index,
            //     n_targets,
            //     nullptr,
            //     nullptr,
            //     0,
            //     CUSTATEVEC_COMPUTE_64F,
            //     extra_workspace_param,
            //     extra_workspace_size_in_bytes_param);
        }
    }

    cudaDeviceSynchronize();
    auto end_upd = std::chrono::steady_clock::now();
    float diff_upd = std::chrono::duration<double, std::milli>(end_upd - start_upd).count();

    std::cout << "initialize time: " << diff_init << " [ms]" << std::endl;
    std::cout << "update time: " << diff_upd << " [ms]" << std::endl;
    std::cout << "total time: " << diff_init + diff_upd << " [ms]" << std::endl;

    cuDoubleComplex* h_states = nullptr;
    CUDA_CHECK(cudaMallocHost(&h_states, static_cast<size_t>(n_batches)*dim*sizeof(cuDoubleComplex)));
    cudaMemcpy(h_states, d_states, n_batches*dim* sizeof(cuDoubleComplex),
               cudaMemcpyDeviceToHost);
    std::cout << "=== Check ===" << std::endl;
    for(int i=0;i<5;i++){
        std::cout <<"(" << h_states[i].x << ", " << h_states[i].y << ")" << std::endl;
    }

    if (extra_workspace_size_in_bytes_cx)
        cudaFree(extra_workspace_cx);
    if (extra_workspace_size_in_bytes_param)
        cudaFree(extra_workspace_param);
    cudaFree(d_states);
    custatevecDestroy(handle);
}
