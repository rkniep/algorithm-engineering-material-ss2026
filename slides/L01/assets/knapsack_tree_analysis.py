"""
Knapsack Branch-and-Bound Search Tree Analysis

Analyzes how feasibility pruning, optimality pruning, and item ordering
affect the size of the search tree for small knapsack instances (5 items).
Used to find good teaching examples for Algorithm Engineering lecture.

Usage:
    python knapsack_tree_analysis.py
"""

from itertools import permutations, product
from dataclasses import dataclass


@dataclass
class Item:
    name: str
    weight: int
    value: int

    def __repr__(self):
        return f"{self.name}(w={self.weight},v={self.value})"


def solve_knapsack_tree(items: list[Item], capacity: int, known_best: int | None = None,
                         prune_feasibility: bool = True, prune_optimality: bool = True):
    """
    Build branch-and-bound search tree. Returns tree stats.

    At each level i, we decide: include item[i] or not.
    Left branch = include, Right branch = exclude.
    """
    n = len(items)
    nodes_visited = 0
    nodes_pruned_feasibility = 0
    nodes_pruned_optimality = 0
    best_value = known_best if known_best is not None else 0
    best_solution = []
    tree = []  # list of (depth, current_weight, current_value, action, pruned_reason)

    def remaining_value(level):
        """Upper bound: sum of all remaining items' values."""
        return sum(item.value for item in items[level:])

    def dfs(level, current_weight, current_value, path):
        nonlocal nodes_visited, nodes_pruned_feasibility, nodes_pruned_optimality
        nonlocal best_value, best_solution

        nodes_visited += 1

        # Leaf node
        if level == n:
            if current_value > best_value:
                best_value = current_value
                best_solution = path[:]
            tree.append((level, current_weight, current_value, path[:], None))
            return

        # Try including item[level] (left branch)
        item = items[level]
        new_weight = current_weight + item.weight
        new_value = current_value + item.value

        if prune_feasibility and new_weight > capacity:
            nodes_pruned_feasibility += 1
            tree.append((level, new_weight, new_value, path + [1], "infeasible"))
        else:
            # Check optimality bound before branching
            upper_bound_include = new_value + remaining_value(level + 1)
            if prune_optimality and upper_bound_include <= best_value:
                nodes_pruned_optimality += 1
                tree.append((level, new_weight, new_value, path + [1], "suboptimal"))
            else:
                dfs(level + 1, new_weight, new_value, path + [1])

        # Try excluding item[level] (right branch)
        upper_bound_exclude = current_value + remaining_value(level + 1)
        if prune_optimality and upper_bound_exclude <= best_value:
            nodes_pruned_optimality += 1
            tree.append((level, current_weight, current_value, path + [0], "suboptimal"))
        else:
            dfs(level + 1, current_weight, current_value, path + [0])

    dfs(0, 0, 0, [])

    return {
        "nodes_visited": nodes_visited,
        "pruned_feasibility": nodes_pruned_feasibility,
        "pruned_optimality": nodes_pruned_optimality,
        "total_nodes": nodes_visited + nodes_pruned_feasibility + nodes_pruned_optimality,
        "best_value": best_value,
        "best_solution": best_solution,
        "tree": tree,
    }


def print_tree(items, result, label=""):
    """Print a compact tree visualization."""
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Items: {items}")
    print(f"  Nodes visited: {result['nodes_visited']}")
    print(f"  Pruned (feasibility): {result['pruned_feasibility']}")
    print(f"  Pruned (optimality): {result['pruned_optimality']}")
    print(f"  Total nodes: {result['total_nodes']}")
    print(f"  Best value: {result['best_value']}")
    sel = [items[i] for i, x in enumerate(result['best_solution']) if x == 1]
    print(f"  Best solution: {sel}")
    print(f"{'='*60}")


