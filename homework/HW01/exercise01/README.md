# Exercise 01: Setup

This exercise verifies that you can build and run a C++ program.
The program produces a unique output string; no code changes are needed.

## Build

Prerequisites: C++ compiler with C++20 support, CMake 3.20+.

```bash
mkdir cmake-build-release
cmake -S . -B cmake-build-release -DCMAKE_BUILD_TYPE=Release
cmake --build cmake-build-release
./cmake-build-release/output_id
```

## Docker (alternative)

A Dockerfile is provided if you don't have a local C++ toolchain.

```bash
docker build -t ae26-ex1 .
docker run --rm -it ae26-ex1
```
