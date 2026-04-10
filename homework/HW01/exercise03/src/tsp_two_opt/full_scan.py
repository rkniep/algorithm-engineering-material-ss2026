import math


def _dist(points, a, b):
    dx = points[a][0] - points[b][0]
    dy = points[a][1] - points[b][1]
    return math.sqrt(dx * dx + dy * dy)


def full_scan_two_opt(
    points: list[tuple[float, float]], initial_tour: list[int]
) -> list[int]:
    """
    Full-scan 2-opt: apply improvements immediately, continue scanning.

    Args:
        points: List of (x, y) coordinate tuples.
        initial_tour: Starting tour as a permutation of point indices.

    Returns:
        Tour as a list of point indices.
    """
    # TODO: Implement Variant 2 (full-scan, continue after improvement).
    raise NotImplementedError