def analyze_instance(items: list[Item], capacity: int):
    """Run all pruning strategies on an instance and compare."""
    print(f"\n{'#'*70}")
    print(f"  INSTANCE: capacity={capacity}")
    print(f"  Items: {items}")
    total_weight = sum(i.weight for i in items)
    total_value = sum(i.value for i in items)
    print(f"  Total weight: {total_weight}, Total value: {total_value}")
    print(f"{'#'*70}")

    # No pruning at all
    r_none = solve_knapsack_tree(items, capacity, prune_feasibility=False, prune_optimality=False)
    print_tree(items, r_none, "NO PRUNING (full tree)")

    # Feasibility only
    r_feas = solve_knapsack_tree(items, capacity, prune_feasibility=True, prune_optimality=False)
    print_tree(items, r_feas, "FEASIBILITY PRUNING ONLY")

    # Feasibility + optimality (no known solution)
    r_both = solve_knapsack_tree(items, capacity, prune_feasibility=True, prune_optimality=True)
    print_tree(items, r_both, "FEASIBILITY + OPTIMALITY PRUNING")

    # Feasibility + optimality with known best
    r_known = solve_knapsack_tree(items, capacity, known_best=r_both["best_value"],
                                   prune_feasibility=True, prune_optimality=True)
    print_tree(items, r_known, f"FEAS + OPT + KNOWN BEST={r_both['best_value']}")

    return r_none, r_feas, r_both, r_known


def find_best_ordering(items: list[Item], capacity: int):
    """Try all permutations and find the one that minimizes tree size."""
    n = len(items)
    results = []

    for perm in permutations(range(n)):
        ordered = [items[i] for i in perm]
        r = solve_knapsack_tree(ordered, capacity, prune_feasibility=True, prune_optimality=True)
        results.append((perm, ordered, r))

    results.sort(key=lambda x: x[2]["nodes_visited"])

    print(f"\n{'*'*70}")
    print(f"  ORDERING ANALYSIS (feasibility + optimality pruning)")
    print(f"{'*'*70}")

    print(f"\n  Best 5 orderings:")
    for perm, ordered, r in results[:5]:
        names = str([items[i].name for i in perm])
        print(f"    {names:30s} → "
              f"visited={r['nodes_visited']:3d}, "
              f"pruned_f={r['pruned_feasibility']:2d}, "
              f"pruned_o={r['pruned_optimality']:2d}")

    print(f"\n  Worst 5 orderings:")
    for perm, ordered, r in results[-5:]:
        names = str([items[i].name for i in perm])
        print(f"    {names:30s} → "
              f"visited={r['nodes_visited']:3d}, "
              f"pruned_f={r['pruned_feasibility']:2d}, "
              f"pruned_o={r['pruned_optimality']:2d}")

    best_perm, best_ordered, best_r = results[0]
    worst_perm, worst_ordered, worst_r = results[-1]

    print(f"\n  Best ordering visits {best_r['nodes_visited']} nodes")
    print(f"  Worst ordering visits {worst_r['nodes_visited']} nodes")
    print(f"  Ratio: {worst_r['nodes_visited'] / best_r['nodes_visited']:.1f}x")

    return results


