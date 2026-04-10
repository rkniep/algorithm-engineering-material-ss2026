"""
Tests for 2-opt TSP implementations.

Checks that each implementation:
  1. Returns a valid tour (permutation of 0..n-1)
  2. Does not make the tour worse than the initial tour
  3. Produces a 2-optimal tour (no improving 2-opt move exists)
"""

import math
import random
import pytest


# ── Helpers ──────────────────────────────────────────────────────────

def _dist(points, a, b):
    dx = points[a][0] - points[b][0]
    dy = points[a][1] - points[b][1]
    return math.sqrt(dx * dx + dy * dy)


def tour_length(points, tour):
    n = len(tour)
    return sum(_dist(points, tour[i], tour[(i + 1) % n]) for i in range(n))


def is_valid_tour(points, tour):
    return sorted(tour) == list(range(len(points)))


def is_two_optimal(points, tour, eps=1e-10):
    """Return True if no improving 2-opt move exists."""
    n = len(tour)
    for i in range(n - 1):
        a, b = tour[i], tour[(i + 1) % n]
        upper = n - 1 if i == 0 else n
        for j in range(i + 2, upper):
            c, d = tour[j], tour[(j + 1) % n]
            delta = _dist(points, a, c) + _dist(points, b, d) \
                  - _dist(points, a, b) - _dist(points, c, d)
            if delta < -eps:
                return False
    return True


# ── Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture
def small_instance():
    """10 points — fast, exercises all code paths."""
    rng = random.Random(42)
    return [(rng.uniform(0, 1000), rng.uniform(0, 1000)) for _ in range(10)]


@pytest.fixture
def medium_instance():
    """100 points — still fast, more realistic."""
    rng = random.Random(123)
    return [(rng.uniform(0, 10000), rng.uniform(0, 10000)) for _ in range(100)]


def make_tour(n, seed=0):
    rng = random.Random(seed)
    tour = list(range(n))
    rng.shuffle(tour)
    return tour


# ── Python: first-improvement ────────────────────────────────────────

class TestFirstImprovement:
    def _run(self, points, seed=0):
        from tsp_two_opt import first_improvement_two_opt
        return first_improvement_two_opt(points, make_tour(len(points), seed))

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import first_improvement_two_opt
        result = first_improvement_two_opt(small_instance, initial)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_multiple_seeds(self, medium_instance):
        for seed in range(5):
            tour = self._run(medium_instance, seed)
            assert is_valid_tour(medium_instance, tour)
            assert is_two_optimal(medium_instance, tour)


# ── Python: full-scan ────────────────────────────────────────────────

class TestFullScan:
    def _run(self, points, seed=0):
        from tsp_two_opt import full_scan_two_opt
        return full_scan_two_opt(points, make_tour(len(points), seed))

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import full_scan_two_opt
        result = full_scan_two_opt(small_instance, initial)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_multiple_seeds(self, medium_instance):
        for seed in range(5):
            tour = self._run(medium_instance, seed)
            assert is_valid_tour(medium_instance, tour)
            assert is_two_optimal(medium_instance, tour)


# ── Python: best-improvement ─────────────────────────────────────────

class TestBestImprovement:
    def _run(self, points, seed=0):
        from tsp_two_opt import best_improvement_two_opt
        return best_improvement_two_opt(points, make_tour(len(points), seed))

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import best_improvement_two_opt
        result = best_improvement_two_opt(small_instance, initial)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_multiple_seeds(self, medium_instance):
        for seed in range(5):
            tour = self._run(medium_instance, seed)
            assert is_valid_tour(medium_instance, tour)
            assert is_two_optimal(medium_instance, tour)


# ── C++: first-improvement ───────────────────────────────────────────

class TestCppFirstImprovement:
    def _run(self, points, seed=0):
        from tsp_two_opt import cpp_first_improvement
        return cpp_first_improvement(points, make_tour(len(points), seed), timeout=60.0)

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import cpp_first_improvement
        result = cpp_first_improvement(small_instance, initial, timeout=60.0)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_matches_python(self, medium_instance):
        """C++ should produce the same result as Python given the same initial tour."""
        from tsp_two_opt import first_improvement_two_opt, cpp_first_improvement
        initial = make_tour(len(medium_instance))
        try:
            py_tour = first_improvement_two_opt(medium_instance, initial)
        except NotImplementedError:
            pytest.skip("Python first_improvement not yet implemented")
        cpp_tour = cpp_first_improvement(medium_instance, initial, timeout=60.0)
        assert tour_length(medium_instance, cpp_tour) == pytest.approx(
            tour_length(medium_instance, py_tour), abs=1e-6)


