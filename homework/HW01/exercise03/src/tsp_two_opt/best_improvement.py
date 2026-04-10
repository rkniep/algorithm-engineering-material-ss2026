import math


def _dist(points, a, b):
    dx = points[a][0] - points[b][0]
    dy = points[a][1] - points[b][1]
    return math.sqrt(dx * dx + dy * dy)


def best_improvement_two_opt(
    points: list[tuple[float, float]], initial_tour: list[int]
) -> list[int]:
    """
    Best-improvement 2-opt: scan all pairs, apply only the best move per pass.

    Args:
        points: List of (x, y) coordinate tuples.
        initial_tour: Starting tour as a permutation of point indices.

    Returns:
        Tour as a list of point indices.
    """
    # TODO: Implement Variant 3 (best-improvement).
    raise NotImplementedError
