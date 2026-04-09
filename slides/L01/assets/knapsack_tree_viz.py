"""
Generate Graphviz decision trees for knapsack branch-and-bound.

Always renders the FULL binary tree. Every node is colored by its properties
(feasible, infeasible, suboptimal, optimal). Pruned subtrees are grayed out.

Key: a pruned node is still *explored* (we visit it to discover the reason).
Only its children are grayed out.

Designed for widescreen slides: left-to-right layout, compact nodes.

Usage:
    python knapsack_tree_viz.py
"""

from dataclasses import dataclass, field
import subprocess
import os


@dataclass
class Item:
    name: str
    weight: int
    value: int


@dataclass
class Node:
    id: str
    decisions: list
    weight: int
    value: int
    bound: int
    depth: int
    kind: str = "normal"     # normal, infeasible, suboptimal, optimal
    pruned: bool = False     # grayed out (not explored by solver)
    children: list = field(default_factory=list)


def build_full_tree(items, capacity, prune_feasibility=True, prune_optimality=True,
                    known_best=None):
    """
    Step 1: Build the complete binary tree with node properties.
    Step 2: Simulate DFS and mark pruned subtrees.
    """
    n = len(items)
    node_counter = [0]

    # Compute true optimal
    true_optimal = 0
    for mask in range(1 << n):
        w = sum(items[i].weight for i in range(n) if mask & (1 << i))
        v = sum(items[i].value for i in range(n) if mask & (1 << i))
        if w <= capacity and v > true_optimal:
            true_optimal = v

    def remaining_value(level):
        return sum(items[i].value for i in range(level, n))

    def make_id():
        node_counter[0] += 1
        return f"n{node_counter[0]}"

    # Step 1: Build full tree, classify every node
    def build(decisions, weight, value, level):
        bound = value + remaining_value(level)
        nid = make_id()

        if weight > capacity:
            kind = "infeasible"
        elif level == n and value == true_optimal:
            kind = "optimal"
        else:
            kind = "normal"

        node = Node(nid, list(decisions), weight, value, bound, level, kind=kind)

        if level < n:
            item = items[level]
            left = build(decisions + [1], weight + item.weight,
                         value + item.value, level + 1)
            node.children.append((f"+{item.name}", left))
            right = build(decisions + [0], weight, value, level + 1)
            node.children.append((f"−{item.name}", right))

        return node

    root = build([], 0, 0, 0)

    # Step 2: Simulate solver DFS, marking pruned subtrees
    best_value = [known_best if known_best is not None else 0]

    def mark_pruned(node):
        """Recursively mark all descendants as pruned."""
        node.pruned = True
        for _, child in node.children:
            mark_pruned(child)

    def simulate(node):
        """DFS simulation. The node itself is always explored.
        We check if its children should be pruned."""
        if not node.children:
            # Leaf: update best if feasible
            if node.kind != "infeasible" and node.value > best_value[0]:
                best_value[0] = node.value
            return

        for edge_label, child in node.children:
            should_prune = False

            if prune_feasibility and child.kind == "infeasible":
                # We visit the infeasible child (it stays explored),
                # but prune its children
                should_prune = True
            elif prune_optimality and child.bound <= best_value[0]:
                # Bound pruning: we visit the child to check the bound,
                # but prune its children. Mark it suboptimal.
                child.kind = "suboptimal"
                should_prune = True

            if should_prune:
                # Child is explored, but its subtree is pruned
                for _, grandchild in child.children:
                    mark_pruned(grandchild)
            else:
                simulate(child)

    simulate(root)

    return root


def count_stats(root):
    explored = 0
    pruned = 0
    def walk(n):
        nonlocal explored, pruned
        if n.pruned:
            pruned += 1
        else:
            explored += 1
        for _, c in n.children:
            walk(c)
    walk(root)
    return explored, pruned


# --- Graphviz renderer ---

STYLE_ACTIVE = {
    "normal":     ("#e3f2fd", "#1565c0", "#1565c0"),
    "infeasible": ("#ffebee", "#c62828", "#ef5350"),
    "suboptimal": ("#fff3e0", "#e65100", "#ffa726"),
    "optimal":    ("#c8e6c9", "#1b5e20", "#43a047"),
}

STYLE_PRUNED = {
    "normal":     ("#fafafa", "#cccccc", "#e0e0e0"),
    "infeasible": ("#fafafa", "#ddbbbb", "#e0d0d0"),
    "suboptimal": ("#fafafa", "#ddccbb", "#e0d8d0"),
    "optimal":    ("#fafafa", "#bbddbb", "#d0e0d0"),
}


def node_label(node, items):
    selected = [items[i].name for i, d in enumerate(node.decisions) if d == 1]
    sel_str = "{" + ",".join(selected) + "}" if selected else "∅"

    if node.pruned:
        return sel_str

    parts = [sel_str, f"{node.value}$", f"{node.weight}kg"]
    if node.depth < len(items):
        parts.append(f"≤{node.bound}$")
    return " ∣ ".join(parts)