# ── C++: full-scan ───────────────────────────────────────────────────

class TestCppFullScan:
    def _run(self, points, seed=0):
        from tsp_two_opt import cpp_full_scan
        return cpp_full_scan(points, make_tour(len(points), seed), timeout=60.0)

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import cpp_full_scan
        result = cpp_full_scan(small_instance, initial, timeout=60.0)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_matches_python(self, medium_instance):
        """C++ should produce the same result as Python given the same initial tour."""
        from tsp_two_opt import full_scan_two_opt, cpp_full_scan
        initial = make_tour(len(medium_instance))
        try:
            py_tour = full_scan_two_opt(medium_instance, initial)
        except NotImplementedError:
            pytest.skip("Python full_scan not yet implemented")
        cpp_tour = cpp_full_scan(medium_instance, initial, timeout=60.0)
        assert tour_length(medium_instance, cpp_tour) == pytest.approx(
            tour_length(medium_instance, py_tour), abs=1e-6)


# ── C++: best-improvement ────────────────────────────────────────────

class TestCppBestImprovement:
    def _run(self, points, seed=0):
        from tsp_two_opt import cpp_best_improvement
        return cpp_best_improvement(points, make_tour(len(points), seed), timeout=60.0)

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_no_worse(self, small_instance):
        initial = make_tour(len(small_instance))
        from tsp_two_opt import cpp_best_improvement
        result = cpp_best_improvement(small_instance, initial, timeout=60.0)
        assert tour_length(small_instance, result) <= tour_length(small_instance, initial) + 1e-10

    def test_two_optimal_small(self, small_instance):
        tour = self._run(small_instance)
        assert is_two_optimal(small_instance, tour)

    def test_two_optimal_medium(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_matches_python(self, medium_instance):
        """C++ should produce the same result as Python given the same initial tour."""
        from tsp_two_opt import best_improvement_two_opt, cpp_best_improvement
        initial = make_tour(len(medium_instance))
        try:
            py_tour = best_improvement_two_opt(medium_instance, initial)
        except NotImplementedError:
            pytest.skip("Python best_improvement not yet implemented")
        cpp_tour = cpp_best_improvement(medium_instance, initial, timeout=60.0)
        assert tour_length(medium_instance, cpp_tour) == pytest.approx(
            tour_length(medium_instance, py_tour), abs=1e-6)


# ── C++: parallel ────────────────────────────────────────────────────

class TestParallel:
    def _run(self, points, num_threads=4, base_seed=0):
        from tsp_two_opt import parallel_two_opt
        return parallel_two_opt(points, num_threads=num_threads,
                                base_seed=base_seed, timeout=60.0)

    def test_valid_tour(self, small_instance):
        tour = self._run(small_instance)
        assert is_valid_tour(small_instance, tour)

    def test_two_optimal(self, medium_instance):
        tour = self._run(medium_instance)
        assert is_two_optimal(medium_instance, tour)

    def test_thread_counts(self, medium_instance):
        for t in [1, 2, 4, 8]:
            tour = self._run(medium_instance, num_threads=t)
            assert is_valid_tour(medium_instance, tour)
            assert is_two_optimal(medium_instance, tour)

    def test_more_threads_no_worse(self, medium_instance):
        """More threads should produce equal or better average quality."""
        from tsp_two_opt import parallel_two_opt
        len_1t = tour_length(medium_instance,
                             parallel_two_opt(medium_instance, num_threads=1,
                                              base_seed=0, timeout=60.0))
        len_8t = tour_length(medium_instance,
                             parallel_two_opt(medium_instance, num_threads=8,
                                              base_seed=0, timeout=60.0))
        # 8 threads pick the best of 8 seeds; 1 thread only has 1 seed.
        # With base_seed=0, the 1-thread result is one of the 8 candidates,
        # so 8 threads should be at least as good.
        assert len_8t <= len_1t + 1e-10

    def test_rejects_zero_threads(self):
        from tsp_two_opt import parallel_two_opt
        with pytest.raises((ValueError, RuntimeError)):
            parallel_two_opt([(0, 0), (1, 1), (2, 2), (3, 3)],
                             num_threads=0, base_seed=0)
