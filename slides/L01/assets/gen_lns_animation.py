"""Generate LNS TSP animation for dark slides.

Starts from a random tour, iteratively destroys a neighborhood and
re-optimizes it using CP-SAT's add_circuit constraint. Outputs a GIF.

Each iteration produces two frames:
  1. Destroy frame  — old tour with removed edges highlighted red
  2. Repair frame   — new tour with added edges highlighted green

Run from the assets/ directory:
    python gen_lns_animation.py
"""

import os
import random
import math
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ortools.sat.python import cp_model
from PIL import Image

# -- Parameters --
N = 150
K = 30  # destroy neighborhood size
SEED = 42
ITERATIONS = 40
BG_COLOR = "#1e1e2e"
COLOR_NODE = "#f39c12"
COLOR_EDGE = "#ecf0f1"
COLOR_DESTROY = "#e74c3c"
COLOR_REPAIR = "#50b866"
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(OUT_DIR, "lns_animation.gif")

random.seed(SEED)
points = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(N)]

# Precompute distance matrix
dist_matrix = [[0] * N for _ in range(N)]
for i in range(N):
    for j in range(i + 1, N):
        d = round(math.sqrt((points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2))
        dist_matrix[i][j] = d
        dist_matrix[j][i] = d

# Precompute nearest neighbors for each node
nearest = []
for i in range(N):
    nearest.append(
        sorted(range(N), key=lambda j, i=i: dist_matrix[i][j] if j != i else 999999)[:K]
    )


def tour_cost(tour):
    return sum(dist_matrix[tour[i]][tour[(i + 1) % N]] for i in range(N))


def tour_edge_set(tour):
    """Return set of canonical (min, max) node-index pairs for all tour edges."""
    return {
        (min(tour[i], tour[(i + 1) % N]), max(tour[i], tour[(i + 1) % N]))
        for i in range(N)
    }


# Initial random tour
tour = list(range(N))
random.shuffle(tour)


def lns_step(tour, center):
    """Destroy center's neighborhood and re-optimize with CP-SAT."""
    destroy = set(nearest[center]) | {center}

    succ = {tour[i]: tour[(i + 1) % N] for i in range(N)}

    model = cp_model.CpModel()
    arcs = []
    cost_terms = []

    for i in range(N):
        for j in range(N):
            if i == j:
                continue
            if i not in destroy and j not in destroy:
                if succ[i] == j:
                    arcs.append((i, j, True))
                continue
            lit = model.new_bool_var(f"a_{i}_{j}")
            arcs.append((i, j, lit))
            cost_terms.append(dist_matrix[i][j] * lit)

    model.add_circuit(arcs)
    model.minimize(sum(cost_terms))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        new_succ = {}
        for i, j, lit in arcs:
            if lit is True or solver.value(lit):
                new_succ[i] = j

        new_tour = [0]
        for _ in range(N - 1):
            new_tour.append(new_succ[new_tour[-1]])
        return new_tour, destroy

    return tour, destroy


def render_frame(tour, iteration, cost, red_edges=None, green_edges=None):
    """Render one animation frame.

    red_edges   — set of (min_node, max_node) pairs to draw in red (destroyed)
    green_edges — set of (min_node, max_node) pairs to draw in green (repaired)
    """
    fig, ax = plt.subplots(figsize=(7, 5.5))
    fig.patch.set_facecolor(BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-50, 1050)
    ax.set_ylim(-50, 1050)

    highlight = (red_edges or set()) | (green_edges or set())

    # Draw normal edges first (dim them if highlights are present)
    alpha_normal = 0.25 if highlight else 0.6
    for i in range(N):
        u, v = tour[i], tour[(i + 1) % N]
        key = (min(u, v), max(u, v))
        if key in highlight:
            continue  # drawn separately below
        p1, p2 = points[u], points[v]
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                color=COLOR_EDGE, linewidth=0.8, alpha=alpha_normal)

    # Draw highlighted edges on top
    for i in range(N):
        u, v = tour[i], tour[(i + 1) % N]
        key = (min(u, v), max(u, v))
        if key in (red_edges or set()):
            p1, p2 = points[u], points[v]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                    color=COLOR_DESTROY, linewidth=1.8, alpha=1.0, zorder=4)
        elif key in (green_edges or set()):
            p1, p2 = points[u], points[v]
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]],
                    color=COLOR_REPAIR, linewidth=1.8, alpha=1.0, zorder=4)

    # Nodes
    xs = [points[n][0] for n in tour]
    ys = [points[n][1] for n in tour]
    ax.scatter(xs, ys, c=COLOR_NODE, s=15, zorder=5, edgecolors="none")

    ax.set_title(
        f"Iteration {iteration} — Cost: {cost}",
        color="#ecf0f1", fontsize=14, fontweight="bold", pad=10,
    )

    buf = io.BytesIO()
    plt.tight_layout(pad=0.5)
    fig.savefig(buf, format="png", dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return Image.open(buf).copy()


# -- Run LNS and collect frames --
frames = []
durations = []
cost = tour_cost(tour)
print(f"Initial cost: {cost}")
frames.append(render_frame(tour, 0, cost))
durations.append(600)

rng = random.Random(SEED + 1)
for it in range(1, ITERATIONS + 1):
    center = rng.randint(0, N - 1)
    old_tour = tour
    old_edges = tour_edge_set(old_tour)

    tour, destroy = lns_step(tour, center)
    cost = tour_cost(tour)
    new_edges = tour_edge_set(tour)

    # Edges that were removed (touched destroy set) vs edges that are new
    destroyed_edges = {e for e in old_edges if e[0] in destroy or e[1] in destroy}
    subproblem_edges = {e for e in new_edges if e[0] in destroy or e[1] in destroy}

    print(f"Iteration {it}: cost = {cost}")

    # Frame 1: old tour, destroyed edges in red
    frames.append(render_frame(old_tour, it, tour_cost(old_tour), red_edges=destroyed_edges))
    durations.append(300)

    # Frame 2: new tour, full subproblem solution in green
    frames.append(render_frame(tour, it, cost, green_edges=subproblem_edges))
    durations.append(500)

# Hold last frame longer
for _ in range(8):
    frames.append(frames[-1])
    durations.append(500)

# Save GIF
frames[0].save(
    OUTPUT, save_all=True, append_images=frames[1:],
    duration=durations, loop=0,
)
print(f"Saved {OUTPUT}")