def search_good_instances():
    """Search for instances that demonstrate pruning well."""
    print("\n" + "=" * 70)
    print("  SEARCHING FOR GOOD TEACHING INSTANCES")
    print("=" * 70)

    best_instances = []

    # Try various random-ish instances with 5 items
    # We want: significant feasibility pruning AND optimality pruning
    for weights in product(range(2, 10), repeat=5):
        # Skip boring cases
        if len(set(weights)) < 3:
            continue
        # Only try a subset
        if sum(weights) < 15 or sum(weights) > 35:
            continue

        values = []
        for w in weights:
            # Correlated values (more realistic)
            values.append(w + 1)

        items = [Item(chr(65 + i), weights[i], values[i]) for i in range(5)]
        capacity = sum(weights) * 2 // 5  # ~40% of total weight

        r_none = solve_knapsack_tree(items, capacity, prune_feasibility=False, prune_optimality=False)
        r_feas = solve_knapsack_tree(items, capacity, prune_feasibility=True, prune_optimality=False)
        r_both = solve_knapsack_tree(items, capacity, prune_feasibility=True, prune_optimality=True)

        feas_reduction = r_none["nodes_visited"] - r_feas["nodes_visited"]
        opt_reduction = r_feas["nodes_visited"] - r_both["nodes_visited"]

        if feas_reduction >= 8 and opt_reduction >= 5:
            # Also check ordering effect
            perms = []
            for perm in permutations(range(5)):
                ordered = [items[i] for i in perm]
                r = solve_knapsack_tree(ordered, capacity, prune_feasibility=True, prune_optimality=True)
                perms.append(r["nodes_visited"])

            ordering_ratio = max(perms) / min(perms)

            best_instances.append({
                "items": items,
                "capacity": capacity,
                "full": r_none["nodes_visited"],
                "feas": r_feas["nodes_visited"],
                "both": r_both["nodes_visited"],
                "feas_reduction": feas_reduction,
                "opt_reduction": opt_reduction,
                "ordering_ratio": ordering_ratio,
                "best_ordering_nodes": min(perms),
                "worst_ordering_nodes": max(perms),
            })

    # Sort by combined quality
    best_instances.sort(key=lambda x: (-x["feas_reduction"] - x["opt_reduction"],
                                        -x["ordering_ratio"]))

    print(f"\nFound {len(best_instances)} good instances. Top 10:\n")
    print(f"  {'Items':50s} Cap  Full Feas Both  -F  -O  OrdRatio  BestOrd WorstOrd")
    print(f"  {'-'*100}")
    for inst in best_instances[:10]:
        items_str = str(inst["items"])
        print(f"  {items_str:50s} {inst['capacity']:3d}  "
              f"{inst['full']:3d}  {inst['feas']:3d}  {inst['both']:3d}  "
              f"{inst['feas_reduction']:3d} {inst['opt_reduction']:3d}  "
              f"{inst['ordering_ratio']:5.1f}x    "
              f"{inst['best_ordering_nodes']:3d}     {inst['worst_ordering_nodes']:3d}")

    return best_instances


def main():
    # First, search for good instances
    good_instances = search_good_instances()

    if not good_instances:
        print("No good instances found!")
        return

    # Analyze the best one in detail
    best = good_instances[0]
    print(f"\n\n{'#'*70}")
    print(f"  DETAILED ANALYSIS OF BEST INSTANCE")
    print(f"{'#'*70}")

    analyze_instance(best["items"], best["capacity"])
    find_best_ordering(best["items"], best["capacity"])

    # Hand-crafted instances with varied value/weight ratios
    hand_crafted = [
        (
            "Classic mixed ratios",
            [Item("A", 8, 12), Item("B", 6, 9), Item("C", 5, 7),
             Item("D", 4, 5), Item("E", 3, 4)],
            12,
        ),
        (
            "One heavy high-value + small items",
            [Item("A", 10, 15), Item("B", 3, 5), Item("C", 3, 4),
             Item("D", 2, 3), Item("E", 2, 3)],
            10,
        ),
        (
            "Varied ratios - trap item",
            [Item("A", 7, 8), Item("B", 5, 10), Item("C", 4, 6),
             Item("D", 3, 5), Item("E", 2, 3)],
            10,
        ),
        (
            "Tight capacity, diverse items",
            [Item("A", 6, 11), Item("B", 5, 9), Item("C", 4, 7),
             Item("D", 3, 4), Item("E", 2, 3)],
            10,
        ),
    ]

    for label, items, cap in hand_crafted:
        print(f"\n\n{'#'*70}")
        print(f"  HAND-CRAFTED: {label}")
        print(f"{'#'*70}")
        analyze_instance(items, cap)
        find_best_ordering(items, cap)


if __name__ == "__main__":
    main()
