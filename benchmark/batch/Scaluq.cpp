#include <iostream>
#include <vector>
#include "scaluq/all.hpp"

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
void add_gates(scaluq::Circuit<Prec, Space> &circuit, const std::uint64_t seed)
{

    return;
}

template <scaluq::Precision Prec, scaluq::ExecutionSpace Space>
void run_bench(const std::uint64_t n_qubits, const std::uint64_t n_batches, const std::uint64_t n_layers, scaluq::StateVectorBatched<Prec, Space> &states)
{
    return;
}

int main()
{
    scaluq::initialize();
    {
        auto start_init = std::chrono::steady_clock::now();

        constexpr scaluq::Precision Prec = scaluq::Precision::F64;
        constexpr scaluq::ExecutionSpace Space = scaluq::ExecutionSpace::Default;
        constexpr std::uint64_t n_qubits = 5;
        constexpr std::uint64_t n_batches = 5;
        constexpr std::uint64_t n_layers = 5;
        constexpr std::uint64_t seed = 0;

        scaluq::StateVectorBatched<Prec, Space> states(n_batches, n_qubits);
        scaluq::Circuit<Prec, Space> circuit(n_qubits);

        add_gates(circuit, seed);

        auto end_init = std::chrono::steady_clock::now();
        std::chrono::duration<float> diff_init = end_init - start_init;
        std::cout << "initialize time: " << diff_init.count() << " [ms]" << std::endl;

        auto start_upd = std::chrono::steady_clock::now();
        run_bench(n_qubits, n_batches, n_layers, states);
        auto end_upd = std::chrono::steady_clock::now();
        std::chrono::duration<float> diff_upd = end_upd - start_upd;
        std::cout << "update time: " << diff_upd.count() << " [ms]" << std::endl;
        std::cout << "total time: " << diff_init.count() + diff_upd.count() << " [ms]" << std::endl;
    }
    scaluq::finalize();
}