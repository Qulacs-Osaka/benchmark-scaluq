cmake_minimum_required(VERSION 3.24)

project(bench LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CUDA_STANDARD 20)
# Set your architecture. For example RTX 3060 (Ampere, CC 8.6)
set(CMAKE_CUDA_ARCHITECTURES 80)

set(SCALUQ_USE_CUDA ON  CACHE BOOL  "Enable CUDA in scaluq")
set(SCALUQ_USE_TEST OFF CACHE BOOL  "Build tests if supported")

set(SCALUQ_CMAKE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/scaluq/cmake")
if(EXISTS "${SCALUQ_CMAKE_DIR}/ScaluqUtility.cmake")
  list(PREPEND CMAKE_MODULE_PATH "${SCALUQ_CMAKE_DIR}")
  include(ScaluqUtility)
endif()

add_subdirectory(scaluq)

function(exe name)
    add_executable(${name} ${name}.cpp)

    target_link_libraries(${name} PRIVATE
        scaluq
        Eigen3::Eigen
        Kokkos::kokkos
        nlohmann_json::nlohmann_json
    )

    target_include_directories(${name} PRIVATE
        ${PROJECT_SOURCE_DIR}/scaluq/include
        ${PROJECT_SOURCE_DIR}/include
    )

    target_compile_options(${name} PRIVATE
        $<$<COMPILE_LANGUAGE:CUDA>:-O3 --expt-relaxed-constexpr>
    )
endfunction()

exe(Scaluq)
