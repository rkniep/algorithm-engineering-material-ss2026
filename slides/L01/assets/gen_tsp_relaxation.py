"""Generate side-by-side TSP plots for dark slides: optimal tour vs LP relaxation.

Uses Gurobi via the alglab TSP solvers. Edge width encodes fractional values
in the relaxation plot. Styled for dark reveal.js slides (transparent background,
light-colored elements).

Run from the assets/ directory:
    python gen_tsp_relaxation.py
"""

import sys
import random

sys.path.insert(
    0,
    "/home/krupke/Repositories/alglab_winter2526_internal/sheets/04_mip/exercises/01_tsp",
)

import matplotlib.pyplot as plt
import networkx as nx

from solution_dantzig import GurobiTspSolver
from solution_relaxation import GurobiTspRelaxationSolver

# -- Parameters --
N = 100
SEED = 42
OUTPUT = "/home/krupke/Cloud/Dropbox/Secretary/cases/course-ae-ss26-internal/week01-l01-overview/slides/assets/tsp_side_by_side.svg"

# Dark-slide colors
COLOR_NODE = "#f39c12"
COLOR_EDGE_TOUR = "#ecf0f1"  # light gray for optimal tour
COLOR_EDGE_INTEGRAL = "#ecf0f1"
COLOR_EDGE_FRACTIONAL = "#e74c3c"  # red for fractional edges
COLOR_TITLE = "#ecf0f1"
EDGE_WIDTH_MAX = 2.5  # width for fully-used edges (tour and integral relaxation)

# -- Generate instance --
random.seed(SEED)
points = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(N)]


def eucl_dist(p1, p2):
    return round(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5)


G = nx.Graph()
for i in range(N):
    for j in range(i + 1, N):
        G.add_edge(i, j, weight=eucl_dist(points[i], points[j]))

pos = {i: points[i] for i in range(N)}

# -- Solve --
print("Solving optimal TSP...")
solver = GurobiTspSolver(G)
solver.solve(time_limit=60)
tour = solver.get_solution()
tour_obj = solver.get_objective()
print(f"Optimal tour: {tour_obj:.0f}")

print("Solving LP relaxation (k=2)...")
relax_solver = GurobiTspRelaxationSolver(G, k=2)
relax_solver.solve()
relaxation = relax_solver.get_solution()
relax_obj = relax_solver.get_objective()
print(f"LP relaxation: {relax_obj:.2f}")

# -- Plot --
fig, (ax_tour, ax_relax) = plt.subplots(1, 2, figsize=(12, 5.5))
fig.patch.set_alpha(0)

for ax in (ax_tour, ax_relax):
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_facecolor("none")

# Left: optimal tour
ax_tour.set_title(f"Optimal Tour (cost: {tour_obj:.0f})",
                   color=COLOR_TITLE, fontsize=18, fontweight="bold", pad=12)
nx.draw_networkx_nodes(tour, pos, ax=ax_tour, node_size=40, node_color=COLOR_NODE,
                       edgecolors="none")
nx.draw_networkx_edges(
    tour, pos, ax=ax_tour, edge_color=COLOR_EDGE_TOUR, width=EDGE_WIDTH_MAX, alpha=0.95
)

# Right: LP relaxation with edge width = fractional value
ax_relax.set_title(
    f"LP Relaxation (cost: {relax_obj:.0f})",
    color=COLOR_TITLE, fontsize=18, fontweight="bold", pad=12,
)

# Collect all edges with their fractional values
all_edges = []
for u, v, d in relaxation.edges(data=True):
    x_val = d["x"]
    if x_val > 0.01:
        all_edges.append((u, v, x_val))

# Sort so fractional edges draw on top of integral ones
all_edges.sort(key=lambda e: e[2], reverse=True)

# Draw nodes first (all N nodes)
node_graph = nx.Graph()
node_graph.add_nodes_from(range(N))
nx.draw_networkx_nodes(node_graph, pos, ax=ax_relax, node_size=40,
                       node_color=COLOR_NODE, edgecolors="none")

# Draw each edge with width proportional to its value
for u, v, x_val in all_edges:
    color = COLOR_EDGE_INTEGRAL if x_val > 0.99 else COLOR_EDGE_FRACTIONAL
    width = x_val * EDGE_WIDTH_MAX
    alpha = 0.95 if x_val > 0.99 else 0.5 + 0.4 * x_val
    nx.draw_networkx_edges(
        nx.Graph([(u, v)]), pos, ax=ax_relax,
        edge_color=color, width=width, alpha=alpha,
    )

plt.tight_layout(pad=1.5)
plt.savefig(OUTPUT, transparent=True, bbox_inches="tight")
print(f"Saved {OUTPUT}")

# -- Also save standalone tour image --
OUTPUT_TOUR = OUTPUT.replace("side_by_side", "tour_dark")
fig2, ax2 = plt.subplots(1, 1, figsize=(7, 6))
fig2.patch.set_alpha(0)
ax2.set_aspect("equal", adjustable="box")
ax2.axis("off")
ax2.set_facecolor("none")

ax2.set_title(f"Cost: {tour_obj:.0f}", color=COLOR_TITLE, fontsize=20,
              fontweight="bold", pad=14)
nx.draw_networkx_nodes(tour, pos, ax=ax2, node_size=40, node_color=COLOR_NODE,
                       edgecolors="none")
nx.draw_networkx_edges(
    tour, pos, ax=ax2, edge_color=COLOR_EDGE_TOUR, width=EDGE_WIDTH_MAX, alpha=0.95
)

plt.tight_layout(pad=0.5)
fig2.savefig(OUTPUT_TOUR, transparent=True, bbox_inches="tight")
print(f"Saved {OUTPUT_TOUR}")

# -- Also save standalone relaxation image --
OUTPUT_RELAX = OUTPUT.replace("side_by_side", "relaxation_dark")
fig3, ax3 = plt.subplots(1, 1, figsize=(7, 6))
fig3.patch.set_alpha(0)
ax3.set_aspect("equal", adjustable="box")
ax3.axis("off")
ax3.set_facecolor("none")

ax3.set_title(f"Cost: {relax_obj:.0f}", color=COLOR_TITLE, fontsize=20,
              fontweight="bold", pad=14)
node_graph = nx.Graph()
node_graph.add_nodes_from(range(N))
nx.draw_networkx_nodes(node_graph, pos, ax=ax3, node_size=40, node_color=COLOR_NODE,
                       edgecolors="none")

for u, v, x_val in all_edges:
    color = COLOR_EDGE_INTEGRAL if x_val > 0.99 else COLOR_EDGE_FRACTIONAL
    width = x_val * EDGE_WIDTH_MAX
    alpha = 0.95 if x_val > 0.99 else 0.5 + 0.4 * x_val
    nx.draw_networkx_edges(
        nx.Graph([(u, v)]), pos, ax=ax3,
        edge_color=color, width=width, alpha=alpha,
    )

plt.tight_layout(pad=0.5)
fig3.savefig(OUTPUT_RELAX, transparent=True, bbox_inches="tight")
print(f"Saved {OUTPUT_RELAX}")
