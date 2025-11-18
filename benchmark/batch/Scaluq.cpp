#include <iostream>
#include <vector>
#include <string>
#include <fstream>
#include <chrono>
#include <random>
#include <tuple>
#include <numbers>
#include <cstdint>
#include "scaluq/all.hpp"

#define CUDA_CHECK(err)                                                                                                         \
    {                                                                                                                           \
        cudaError_t e = err;                                                                                                    \
        if (e != cudaSuccess)                                                                                                   \
        {                                                                                                                       \
            std::cerr << "CUDA Error: " << cudaGetErrorString(e) << " in " << __FILE__ << " at line " << __LINE__ << std::endl; \
            exit(EXIT_FAILURE);                                                                                                 \
        }                                                                                                                       \
    }

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
    std::uniform_real_distribution<double> dist(0.0, 2.0 * M_PI);

    for (std::uint64_t layer = 0; layer < n_layers; ++layer)
    {
        for (std::uint64_t i = 0; i < n_qubits; ++i)
        {
            circuit.add_gate(scaluq::gate::CX<Prec, Space>(i, (i + 1) % n_qubits));
            circuit.add_gate(scaluq::gate::RX<Prec, Space>(i, dist(rng)));
            circuit.add_gate(scaluq::gate::RZ<Prec, Space>(i, dist(rng)));
        }
    }
    return std::move(circuit);
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

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
auto initialize_benchmark(const BenchmarkConfig &config)
{
    scaluq::StateVectorBatched<Prec, Space> states(config.n_batches, config.n_qubits);
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

    scaluq::initialize();
    {
        Kokkos::fence();
        auto start_init = std::chrono::steady_clock::now();

        const auto n_qubits = static_cast<std::uint64_t>(std::strtoull(argv[1], nullptr, 10));
        const auto n_batches = static_cast<std::uint64_t>(std::strtoull(argv[2], nullptr, 10));
        BenchmarkResult result{};
        BenchmarkConfig config{n_qubits, n_batches, 1, 100, 0};

        constexpr scaluq::Precision Prec = scaluq::Precision::F64;
        constexpr scaluq::ExecutionSpace Space = scaluq::ExecutionSpace::Default;

        auto [states, circuit] = initialize_benchmark<Prec, Space>(config);
        Kokkos::fence();
        auto end_init = std::chrono::steady_clock::now();
        result.initialization_ms = std::chrono::duration<float, std::milli>(end_init - start_init).count();

        Kokkos::fence();
        auto start_upd = std::chrono::steady_clock::now();
        run_benchmark(circuit, states, config.n_iterations);
        Kokkos::fence();
        auto end_upd = std::chrono::steady_clock::now();
        result.execution_ms = std::chrono::duration<float, std::milli>(end_upd - start_upd).count();

        result.per_iteration_ms = result.execution_ms / config.n_iterations;

        std::cout << "initialize time: " << result.initialization_ms << " [ms]" << std::endl;
        std::cout << "update time: " << result.execution_ms << " [ms]" << std::endl;
        std::cout << "total time: " << result.initialization_ms + result.execution_ms << " [ms]" << std::endl;

        std::string csv_path = argv[3];
        std::ofstream ofs(csv_path, std::ios::out | std::ios::app);
        if (!ofs)
        {
            std::cerr << "cannot open csv: " << csv_path << std::endl;
            return 1;
        }

        ofs << "scaluq" << ','
            << config.n_qubits << ','
            << config.n_batches << ','
            << config.n_iterations << ','
            << config.seed << ','
            << result.per_iteration_ms << '\n';
    }
    scaluq::finalize();
}