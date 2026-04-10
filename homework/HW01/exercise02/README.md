# Exercise 02: Bad Programs

This exercise contains two C++ programs with suboptimal performance.
Your task is to identify and fix the performance issues.

## Programs

- **problem_program_a**: Suffers from branch mispredictions.
  Takes an integer N as argument.
- **problem_program_b**: Suffers from poor cache performance due to
  data structure choices. Takes a graph JSON file as argument.

## Build

Prerequisites: C++ compiler with C++20 support, CMake 3.20+.

```bash
mkdir cmake-build-release
cmake -S . -B cmake-build-release -DCMAKE_BUILD_TYPE=Release
cmake --build cmake-build-release
```

## Running

```bash
# Exercise 2a
./cmake-build-release/problem_program_a 1024
./cmake-build-release/problem_program_a 8192
./cmake-build-release/problem_program_a 32768

# Exercise 2b
./cmake-build-release/problem_program_b graph1.json
```

Nine test graphs (`graph1.json` through `graph9.json`) are provided.

> **Note:** Exercise 2a mentions `perf stat` to observe branch mispredictions.
> `perf` is useful for confirming your analysis but not strictly required —
> you can identify and fix the issue by reasoning about the code, and measure
> the improvement via the wall-clock times the program prints.
> If you do want to use `perf`, it needs direct access to hardware performance
> counters and only works natively on Linux (not inside Docker).

## Docker (alternative)

A Dockerfile is provided if you don't have a local C++ toolchain.
Note that `perf` will **not** work inside the container.

```bash
docker build -t ae26-ex2 .
docker run --rm -it -v $(pwd):/app ae26-ex2
```

Inside the container, build and run as shown above (using `build/Release`
instead of `cmake-build-release`):

```bash
mkdir -p build/Release
cmake -DCMAKE_BUILD_TYPE=Release -S . -B build/Release
cmake --build build/Release
```