def kind_marker(node):
    if node.kind == "infeasible":
        return "✗"
    if node.kind == "suboptimal":
        return "✗"
    if node.kind == "optimal":
        return "★"
    return ""


def to_dot(root, items, title=""):
    lines = []
    lines.append("digraph G {")
    lines.append(f'  label="{title}";')
    lines.append("  labelloc=t;")
    lines.append("  fontsize=13;")
    lines.append('  fontname="Helvetica";')
    lines.append("  rankdir=LR;")
    lines.append("  nodesep=0.12;")
    lines.append("  ranksep=0.4;")
    lines.append('  node [shape=box, style="filled,rounded", fontname="Helvetica",'
                 ' fontsize=8, height=0.25, margin="0.06,0.03"];')
    lines.append('  edge [fontname="Helvetica", fontsize=7, arrowsize=0.5];')
    lines.append("")

    def emit(node):
        styles = STYLE_PRUNED if node.pruned else STYLE_ACTIVE
        fill, font, border = styles[node.kind]
        pw = 2.0 if (node.kind == "optimal" and not node.pruned) else (0.8 if node.pruned else 1.2)

        label = node_label(node, items)
        marker = kind_marker(node)
        if marker and not node.pruned:
            label = f"{label}  {marker}"

        lines.append(f'  {node.id} [label="{label}", '
                     f'fillcolor="{fill}", fontcolor="{font}", color="{border}", penwidth={pw}];')

        for edge_label, child in node.children:
            if child.pruned:
                ecolor = "#e0e0e0"
                elabel = ""
            else:
                ecolor = "#555555"
                elabel = f" {edge_label} "
            lines.append(f'  {node.id} -> {child.id} [label="{elabel}", '
                         f'style=solid, color="{ecolor}", fontcolor="{ecolor}"];')
            emit(child)

    emit(root)
    lines.append("}")
    return "\n".join(lines)


def render(dot_source, output_path):
    dot_path = output_path.replace(".svg", ".dot")
    with open(dot_path, "w") as f:
        f.write(dot_source)
    try:
        subprocess.run(["dot", "-Tsvg", "-o", output_path, dot_path],
                       check=True, capture_output=True, text=True)
        size_kb = os.path.getsize(output_path) / 1024
        print(f"  {output_path.split('/')[-1]:40s} {size_kb:6.0f}K")
    except FileNotFoundError:
        print(f"  WARNING: graphviz 'dot' not found. Wrote {dot_path}")
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e.stderr[:200]}")


def main():
    items = [
        Item("A", 6, 11),
        Item("B", 5, 9),
        Item("C", 4, 7),
        Item("D", 3, 4),
    ]
    capacity = 9
    optimal_value = 16
    total_nodes = 31

    header = (f"Items: {', '.join(f'{it.name}(w={it.weight},v={it.value})' for it in items)}"
              f"  ∣  Capacity: {capacity}")
    out_dir = os.path.dirname(os.path.abspath(__file__))

    configs = [
        ("no_pruning",     "No Pruning",                    False, False, None),
        ("feas_only",      "Feasibility Pruning",           True,  False, None),
        ("feas_opt",       "Feasibility + Bound Pruning",   True,  True,  None),
        ("feas_opt_known", f"Feas + Bound + Known Best={optimal_value}$",
         True, True, optimal_value),
    ]

    for suffix, label, pf, po, kb in configs:
        root = build_full_tree(items, capacity, prune_feasibility=pf, prune_optimality=po,
                               known_best=kb)
        explored, pruned = count_stats(root)
        title = f"{label}  —  {explored} explored / {total_nodes} total\\n{header}"
        dot = to_dot(root, items, title)
        path = os.path.join(out_dir, f"knapsack_tree_{suffix}.svg")
        render(dot, path)
        print(f"    {label}: {explored} explored, {pruned} pruned")

    # Ordering comparison
    print("\n  --- Ordering comparison (feas + bound pruning) ---")

    best_order = [
        Item("B", 5, 9),
        Item("A", 6, 11),
        Item("C", 4, 7),
        Item("D", 3, 4),
    ]
    worst_order = list(reversed(items))

    for label, order, suffix in [
        ("Best ordering",  best_order,  "order_best"),
        ("Worst ordering", worst_order, "order_worst"),
    ]:
        root = build_full_tree(order, capacity, prune_feasibility=True, prune_optimality=True)
        explored, pruned = count_stats(root)
        hdr = (f"Items: {', '.join(f'{it.name}(w={it.weight},v={it.value})' for it in order)}"
               f"  ∣  Capacity: {capacity}")
        title = f"{label}  —  {explored} explored / {total_nodes} total\\n{hdr}"
        dot = to_dot(root, order, title)
        path = os.path.join(out_dir, f"knapsack_tree_{suffix}.svg")
        render(dot, path)
        print(f"    {label}: {explored} explored, {pruned} pruned")


if __name__ == "__main__":
    main()
