// scaluq　two-qubit-dense-matrix-gateのベンチマークを測定するためのコード
#include <iostream>
#include <vector>
#include <string>    // std::string
#include <fstream>   // std::ofstream
#include <random>    // std::mt19937, std::uniform_real_distribution
#include <chrono>    // std::chrono
#include <cmath>     // M_PI
#include <cstdlib>   // std::strtol, EXIT_FAILURE
#include <algorithm> // std::max

#include "scaluq/all.hpp"

#ifdef SCALUQ_USE_CUDA // scaluq が CUDA を使う場合にのみ有効
#include <cuda_runtime.h>
#define CUDA_CHECK(err)                                                                                                         \
    {                                                                                                                           \
        cudaError_t e = err;                                                                                                    \
        if (e != cudaSuccess)                                                                                                   \
        {                                                                                                                       \
            std::cerr << "CUDA Error: " << cudaGetErrorString(e) << " in " << __FILE__ << " at line " << __LINE__ << std::endl; \
            exit(EXIT_FAILURE);                                                                                                 \
        }                                                                                                                       \
    }
#else
#define CUDA_CHECK(err) // CUDA がない場合は何もしない
#endif

struct BenchmarkConfig
{
    std::uint64_t n_qubits = 16;
    std::uint64_t n_batches = 1024;
    std::uint64_t n_layers = 1;
    std::uint64_t n_iterations = 100;
    std::uint64_t seed = 0;
};

struct BenchmarkResult
{
    float initialization_ms;
    float execution_ms;
    float per_iteration_ms;
};

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
scaluq::Circuit<Prec, Space> create_benchmark_circuit(
    std::uint64_t n_qubits,
    std::uint64_t n_layers,
    std::uint64_t seed)
{
    scaluq::Circuit<Prec, Space> circuit(n_qubits);
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> dist_angle(0.0, 2.0 * M_PI);
    std::uniform_int_distribution<std::uint64_t> dist_qubit(0, n_qubits - 1);

    for (std::uint64_t layer = 0; layer < n_layers; ++layer)
    {
        if (n_qubits > 1)
        {
            // n_qubits / 2 回 SWAP を追加 (ランダムなペア)
            for (std::uint64_t i = 0; i < n_qubits / 2; ++i)
            {
                std::uint64_t q0 = dist_qubit(rng);
                std::uint64_t q1 = dist_qubit(rng);
                while (q0 == q1)
                    q1 = dist_qubit(rng);

                circuit.add_gate(scaluq::gate::Swap<Prec, Space>(q0, q1));
            }
        }
    }
    return std::move(circuit); // RVO (Return Value Optimization) またはムーブ
}

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
void run_benchmark(
    const scaluq::Circuit<Prec, Space> &circuit,
    scaluq::StateVectorBatched<Prec, Space> &states,
    std::uint64_t n_iterations = 1)
{
    for (std::uint64_t i = 0; i < n_iterations; ++i)
    {
        circuit.update_quantum_state(states);
    }
}

// ベンチマーク初期化
template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
auto initialize_benchmark(const BenchmarkConfig &config)
{
    scaluq::StateVectorBatched<Prec, Space> states(config.n_batches, config.n_qubits);
    states.set_zero_state();
    auto circuit = create_benchmark_circuit<Prec, Space>(config.n_qubits, config.n_layers, config.seed);
    return std::make_tuple(std::move(states), std::move(circuit));
}

int main(int argc, char *argv[])
{
    if (argc < 4)
    {
        std::cerr << "Usage: " << argv[0] << " <n_qubits> <n_batches> <csv_path>" << std::endl;
        std::cerr << "  <n_qubits> : positive integer (e.g., 4, 8, 16)" << std::endl;
        std::cerr << "  <n_batches>: positive integer (e.g., 1, 32, 1024)" << std::endl;
        std::cerr << "  <csv_path> : output CSV file" << std::endl;
        return EXIT_FAILURE;
    }

    scaluq::initialize(); // Kokkos の初期化
    {
        Kokkos::fence(); // 同期
        auto start_init = std::chrono::steady_clock::now();

        BenchmarkResult result{};
        // コマンドライン引数をパース
        BenchmarkConfig config{
            static_cast<std::uint64_t>(std::strtol(argv[1], nullptr, 10)),
            static_cast<std::uint64_t>(std::strtol(argv[2], nullptr, 10)),
            1,   // n_layers (固定)
            100, // n_iterations (固定)
            0    // seed (固定)
        };

        // config の値が不正な場合のチェック（簡易）
        if (config.n_qubits == 0 || config.n_batches == 0)
        {
            std::cerr << "n_qubits and n_batches must be positive." << std::endl;
            return EXIT_FAILURE;
        }

        std::cout << "Config: n_qubits=" << config.n_qubits
                  << ", n_batches=" << config.n_batches
                  << ", n_layers=" << config.n_layers
                  << ", n_iterations=" << config.n_iterations
                  << ", seed=" << config.seed << std::endl;

        constexpr scaluq::Precision Prec = scaluq::Precision::F64;
        constexpr scaluq::ExecutionSpace Space = scaluq::ExecutionSpace::Default;

        auto [states, circuit] = initialize_benchmark<Prec, Space>(config);

        Kokkos::fence(); // 初期化完了を同期
        auto end_init = std::chrono::steady_clock::now();
        result.initialization_ms = std::chrono::duration<float, std::milli>(end_init - start_init).count();

        // ウォームアップ（オプションだが推奨）
        run_benchmark(circuit, states, 1);

        Kokkos::fence(); // 実行開始前に同期
        auto start_upd = std::chrono::steady_clock::now();

        run_benchmark(circuit, states, config.n_iterations);

        Kokkos::fence(); // 実行完了を同期
        auto end_upd = std::chrono::steady_clock::now();
        result.execution_ms = std::chrono::duration<float, std::milli>(end_upd - start_upd).count();

        // 1イテレーションあたりの平均実行時間
        result.per_iteration_ms = result.execution_ms / std::max(static_cast<std::uint64_t>(1), config.n_iterations);

        std::cout << "Initialization time: " << result.initialization_ms << " [ms]" << std::endl;
        std::cout << "Execution time (" << config.n_iterations << " iterations): " << result.execution_ms << " [ms]" << std::endl;
        std::cout << "Time per iteration: " << result.per_iteration_ms << " [ms]" << std::endl;

        // CSVファイルへの書き込み
        std::string csv_path = argv[3];
        std::ofstream ofs(csv_path, std::ios::out | std::ios::app);
        if (!ofs)
        {
            std::cerr << "Cannot open csv: " << csv_path << std::endl;
        }
        else
        {
            // ヘッダ（ファイルが空の場合）
            ofs.seekp(0, std::ios::end);
            if (ofs.tellp() == 0)
            {
                ofs << "backend,n_qubits,n_batches,n_iterations,seed,per_iteration_ms\n";
            }

            // "scaluq_range" のような識別子に変更（MDRange版と比較するため）
            ofs << "scaluq_range" << ','
                << config.n_qubits << ','
                << config.n_batches << ','
                << config.n_iterations << ','
                << config.seed << ','
                << result.per_iteration_ms << '\n';
            ofs.close();
            std::cout << "Result appended to " << csv_path << std::endl;
        }
    }
    scaluq::finalize(); // Kokkos の終了処理
    return 0;
}