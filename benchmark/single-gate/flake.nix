{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            cudaSupport = true;
          };
        };

        cuquantum = pkgs.stdenv.mkDerivation {
          pname = "cuquantum";
          version = "23.03.0.20";
          src = pkgs.fetchurl {
            url = "https://developer.download.nvidia.com/compute/cuquantum/redist/cuquantum/linux-x86_64/cuquantum-linux-x86_64-23.03.0.20-archive.tar.xz";
            sha256 = "1447b49h4myab9s8q7kgi3h7xvimb8jf72amjfnyrgfgmm3ixcq8";
          };
          installPhase = ''
            mkdir -p $out
            cp -r include/ $out/include/
            cp -r lib/ $out/lib/
          '';
          meta = with pkgs.lib; {
            description = "cuQuantum";
            license = licenses.unfree;
            platforms = platforms.linux;
          };
        };
        cutensor = pkgs.stdenv.mkDerivation {
          pname = "cutensor";
          version = "1.7.0.1";
          src = pkgs.fetchurl {
            url = "https://developer.download.nvidia.com/compute/cutensor/redist/libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz";
            sha256 = "09pbkp5pl3ibi7j30sms9aayw2rv73jyymf9wxrrx8bi2f4mfdfx";

          };
          installPhase = ''
            mkdir -p $out
            cp -r include/ $out/include/
            cp -r lib/ $out/lib/
          '';
          meta = with pkgs.lib; {
            description = "cuTENSOR";
            license = licenses.unfree;
            platforms = platforms.linux;
          };
        };
        qiskit-simple = pkgs.python312Packages.buildPythonPackage rec {
          pname = "qiskit";
          version = "2.1.1";
          src = pkgs.fetchFromGitHub {
            owner = "Qiskit";
            repo = "qiskit";
            rev = "refs/tags/${version}";
            sha256 = "sha256-WHfsl/T4lmnvkGY7gF5PStilGq3G66TZG9oB1tKwuOQ=";
          };
          nativeBuildInputs = with pkgs; [
            python312Full
            python312Packages.setuptools-rust
            rustc
            cargo
            rustPlatform.cargoSetupHook
          ];
          propagatedBuildInputs = with pkgs.python312Packages; [
            rustworkx
            numpy
            scipy
            dill
            stevedore
            typing-extensions
          ];
          cargoDeps = pkgs.rustPlatform.fetchCargoVendor {
            inherit pname version src;
            hash = "sha256-MqHm2J+8xXFzm8/ob76hfNeQgTu0CiWrGCo+oXLPEuc=";
          };
        };
        qiskit-aer-custatevec = pkgs.python312Packages.buildPythonPackage rec {
          pname = "qiskit-aer-custatevec";
          version = "0.17.1";
          src = pkgs.fetchFromGitHub {
            owner = "Qiskit";
            repo = "qiskit-aer";
            rev = "refs/tags/${version}";
            sha256 = "sha256-jvapuARJUHgAKFUzGb5MUft01LNefVIXtStJqFnCo90=";
          };
          format = "setuptools";
          nativeBuildInputs = with pkgs; [
            gcc13
            python312Full
            cmake
            ninja
            boost
            zlib
            openblas
            nlohmann_json
            spdlog
            fmt
          ] ++ (with pkgs.cudaPackages; [
            cuda_cudart
            cudatoolkit
            libcublas
            libcufft
            libcurand
            libcusolver
            libcusparse
            libnpp
          ]) ++ (with pkgs.python312Packages; [
            cmake
            scikit-build
            pybind11
          ]) ++ [
            cuquantum
            cutensor
          ];
          buildInputs = with pkgs; [
            gcc13
            python312Full
            python312Packages.pip
            boost
            zlib
            openblas
            spdlog
          ] ++ (with pkgs.cudaPackages; [
            cuda_cudart
            cudatoolkit
            libcublas
            libcufft
            libcurand
            libcusolver
            libcusparse
            libnpp
          ]) ++ [
            cuquantum
            cutensor
          ];
          propagatedBuildInputs = with pkgs.python312Packages; [
            numpy
            scipy
            psutil
            python-dateutil
          ];
          dontUseCmakeConfigure = true;
          buildPhase = ''
            export HOME=$(pwd)
            export CPLUS_INCLUDE_PATH="${pkgs.spdlog.dev}/include:${pkgs.fmt.dev}/include"
            export LIBRARY_PATH="${pkgs.cudaPackages.cuda_cudart.static}/lib:${pkgs.cudaPackages.libcublas.static}/lib:${pkgs.cudaPackages.libcufft.static}/lib:${pkgs.cudaPackages.libcurand.static}/lib:${pkgs.cudaPackages.libcusolver.static}/lib:${pkgs.cudaPackages.libcusparse.static}/lib:${pkgs.cudaPackages.libnpp.static}/lib"
            ls
            ${pkgs.python312Packages.python.interpreter} setup.py bdist_wheel -- -DAER_THRUST_BACKEND=CUDA -DCUQUANTUM_ROOT=${cuquantum} -DCUTENSOR_ROOT=${cutensor} -DAER_ENABLE_CUQUANTUM=true -DCUQUANTUM_STATIC=true -DDISABLE_CONAN=ON -DCMAKE_PREFIX_PATH="${pkgs.nlohmann_json}/share/cmake/nlohmann_json;${pkgs.spdlog.dev}/lib/cmake/spdlog;${pkgs.fmt.dev}/lib/cmake/fmt" --
          '';
          installPhase = ''
            ${pkgs.python312Packages.python.interpreter} -m pip install dist/*.whl --prefix=$out --no-deps --no-build-isolation
          '';

          meta = with pkgs.lib; {
            description = "Qiskit Aer with CUDA and cuQuantum support";
            homepage = "https://github.com/Qiskit/qiskit-aer";
            license = licenses.asl20;
            maintainers = [ ];
            platforms = platforms.linux;
            broken = !pkgs.stdenv.isLinux;
          };
        };
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            gcc13
            python312Full
            cmake
            boost
            zlib
            cudaPackages.cuda_cudart
            cudaPackages.cudatoolkit
            cudaPackages.libcublas
            cudaPackages.libcufft
            cudaPackages.libcurand
            cudaPackages.libcusolver
            cudaPackages.libcusparse
            cudaPackages.libnpp
            python312Packages.pytest
            python312Packages.pytest-benchmark
            cutensor
            cuquantum
            qiskit-simple
            qiskit-aer-custatevec
            openblas
          ];
          LIBRARY_PATH = "${pkgs.cudaPackages.cuda_cudart.static}/lib:${pkgs.cudaPackages.libcublas.static}/lib:${pkgs.cudaPackages.libcufft.static}/lib:${pkgs.cudaPackages.libcurand.static}/lib:${pkgs.cudaPackages.libcusolver.static}/lib:${pkgs.cudaPackages.libcusparse.static}/lib:${pkgs.cudaPackages.libnpp.static}/lib";
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.cudaPackages.cudatoolkit}/lib:${cuquantum}/lib/12:${cutensor}/lib/12";
        };
      }
    );
}
