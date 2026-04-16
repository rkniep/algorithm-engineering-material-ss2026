import math


def _dist(points, a, b):
    dx = points[a][0] - points[b][0]
    dy = points[a][1] - points[b][1]
    return math.sqrt(dx * dx + dy * dy)


def best_improvement_two_opt(
    points: list[tuple[float, float]],
    initial_tour: list[int],
    timeout: float = 10.0,
) -> list[int]:
    """
    Best-improvement 2-opt: scan all pairs, apply only the best move per pass.

    Args:
        points: List of (x, y) coordinate tuples.
        initial_tour: Starting tour as a permutation of point indices.
        timeout: Maximum runtime in seconds. If exceeded, return the best tour
            found so far. Check ``time.perf_counter()`` against a precomputed
            deadline after each full sweep (coarse-grained is fine).

    Returns:
        Tour as a list of point indices.
    """
    # TODO: Implement Variant 3 (best-improvement).
    # Respect ``timeout``: compute ``deadline = time.perf_counter() + timeout``
    # and break out of the outer loop once the deadline is reached.
    raise NotImplementedError
