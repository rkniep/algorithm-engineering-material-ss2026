"""Generate a 2D bin packing visualization for dark slides.

Packs rectangles into a strip of fixed width, minimizing height.
Uses CP-SAT's add_no_overlap_2d constraint.

Run from the assets/ directory:
    python gen_binpacking.py
"""

from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random

# -- Parameters --
SEED = 7
W = 20  # strip width
random.seed(SEED)

# Generate random boxes
boxes = [(random.randint(2, 8), random.randint(2, 6)) for _ in range(12)]

# Upper bound on height
H_max = sum(h for _, h in boxes)

# -- Solve with CP-SAT --
model = cp_model.CpModel()

x_vars, y_vars = [], []
x_ivls, y_ivls = [], []

height = model.new_int_var(0, H_max, "height")

for i, (w, h) in enumerate(boxes):
    x = model.new_int_var(0, W - w, f"x_{i}")
    y = model.new_int_var(0, H_max - h, f"y_{i}")
    x_vars.append(x)
    y_vars.append(y)
    x_ivls.append(model.new_fixed_size_interval_var(x, w, f"xi_{i}"))
    y_ivls.append(model.new_fixed_size_interval_var(y, h, f"yi_{i}"))
    model.add(y + h <= height)

model.add_no_overlap_2d(x_ivls, y_ivls)
model.minimize(height)

solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 30
status = solver.solve(model)

assert status in (cp_model.OPTIMAL, cp_model.FEASIBLE)
H_sol = solver.value(height)
print(f"Packed {len(boxes)} boxes into {W} x {H_sol} strip")

# -- Plot --
# Color palette for boxes (warm/cool mix on dark background)
palette = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#3498db",
    "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
]

fig, ax = plt.subplots(1, 1, figsize=(5, 5))
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.set_xlim(-0.5, W + 0.5)
ax.set_ylim(-0.5, H_sol + 0.5)
ax.set_aspect("equal")
ax.axis("off")

# Draw container outline
container = patches.Rectangle(
    (0, 0), W, H_sol,
    linewidth=1.5, edgecolor="#7f8c8d", facecolor="none", linestyle="--"
)
ax.add_patch(container)

# Draw boxes
for i, (w, h) in enumerate(boxes):
    bx = solver.value(x_vars[i])
    by = solver.value(y_vars[i])
    color = palette[i % len(palette)]
    rect = patches.FancyBboxPatch(
        (bx + 0.1, by + 0.1), w - 0.2, h - 0.2,
        boxstyle="round,pad=0.1",
        facecolor=color, edgecolor="white", linewidth=0.8, alpha=0.85,
    )
    ax.add_patch(rect)

OUTPUT = "/home/krupke/Cloud/Dropbox/Secretary/cases/course-ae-ss26-internal/week01-l01-overview/slides/assets/binpacking.svg"
plt.tight_layout(pad=0.5)
fig.savefig(OUTPUT, transparent=True, bbox_inches="tight")
print(f"Saved {OUTPUT}")
