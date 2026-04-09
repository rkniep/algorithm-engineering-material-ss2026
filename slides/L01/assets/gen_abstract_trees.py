"""
Generate abstract search tree illustrations for the "NP-hard ≠ unsolvable" slide.

Compact matplotlib rendering — positions computed directly, no graphviz needed.
Trees are drawn top-down with dots and lines. Pruned subtrees are grayed out.

Usage:
    python gen_abstract_trees.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
DEPTH = 8

# Colors
C_ACTIVE = "#4a90d9"
C_PRUNED = "#333333"
C_CUT    = "#e86450"
C_BOUND  = "#f0a030"
C_SOLUTION = "#50b866"
C_PROPAGATED = "#90c0e8"
C_EDGE_ACTIVE = "#aaaaaa"
C_EDGE_PRUNED = "#222222"


def build_tree(depth):
    """Build full binary tree. Returns dict: id -> (depth, left_id, right_id)"""
    nodes = {}
    counter = [0]

    def make(d):
        counter[0] += 1
        nid = counter[0]
        if d == depth:
            nodes[nid] = (d, None, None)
        else:
            left = make(d + 1)
            right = make(d + 1)
            nodes[nid] = (d, left, right)
        return nid

    root = make(0)
    return root, nodes


def get_node_by_path(root, nodes, path):
    """Navigate tree by path: 0=left, 1=right."""
    nid = root
    for p in path:
        d, left, right = nodes[nid]
        nid = left if p == 0 else right
    return nid


def subtree_ids(nid, nodes):
    """All ids in subtree rooted at nid."""
    result = {nid}
    d, left, right = nodes[nid]
    if left:
        result |= subtree_ids(left, nodes)
    if right:
        result |= subtree_ids(right, nodes)
    return result


def children_ids(nid, nodes):
    """All ids in subtree excluding the root."""
    return subtree_ids(nid, nodes) - {nid}


def compute_positions(root, nodes):
    """Compute (x, y) using fixed offsets that shrink per level for a tight layout."""
    positions = {}

    def layout(nid, x, y, spread):
        positions[nid] = (x, y)
        d, left, right = nodes[nid]
        if left is not None:
            layout(left,  x - spread, y + 1, spread / 2)
            layout(right, x + spread, y + 1, spread / 2)

    layout(root, 0, 0, 2 ** (DEPTH - 1))
    return positions


def draw_tree(root, nodes, positions, colors, filename, figsize=(16, 4)):
    """Draw the tree with matplotlib."""
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    ax.axis("off")

    # Draw edges first (behind nodes)
    def draw_edges(nid):
        d, left, right = nodes[nid]
        px, py = positions[nid]
        for child in [left, right]:
            if child is not None:
                cx, cy = positions[child]
                ecolor = C_EDGE_PRUNED if colors.get(child, C_ACTIVE) == C_PRUNED else C_EDGE_ACTIVE
                lw = 1.0 if ecolor == C_EDGE_PRUNED else 1.5
                ax.plot([px, cx], [-py, -cy], color=ecolor, linewidth=lw, zorder=1)
                draw_edges(child)

    draw_edges(root)

    # Draw nodes
    xs = [positions[nid][0] for nid in nodes]
    xmin, xmax = min(xs), max(xs)
    # Node size scales with tree width
    node_size = max(2.0, 5000 / len(nodes))

    for nid in nodes:
        x, y = positions[nid]
        color = colors.get(nid, C_ACTIVE)
        s = node_size * (0.7 if color == C_PRUNED else 1.0)
        zorder = 2 if color == C_PRUNED else 3
        ax.scatter(x, -y, c=color, s=s, zorder=zorder, edgecolors="none")

    ax.margins(0.02)
    plt.tight_layout(pad=0.5)

    path = os.path.join(OUT_DIR, filename)
    fig.savefig(path, dpi=200, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"  {filename:35s} ({os.path.getsize(path) / 1024:.0f}K)")


def apply_cuts(root, nodes, colors, cut_paths, cut_color):
    """Mark cut nodes with cut_color, gray out their children."""
    for path in cut_paths:
        nid = get_node_by_path(root, nodes, path)
        colors[nid] = cut_color
        for cid in children_ids(nid, nodes):
            colors[cid] = C_PRUNED


def apply_propagation(root, nodes, colors, prop_points):
    """Propagation: force one branch, gray out the other."""
    for path, forced_dir in prop_points:
        nid = get_node_by_path(root, nodes, path)
        colors[nid] = C_PROPAGATED
        d, left, right = nodes[nid]
        # Gray out the non-forced branch
        other = right if forced_dir == 0 else left
        if other:
            for sid in subtree_ids(other, nodes):
                colors[sid] = C_PRUNED


def main():
    root, nodes = build_tree(DEPTH)
    positions = compute_positions(root, nodes)
    total = len(nodes)

    # 1. Full tree
    colors = {nid: C_ACTIVE for nid in nodes}
    draw_tree(root, nodes, positions, colors, "tree_full.svg")
    print(f"    {total} active / {total} total")

    # 2. Pruned (feasibility cuts)
    colors = {nid: C_ACTIVE for nid in nodes}
    feas_cuts = [
        [0, 0],
        [0, 1, 0],
        [0, 1, 1, 0],
        [0, 1, 1, 1, 0, 0],
        [0, 1, 1, 1, 1],
        [1, 0],
        [1, 1, 0, 0],
        [1, 1, 0, 1, 1],
        [1, 1, 1, 0],
        [1, 1, 1, 1, 1],
    ]
    apply_cuts(root, nodes, colors, feas_cuts, C_CUT)
    active = sum(1 for c in colors.values() if c != C_PRUNED)
    draw_tree(root, nodes, positions, colors, "tree_pruned.svg")
    print(f"    {active} active / {total} total")

    # 3. Pruned + bounded
    colors_bounded = dict(colors)  # start from pruned state
    bound_cuts = [
        [0, 1, 1, 1, 0, 1, 1],
        [1, 1, 0, 1, 0],
        [1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 0, 1],
    ]
    # Solution node
    sol_path = [0, 1, 1, 1, 0, 1, 0, 1]
    sol_nid = get_node_by_path(root, nodes, sol_path)
    colors_bounded[sol_nid] = C_SOLUTION
    apply_cuts(root, nodes, colors_bounded, bound_cuts, C_BOUND)
    active = sum(1 for c in colors_bounded.values() if c != C_PRUNED)
    draw_tree(root, nodes, positions, colors_bounded, "tree_bounded.svg")
    print(f"    {active} active / {total} total")

    # 4. Pruned + bounded + propagation
    colors_prop = dict(colors_bounded)
    prop_points = [
        ([0, 1, 1, 1], 0),
        ([0, 1, 1, 1, 0, 1], 0),
        ([1, 1, 1, 1], 0),
    ]
    apply_propagation(root, nodes, colors_prop, prop_points)
    # Re-mark solution
    colors_prop[sol_nid] = C_SOLUTION
    active = sum(1 for c in colors_prop.values() if c != C_PRUNED)
    draw_tree(root, nodes, positions, colors_prop, "tree_propagated.svg")
    print(f"    {active} active / {total} total")


if __name__ == "__main__":
    main()
