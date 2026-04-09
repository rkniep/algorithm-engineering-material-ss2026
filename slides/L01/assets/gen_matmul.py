"""Generate a classic matrix multiplication diagram: row of A × column of B → element of C."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, axes = plt.subplots(1, 3, figsize=(10, 4))
fig.patch.set_alpha(0)

n = 4  # matrix size
highlight_row = 1
highlight_col = 2

colors = {
    "default": "#2c3e50",
    "row": "#e74c3c",
    "col": "#3498db",
    "element": "#9b59b6",
    "text": "#ecf0f1",
    "label": "#ecf0f1",
}


def draw_matrix(ax, label, highlight=None):
    """Draw an n×n grid. highlight: 'row', 'col', or 'element'."""
    ax.set_xlim(-0.1, n + 0.1)
    ax.set_ylim(-0.6, n + 0.6)
    ax.set_aspect("equal")
    ax.axis("off")

    for i in range(n):
        for j in range(n):
            color = colors["default"]
            if highlight == "row" and i == highlight_row:
                color = colors["row"]
            elif highlight == "col" and j == highlight_col:
                color = colors["col"]
            elif highlight == "element" and i == highlight_row and j == highlight_col:
                color = colors["element"]

            rect = patches.FancyBboxPatch(
                (j + 0.05, n - 1 - i + 0.05),
                0.9,
                0.9,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor="#7f8c8d",
                linewidth=0.5,
            )
            ax.add_patch(rect)

    ax.text(
        n / 2,
        -0.4,
        label,
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color=colors["label"],
    )


draw_matrix(axes[0], "A", highlight="row")
draw_matrix(axes[1], "B", highlight="col")
draw_matrix(axes[2], "C", highlight="element")

# Add × and = signs (vertically aligned with matrix centers, not figure center)
fig.text(0.335, 0.53, "×", ha="center", va="center", fontsize=28, color=colors["text"])
fig.text(0.665, 0.53, "=", ha="center", va="center", fontsize=28, color=colors["text"])

plt.tight_layout(pad=1.5)
plt.savefig(
    "/home/krupke/Cloud/Dropbox/Secretary/cases/course-ae-ss26-internal/week01-l01-overview/slides/assets/matmul_diagram.png",
    dpi=150,
    transparent=True,
    bbox_inches="tight",
)
print("Saved matmul_diagram.png")
