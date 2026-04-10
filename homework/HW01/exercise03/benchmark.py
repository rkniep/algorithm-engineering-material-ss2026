"""
Benchmark script for 2-opt TSP implementations.

For each instance size, runs all available implementations (Python, C++, parallel)
on the same generated points with the same initial tours. A timeout prevents
slow variants from blocking.
"""

import math
import random
import statistics
import time

NUM_SEEDS = 5  # number of random seeds per comparison
COORD_RANGE = 10000.0
TIMEOUT = 10.0  # seconds per run
PARALLEL_THREADS = [1, 2, 4, 8]


def generate_instance(n: int, instance_seed: int = 0) -> list[tuple[float, float]]:
    """Generate n random points in [0, COORD_RANGE]^2 with a fixed seed."""
    rng = random.Random(instance_seed)
    return [(rng.uniform(0, COORD_RANGE), rng.uniform(0, COORD_RANGE)) for _ in range(n)]


def generate_tour(n: int, seed: int) -> list[int]:
    """Generate a random permutation of 0..n-1."""
    rng = random.Random(seed)
    tour = list(range(n))
    rng.shuffle(tour)
    return tour


def tour_length(points: list[tuple[float, float]], tour: list[int]) -> float:
    """Compute the total Euclidean length of a tour."""
    n = len(tour)
    total = 0.0
    for k in range(n):
        ax, ay = points[tour[k]]
        bx, by = points[tour[(k + 1) % n]]
        total += math.sqrt((ax - bx) ** 2 + (ay - by) ** 2)
    return total


def validate_tour(points: list[tuple[float, float]], tour: list[int]) -> bool:
    """Check that the tour is a valid permutation."""
    return sorted(tour) == list(range(len(points)))


def run_multi_seed(func, points, initial_tours, label="", **kwargs):
    """Run a function with multiple initial tours. Returns list of (length, time) tuples."""
    results = []
    for idx, tour in enumerate(initial_tours):
        try:
            print(f"    {label} seed {idx} ({idx+1}/{len(initial_tours)}) ...", end=" ", flush=True)
            t0 = time.perf_counter()
            result = func(points, initial_tour=tour, **kwargs)
            elapsed = time.perf_counter() - t0
            if not validate_tour(points, result):
                print(f"INVALID ({elapsed:.2f}s)")
                results.append((None, elapsed))
            else:
                length = tour_length(points, result)
                print(f"len={length:.1f}  ({elapsed:.2f}s)")
                results.append((length, elapsed))
        except NotImplementedError:
            print("not implemented")
            return None
        except RuntimeError:
            print("error")
            return None
    return results


def run_parallel(func, points, num_threads, label="", **kwargs):
    """Run parallel variant with varying base seeds. Returns list of (length, time) tuples."""
    results = []
    for trial in range(NUM_SEEDS):
        base_seed = trial * num_threads
        print(f"    {label} trial {trial+1}/{NUM_SEEDS} ...", end=" ", flush=True)
        t0 = time.perf_counter()
        tour = func(points, num_threads=num_threads, base_seed=base_seed, **kwargs)
        elapsed = time.perf_counter() - t0
        if validate_tour(points, tour):
            length = tour_length(points, tour)
            print(f"len={length:.1f}  ({elapsed:.2f}s)")
            results.append((length, elapsed))
        else:
            print("INVALID")
            results.append((None, elapsed))
    return results


def fmt_results(results):
    """Format (length, time) results as avg ± std."""
    lengths = [l for l, _ in results if l is not None]
    times = [t for _, t in results]
    if not lengths:
        return "INVALID"
    avg_len = statistics.mean(lengths)
    avg_time = statistics.mean(times)
    if len(lengths) > 1:
        std_len = statistics.stdev(lengths)
        return f"len={avg_len:12.1f} (±{std_len:8.1f})  avg_time={avg_time:.4f}s"
    return f"len={avg_len:12.1f}  time={avg_time:.4f}s"


def print_table(rows):
    """Print a comparison table. rows = [(label, results), ...]"""
    for label, results in rows:
        if results is None:
            print(f"  {label:20s}  NOT IMPLEMENTED")
        else:
            print(f"  {label:20s}  {fmt_results(results)}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Benchmark 2-opt TSP implementations.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
examples:
  python benchmark.py          # run all sizes
  python benchmark.py 100 500  # run only n=100 and n=500
""",
    )
    parser.add_argument(
        "sizes",
        nargs="*",
        type=int,
        help="instance sizes to run (default: 100 500 1000 5000 20000)",
    )
    args = parser.parse_args()
    sizes = args.sizes if args.sizes else [100, 500, 1000, 5000, 20000]

    # Try importing implementations
    from tsp_two_opt import (first_improvement_two_opt, full_scan_two_opt,
                              best_improvement_two_opt)

    have_cpp = True
    try:
        from tsp_two_opt import (cpp_first_improvement, cpp_full_scan,
                                  cpp_best_improvement, parallel_two_opt)
    except ImportError:
        have_cpp = False
        print("Note: C++ module not built — skipping C++ and parallel variants.\n")

    print("=" * 70)
    print(f"2-Opt TSP Benchmark  (timeout={TIMEOUT}s, seeds={NUM_SEEDS})")
    print("=" * 70)

    for n in sizes:
        points = generate_instance(n)
        initial_tours = [generate_tour(n, seed) for seed in range(NUM_SEEDS)]

        print(f"\n{'─' * 70}")
        print(f"  n = {n}")
        print(f"{'─' * 70}")

        rows = []

        # Python variants
        print(f"\n  Python:")
        res = run_multi_seed(first_improvement_two_opt, points, initial_tours,
                             label="first-impr")
        rows.append(("first-impr (py)", res))
        res = run_multi_seed(best_improvement_two_opt, points, initial_tours,
                             label="best-impr")
        rows.append(("best-impr (py)", res))
        res = run_multi_seed(full_scan_two_opt, points, initial_tours,
                             label="full-scan")
        rows.append(("full-scan (py)", res))

        if have_cpp:
            # C++ variants
            print(f"\n  C++:")
            res = run_multi_seed(cpp_first_improvement, points, initial_tours,
                                 label="first-impr", timeout=TIMEOUT)
            rows.append(("first-impr (C++)", res))
            res = run_multi_seed(cpp_best_improvement, points, initial_tours,
                                 label="best-impr", timeout=TIMEOUT)
            rows.append(("best-impr (C++)", res))
            res = run_multi_seed(cpp_full_scan, points, initial_tours,
                                 label="full-scan", timeout=TIMEOUT)
            rows.append(("full-scan (C++)", res))

            # Parallel variants
            print(f"\n  Parallel C++:")
            for num_threads in PARALLEL_THREADS:
                res = run_parallel(parallel_two_opt, points, num_threads,
                                   label=f"parallel({num_threads}T)", timeout=TIMEOUT)
                rows.append((f"parallel ({num_threads}T)", res))

        # Summary table
        print(f"\n  Summary (n={n}):")
        print_table(rows)

    print("\n" + "=" * 70)
    print("Done.")


if __name__ == "__main__":
    main()
