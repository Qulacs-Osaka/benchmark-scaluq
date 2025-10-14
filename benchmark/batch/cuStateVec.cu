#include <cuda_runtime_api.h> // cudaMalloc, cudaMemcpy, etc.
#include <cuComplex.h>        // cuDoubleComplex
#include <custatevec.h>       // custatevecApplyMatrix
#include <stdio.h>            // printf
#include <stdlib.h>           // EXIT_FAILURE
#include <random>             // std::random_device, std::mt19937, std::uniform_real_distribution
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

// batch個のRXゲートを作る関数
// matricesはn_batches*4のサイズであることを要求
void make_rx(cuDoubleComplex (*matrices)[4], std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        matrices[i][0] = {cos(angle), 0};
        matrices[i][1] = {0, -sin(angle)};
        matrices[i][2] = {0, -sin(angle)};
        matrices[i][3] = {cos(angle), 0};
    }
}

// batch個のRZゲートを作る関数
void make_rz(cuDoubleComplex (*matrices)[4], std::vector<double> angles)
{
    for (int i = 0; i < angles.size(); i++)
    {
        double angle = angles[i] / 2.;
        matrices[i][0] = {cos(angle), -sin(angle)};
        matrices[i][1] = matrices[i][2] = {0, 0};
        matrices[i][3] = {cos(angle), sin(angle)};
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
    auto start_init = std::chrono::steady_clock::now();
    // 各種パラメータ設定＋ベクトル・行列の初期化
    const int n_qubits = 16;
    const int n_layers = 1;
    const int dim = (1 << n_qubits);
    const int n_targets = 1;
    const int n_controls = 1;
    const int n_batches = 1024;
    int target_index[1];
    int control_index[1];
    const int control_value[1] = {1};

    // cuDoubleComplex h_states[n_batches * dim];
    // initialize_states(h_states, n_qubits, n_batches);
    cuDoubleComplex *d_states;
    CUDA_CHECK(cudaMalloc((void **)&d_states, n_batches * dim * sizeof(cuDoubleComplex)));
    // CUDA_CHECK(cudaMemcpy(d_states, h_states, n_batches * dim * sizeof(cuDoubleComplex), cudaMemcpyHostToDevice));
    CUDA_CHECK(cudaMemset(d_states, 0, (size_t)n_batches*dim*sizeof(cuDoubleComplex)));
    {
        int threads=256, blocks=(n_batches+threads-1)/threads;
        set_basis0_heads<<<blocks, threads>>>(d_states, (size_t)dim, n_batches);
        CUDA_CHECK(cudaGetLastError());
        CUDA_CHECK(cudaDeviceSynchronize());
    }

    static custatevecHandle_t handle;
    custatevecCreate(&handle);

    cuDoubleComplex x_matrix[4] = {{0, 0}, {1, 0}, {1, 0}, {0, 0}};
    int mat_indices[n_batches];
    for (int i = 0; i < n_batches; i++)
        mat_indices[i] = i;
    cuDoubleComplex pxs[n_layers * n_qubits][n_batches][4];
    cuDoubleComplex pzs[n_layers * n_qubits][n_batches][4];
    std::random_device rd;
    std::mt19937 mt(rd());
    std::uniform_real_distribution<double> distribution(0.0, 2.0 * M_PI);
    std::vector<double> angles1(n_batches), angles2(n_batches);
    for (int i = 0; i < n_layers * n_qubits; i++)
    {
        for (int j = 0; j < n_batches; j++)
        {
            angles1[j] = distribution(mt);
            angles2[j] = distribution(mt);
        }
        make_rx(pxs[i], angles1);
        make_rz(pzs[i], angles2);
    }

    void *extra_workspace_cx = nullptr;
    void *extra_workspace_param = nullptr;
    size_t extra_workspace_size_in_bytes_cx = 0;
    size_t extra_workspace_size_in_bytes_param = 0;
    // CX: check the size of external workspace
    custatevecApplyMatrixBatchedGetWorkspaceSize(
        handle,
        CUDA_C_64F,
        n_qubits,
        n_batches,
        dim,
        CUSTATEVEC_MATRIX_MAP_TYPE_BROADCAST,
        nullptr,
        x_matrix,
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        false,
        n_batches,
        n_targets,
        n_controls,
        CUSTATEVEC_COMPUTE_64F,
        &extra_workspace_size_in_bytes_cx);
    if (extra_workspace_size_in_bytes_cx > 0)
        CUDA_CHECK(cudaMalloc(&extra_workspace_cx, extra_workspace_size_in_bytes_cx));

    // ParamRX, ParamRZ: check the size of external workspace
    custatevecApplyMatrixBatchedGetWorkspaceSize(
        handle,
        CUDA_C_64F,
        n_qubits,
        n_batches,
        dim,
        CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
        mat_indices,
        pxs[0],
        CUDA_C_64F,
        CUSTATEVEC_MATRIX_LAYOUT_ROW,
        false,
        n_batches,
        n_targets,
        0, // n_controls for parametric gate is 0
        CUSTATEVEC_COMPUTE_64F,
        &extra_workspace_size_in_bytes_param);
    if (extra_workspace_size_in_bytes_param > 0)
        CUDA_CHECK(cudaMalloc(&extra_workspace_param, extra_workspace_size_in_bytes_param));

    auto end_init = std::chrono::steady_clock::now();
    std::chrono::duration<float> diff_init = end_init - start_init;
    std::cout << "initialize time: " << diff_init.count() << " [ms]" << std::endl;

    cudaEvent_t start_upd, end_upd;
    cudaEventCreate(&start_upd);
    cudaEventCreate(&end_upd);

    // start measuring update
    cudaEventRecord(start_upd);

    for (int layer = 0; layer < n_layers; layer++)
    {
        for (int q = 0; q < n_qubits; q++)
        {
            // apply CX
            target_index[0] = (q + 1) % n_qubits;
            control_index[0] = q;
            custatevecApplyMatrixBatched(
                handle,
                d_states,
                CUDA_C_64F,
                n_qubits,
                n_batches,
                dim,
                CUSTATEVEC_MATRIX_MAP_TYPE_BROADCAST,
                nullptr,
                x_matrix,
                CUDA_C_64F,
                CUSTATEVEC_MATRIX_LAYOUT_ROW,
                false,
                n_batches,
                target_index,
                n_targets,
                control_index,
                control_value,
                n_controls,
                CUSTATEVEC_COMPUTE_64F,
                extra_workspace_cx,
                extra_workspace_size_in_bytes_cx);

            // apply ParamRX
            target_index[0] = q;
            custatevecApplyMatrixBatched(
                handle,
                d_states,
                CUDA_C_64F,
                n_qubits,
                n_batches,
                dim,
                CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
                mat_indices,
                pxs[layer * n_qubits + q],
                CUDA_C_64F,
                CUSTATEVEC_MATRIX_LAYOUT_ROW,
                false,
                n_batches,
                target_index,
                n_targets,
                nullptr,
                nullptr,
                0, // n_controls for parametric gate is 0
                CUSTATEVEC_COMPUTE_64F,
                extra_workspace_param,
                extra_workspace_size_in_bytes_param);

            // apply ParamRZ
            custatevecApplyMatrixBatched(
                handle,
                d_states,
                CUDA_C_64F,
                n_qubits,
                n_batches,
                dim,
                CUSTATEVEC_MATRIX_MAP_TYPE_MATRIX_INDEXED,
                mat_indices,
                pzs[layer * n_qubits + q],
                CUDA_C_64F,
                CUSTATEVEC_MATRIX_LAYOUT_ROW,
                false,
                n_batches,
                target_index,
                n_targets,
                nullptr,
                nullptr,
                0, // n_controls for parametric gate is 0
                CUSTATEVEC_COMPUTE_64F,
                extra_workspace_param,
                extra_workspace_size_in_bytes_param);
        }
    }

    // end measuring update
    cudaEventRecord(end_upd);
    CUDA_CHECK(cudaEventSynchronize(end_upd));
    float diff_upd = 0;
    cudaEventElapsedTime(&diff_upd, start_upd, end_upd);
    std::cout << "update time: " << diff_upd << " [ms]" << std::endl;
    std::cout << "total time: " << diff_init.count() + diff_upd << " [ms]" << std::endl;

    // free resources
    if (extra_workspace_size_in_bytes_cx)
        cudaFree(extra_workspace_cx);
    if (extra_workspace_size_in_bytes_param)
        cudaFree(extra_workspace_param);
    custatevecDestroy(handle);
    cudaFree(d_states);
}
