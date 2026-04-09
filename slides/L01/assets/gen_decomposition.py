"""Generate a decomposition flow diagram for dark slides.

Shows master/subproblem loop: Route Planning (MIP) ↔ Packing Check (CP).

Run from the assets/ directory:
    python gen_decomposition.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG_COLOR = "none"
COLOR_BOX_MASTER = "#2980b9"
COLOR_BOX_SUB = "#27ae60"
COLOR_TEXT = "#ecf0f1"
COLOR_ARROW = "#ecf0f1"
COLOR_LABEL = "#bdc3c7"

fig, ax = plt.subplots(figsize=(5, 6))
fig.patch.set_alpha(0)
ax.set_facecolor("none")
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis("off")

# Master box
master = patches.FancyBboxPatch(
    (1.5, 8.5), 7, 2,
    boxstyle="round,pad=0.3",
    facecolor=COLOR_BOX_MASTER, edgecolor=COLOR_TEXT, linewidth=1.5, alpha=0.9,
)
ax.add_patch(master)
ax.text(5, 9.8, "Master", color=COLOR_TEXT, fontsize=16, fontweight="bold",
        ha="center", va="center")
ax.text(5, 9.0, "Route Planning (MIP)", color=COLOR_TEXT, fontsize=13,
        ha="center", va="center", style="italic")

# Subproblem box
sub = patches.FancyBboxPatch(
    (1.5, 3.5), 7, 2,
    boxstyle="round,pad=0.3",
    facecolor=COLOR_BOX_SUB, edgecolor=COLOR_TEXT, linewidth=1.5, alpha=0.9,
)
ax.add_patch(sub)
ax.text(5, 4.8, "Subproblem", color=COLOR_TEXT, fontsize=16, fontweight="bold",
        ha="center", va="center")
ax.text(5, 4.0, "Packing Check (CP)", color=COLOR_TEXT, fontsize=13,
        ha="center", va="center", style="italic")

# Down arrow (solution / assignment)
ax.annotate(
    "", xy=(3.5, 5.7), xytext=(3.5, 8.3),
    arrowprops=dict(
        arrowstyle="-|>", color=COLOR_ARROW, lw=4,
        mutation_scale=25,
    ),
)
ax.text(1.8, 7.0, "routes", color=COLOR_LABEL, fontsize=14, fontweight="bold",
        ha="center", va="center", rotation=90)

# Up arrow (feedback / cuts)
ax.annotate(
    "", xy=(6.5, 8.3), xytext=(6.5, 5.7),
    arrowprops=dict(
        arrowstyle="-|>", color="#e74c3c", lw=4,
        mutation_scale=25,
    ),
)
ax.text(8.4, 7.0, "feedback", color="#e74c3c", fontsize=14, fontweight="bold",
        ha="center", va="center", rotation=90, style="italic")

plt.tight_layout(pad=0.5)

OUTPUT = "/home/krupke/Cloud/Dropbox/Secretary/cases/course-ae-ss26-internal/week01-l01-overview/slides/assets/decomposition_flow.svg"
fig.savefig(OUTPUT, transparent=True, bbox_inches="tight")
print(f"Saved {OUTPUT}")
