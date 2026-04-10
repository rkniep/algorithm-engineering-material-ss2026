#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <limits>
#include <numeric>
#include <random>
#include <stdexcept>
#include <thread>
#include <utility>
#include <vector>

namespace py = pybind11;

using Point = std::pair<double, double>;
using Clock = std::chrono::steady_clock;

static inline double dist(const std::vector<Point> &points, int a, int b) {
  double dx = points[a].first - points[b].first;
  double dy = points[a].second - points[b].second;
  return std::sqrt(dx * dx + dy * dy);
}

static double tour_length(const std::vector<Point> &points,
                          const std::vector<int> &tour) {
  int n = static_cast<int>(tour.size());
  double total = 0.0;
  for (int k = 0; k < n; ++k) {
    total += dist(points, tour[k], tour[(k + 1) % n]);
  }
  return total;
}

static std::vector<int> make_random_tour(int n, int seed) {
  std::vector<int> tour(n);
  std::iota(tour.begin(), tour.end(), 0);
  std::mt19937 rng(seed);
  std::shuffle(tour.begin(), tour.end(), rng);
  return tour;
}

// ---------------------------------------------------------------------------
// Variant 1: First-improvement (classical 2-opt)
//   Find the first improving move, apply it, restart the scan.
// ---------------------------------------------------------------------------
static std::vector<int> two_opt_first_improvement(
    const std::vector<Point> &points, std::vector<int> tour,
    double timeout_seconds) {
  // TODO: Implement first-improvement 2-opt with timeout.
  // Check Clock::now() >= deadline after each restart to respect the timeout.
  throw std::runtime_error("cpp_first_improvement not implemented");
}

// ---------------------------------------------------------------------------
// Variant 2: Full-scan (apply improvements immediately, continue scanning)
//   Sweep all pairs; apply each improving move on the spot without restarting.
//   Repeat until a full sweep finds no improvement.
// ---------------------------------------------------------------------------
static std::vector<int> two_opt_full_scan(
    const std::vector<Point> &points, std::vector<int> tour,
    double timeout_seconds) {
  // TODO: Implement full-scan 2-opt with timeout.
  throw std::runtime_error("cpp_full_scan not implemented");
}

// ---------------------------------------------------------------------------
// Variant 3: Best-improvement
//   Scan all pairs, find the single most improving move, apply it, restart.
// ---------------------------------------------------------------------------
static std::vector<int> two_opt_best_improvement(
    const std::vector<Point> &points, std::vector<int> tour,
    double timeout_seconds) {
  // TODO: Implement best-improvement 2-opt with timeout.
  throw std::runtime_error("cpp_best_improvement not implemented");
}

// ---------------------------------------------------------------------------
// Parallel: run full-scan 2-opt on multiple threads with different seeds
// ---------------------------------------------------------------------------
std::vector<int> parallel_two_opt(const std::vector<Point> &points,
                                  int num_threads = 4,
                                  int base_seed = 0,
                                  double timeout_seconds = 10.0) {
  if (num_threads < 1) {
    throw std::invalid_argument("num_threads must be at least 1");
  }

  // TODO: Launch num_threads threads, each running full-scan 2-opt with
  // a different seed (base_seed + t). Use make_random_tour() to create
  // the initial tour for each thread. After all threads finish, return
  // the tour with the shortest length.
  throw std::runtime_error("parallel_two_opt not implemented");
}

// ---------------------------------------------------------------------------
// Python bindings (do not modify)
// ---------------------------------------------------------------------------
PYBIND11_MODULE(_core, m) {
  m.def("cpp_first_improvement", &two_opt_first_improvement,
        py::arg("points"), py::arg("initial_tour"),
        py::arg("timeout") = 10.0,
        "2-opt with first-improvement and restart (classical).");

  m.def("cpp_full_scan", &two_opt_full_scan,
        py::arg("points"), py::arg("initial_tour"),
        py::arg("timeout") = 10.0,
        "2-opt applying improvements during a full sweep (fastest variant).");

  m.def("cpp_best_improvement", &two_opt_best_improvement,
        py::arg("points"), py::arg("initial_tour"),
        py::arg("timeout") = 10.0,
        "2-opt with best-improvement: applies only the best move per scan.");

  m.def("parallel_two_opt", &parallel_two_opt, py::arg("points"),
        py::arg("num_threads") = 4, py::arg("base_seed") = 0,
        py::arg("timeout") = 10.0,
        "Parallel 2-opt: one thread per seed, returns best tour.");
}
