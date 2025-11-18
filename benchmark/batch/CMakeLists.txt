cmake_minimum_required(VERSION 3.24)

project(bench LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CUDA_STANDARD 20)
# Set your architecture. For example RTX 3060 (Ampere, CC 8.6)
set(CMAKE_CUDA_ARCHITECTURES 86)

set(SCALUQ_USE_CUDA ON  CACHE BOOL  "Enable CUDA in scaluq")
set(SCALUQ_USE_TEST OFF CACHE BOOL  "Build tests if supported")

if(NOT CMAKE_CUDA_COMPILER)
  set(CMAKE_CUDA_COMPILER "/usr/local/cuda/bin/nvcc" CACHE FILEPATH "" FORCE)
endif()

if(DEFINED ENV{CUQUANTUM_ROOT})
  set(CUQUANTUM_ROOT $ENV{CUQUANTUM_ROOT})
  include_directories(${CUQUANTUM_ROOT}/include)
  link_directories(${CUQUANTUM_ROOT}/lib ${CUQUANTUM_ROOT}/lib64)
  find_library(CUSTATEVEC_LIB
    NAMES custatevec libcustatevec
    PATHS ${CUQUANTUM_ROOT}/lib ${CUQUANTUM_ROOT}/lib64
    NO_DEFAULT_PATH)
endif()

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

    if(CUSTATEVEC_LIB)
        target_link_libraries(${name} PRIVATE ${CUSTATEVEC_LIB})
        target_compile_definitions(${name} PRIVATE SCALUQ_USE_CUQUANTUM=1)
    endif()

    if (SCALUQ_USE_TEST)
        find_package(GTest CONFIG REQUIRED)
        target_link_libraries(${name} PRIVATE GTest::gtest_main)
    endif()

    target_include_directories(${name} PRIVATE
        ${PROJECT_SOURCE_DIR}/include
    )

    target_compile_options(${name} PRIVATE
        $<$<COMPILE_LANGUAGE:CXX>:-O2>
        $<$<COMPILE_LANGUAGE:CUDA>:-O2 --expt-relaxed-constexpr>
    )
endfunction()

exe(Scaluq)