import math


def _dist(points, a, b):
    dx = points[a][0] - points[b][0]
    dy = points[a][1] - points[b][1]
    return math.sqrt(dx * dx + dy * dy)


def first_improvement_two_opt(
    points: list[tuple[float, float]], initial_tour: list[int]
) -> list[int]:
    """
    First-improvement 2-opt (classical): find first improving move, apply, restart.

    Args:
        points: List of (x, y) coordinate tuples.
        initial_tour: Starting tour as a permutation of point indices.

    Returns:
        Tour as a list of point indices.
    """
    # TODO: Implement Variant 1 (first-improvement with restart).
    raise NotImplementedError
