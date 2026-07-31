#include "scaluq/all.hpp"
#include <chrono>
#include <cstdint>
#include <cuda_runtime.h>
#include <fstream>
#include <iostream>
#include <map>
#include <numbers>
#include <random>
#include <string>
#include <tuple>
#include <vector>

#define CUDA_CHECK(err)                                                        \
  {                                                                            \
    cudaError_t e = err;                                                       \
    if (e != cudaSuccess) {                                                    \
      std::cerr << "CUDA Error: " << cudaGetErrorString(e) << " in "           \
                << __FILE__ << " at line " << __LINE__ << std::endl;           \
      exit(EXIT_FAILURE);                                                      \
    }                                                                          \
  }

struct BenchmarkConfig {
  std::uint64_t n_qubits = 16;
  std::uint64_t n_batches = 1024;
  std::uint64_t n_layers = 1;
  std::uint64_t n_iterations = 100;
  std::uint64_t seed = 0;
};

struct BenchmarkResult {
  float initialization_ms;
  float execution_ms;
  float per_iteration_total_ms;
};

// Build the circuit with per-batch parametric RX/RZ gates and the matching
// parameter map: each gate has its own key whose value is a length-B vector of
// distinct per-batch angles (the realistic batched-parametric workload).
template <scaluq::Precision Prec>
std::tuple<scaluq::Circuit<Prec>, std::map<std::string, std::vector<double>>>
create_benchmark_circuit(std::uint64_t n_qubits, std::uint64_t n_batches,
                         std::uint64_t n_layers, std::uint64_t seed) {
  scaluq::Circuit<Prec> circuit;
  std::map<std::string, std::vector<double>> params;
  std::mt19937 rng(seed);
  std::uniform_real_distribution<double> dist(0.0, 2.0 * M_PI);

  for (std::uint64_t layer = 0; layer < n_layers; ++layer) {
    for (std::uint64_t i = 0; i < n_qubits; ++i) {
      circuit.add_gate(scaluq::gate::CX<Prec>(i, (i + 1) % n_qubits));
      std::string rx_key =
          "rx_" + std::to_string(layer) + "_" + std::to_string(i);
      std::string rz_key =
          "rz_" + std::to_string(layer) + "_" + std::to_string(i);
      circuit.add_param_gate(scaluq::gate::ParamRX<Prec>(i), rx_key);
      circuit.add_param_gate(scaluq::gate::ParamRZ<Prec>(i), rz_key);
      std::vector<double> rx_vals(n_batches), rz_vals(n_batches);
      for (std::uint64_t b = 0; b < n_batches; ++b)
        rx_vals[b] = dist(rng);
      for (std::uint64_t b = 0; b < n_batches; ++b)
        rz_vals[b] = dist(rng);
      params.emplace(std::move(rx_key), std::move(rx_vals));
      params.emplace(std::move(rz_key), std::move(rz_vals));
    }
  }
  return {std::move(circuit), std::move(params)};
}

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
void run_benchmark(const scaluq::Circuit<Prec> &circuit,
                   scaluq::StateVectorBatched<Prec, Space> &states,
                   const std::map<std::string, std::vector<double>> &params,
                   std::uint64_t n_iterations = 1) {
  for (std::uint64_t i = 0; i < n_iterations; ++i) {
    // pass a fixed seed so the default std::random_device read is avoided
    circuit.update_quantum_state(states, params, std::uint64_t{0});
  }
}

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
auto initialize_benchmark(const BenchmarkConfig &config) {
  scaluq::StateVectorBatched<Prec, Space> states(config.n_batches,
                                                 config.n_qubits);
  auto [circuit, params] = create_benchmark_circuit<Prec>(
      config.n_qubits, config.n_batches, config.n_layers, config.seed);
  return std::make_tuple(std::move(states), std::move(circuit),
                         std::move(params));
}

int main(int argc, char *argv[]) {
  if (argc < 4) {
    std::cerr << "Usage: " << argv[0] << " <n_qubits> <n_batches> <csv_path>"
              << std::endl;
    std::cerr << "  <n_qubits> : positive integer (e.g., 4, 8, 16)"
              << std::endl;
    std::cerr << "  <n_batches>: positive integer (e.g., 1, 32, 1024)"
              << std::endl;
    std::cerr << "  <csv_path> : output CSV file" << std::endl;
    return EXIT_FAILURE;
  }

  scaluq::initialize();
  {
    Kokkos::fence();
    auto start_init = std::chrono::steady_clock::now();

    const auto n_qubits =
        static_cast<std::uint64_t>(std::strtoull(argv[1], nullptr, 10));
    const auto n_batches =
        static_cast<std::uint64_t>(std::strtoull(argv[2], nullptr, 10));
    BenchmarkResult result{};
    BenchmarkConfig config{n_qubits, n_batches, 1, 100, 0};

    constexpr scaluq::Precision Prec = scaluq::Precision::F64;
    constexpr scaluq::ExecutionSpace Space = scaluq::ExecutionSpace::Default;

    auto [states, circuit, params] = initialize_benchmark<Prec, Space>(config);
    Kokkos::fence();
    auto end_init = std::chrono::steady_clock::now();
    result.initialization_ms =
        std::chrono::duration<float, std::milli>(end_init - start_init).count();

    // Measure the update loop with CUDA events to get GPU-side timestamps
    // (no host-side overhead). Assumes Kokkos uses the default CUDA stream,
    // which is the default Scaluq/Kokkos configuration.
    cudaEvent_t ev_start, ev_stop;
    CUDA_CHECK(cudaEventCreate(&ev_start));
    CUDA_CHECK(cudaEventCreate(&ev_stop));
    Kokkos::fence();  // ensure initialization kernels finished before timing
    CUDA_CHECK(cudaEventRecord(ev_start));
    run_benchmark(circuit, states, params, config.n_iterations);
    CUDA_CHECK(cudaEventRecord(ev_stop));
    CUDA_CHECK(cudaEventSynchronize(ev_stop));
    CUDA_CHECK(cudaEventElapsedTime(&result.execution_ms, ev_start, ev_stop));
    CUDA_CHECK(cudaEventDestroy(ev_start));
    CUDA_CHECK(cudaEventDestroy(ev_stop));

    result.per_iteration_total_ms = (result.execution_ms + result.initialization_ms) / config.n_iterations;

    std::cout << "initialize time: " << result.initialization_ms << " [ms]"
              << std::endl;
    std::cout << "update time: " << result.execution_ms << " [ms]" << std::endl;
    std::cout << "total time: "
              << result.initialization_ms + result.execution_ms << " [ms]"
              << std::endl;

    std::string csv_path = argv[3];
    std::ofstream ofs(csv_path, std::ios::out | std::ios::app);
    if (!ofs) {
      std::cerr << "cannot open csv: " << csv_path << std::endl;
      return 1;
    }

    ofs << "scaluq" << ',' << config.n_qubits << ',' << config.n_batches << ','
        << config.n_iterations << ',' << config.seed << ','
        << result.per_iteration_total_ms << '\n';
  }
  scaluq::finalize();
}