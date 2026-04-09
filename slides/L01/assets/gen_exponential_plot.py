"""
Generate an exponential growth plot for the "Brute force is not an option" slide.

Linear scale (no log) so the explosion is visceral — the curve is flat, then
goes almost vertical. x-range capped at 60 so the dramatic part dominates.

Usage:
    python gen_exponential_plot.py
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Match dark slide theme
C_LINE  = "#4a90d9"   # same blue as tree nodes
C_ANN   = "#e86450"   # same red as cut nodes
C_TEXT  = "#dddddd"
C_GRID  = "#333333"
C_LABEL = "#aaaaaa"

N_MAX = 60   # beyond this it's literally off the chart — that's the point


def fmt_large(v):
    """Format huge floats as 10^k strings."""
    if v <= 0:
        return "0"
    exp = int(np.floor(np.log10(v)))
    return f"$10^{{{exp}}}$"


def main():
    ns = np.linspace(0, N_MAX + 3, 500)
    values = 2.0 ** ns

    fig, ax = plt.subplots(figsize=(7, 3.5))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    ax.plot(ns, values, color=C_LINE, linewidth=2.5, zorder=3)

    # Annotate n=50
    n50, v50 = 50, 2.0 ** 50
    ax.axvline(n50, color=C_ANN, linewidth=1.0, linestyle="--", zorder=2, alpha=0.7)
    ax.scatter([n50], [v50], color=C_ANN, s=60, zorder=4)
    ax.annotate(
        "n = 50\n≈ 13 days",
        xy=(n50, v50),
        xytext=(0.6, 0.25),
        textcoords="axes fraction",
        ha="left",
        va="center",
        color=C_TEXT,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=C_ANN, lw=1.0,
                        connectionstyle="arc3,rad=-0.2"),
    )

    # Arrow + label pointing off the top for n=100
    ax.annotate(
        "n = 100\n> 31 000 years\n(way off this chart)",
        xy=(N_MAX, 2.0 ** N_MAX),
        xytext=(47, 2.0 ** N_MAX * 0.7),
        textcoords="data",
        ha="left",
        va="top",
        color=C_TEXT,
        fontsize=9,
        arrowprops=dict(arrowstyle="->", color=C_ANN, lw=1.0),
    )

    # Axes
    ax.set_xlabel("Number of items  $n$", color=C_LABEL, fontsize=10)
    ax.set_ylabel("Subsets  $2^n$", color=C_LABEL, fontsize=10)
    ax.tick_params(colors=C_LABEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(C_GRID)

    ax.set_xlim(0, N_MAX)
    ax.set_ylim(0, 2.0 ** N_MAX)

    # Y-axis: show only a couple of ticks with scientific notation
    ymax = 2.0 ** N_MAX
    ax.set_yticks([0, ymax / 2, ymax])
    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(lambda v, _: fmt_large(v) if v > 0 else "0")
    )

    ax.grid(True, which="major", color=C_GRID, linewidth=0.5, zorder=1)

    plt.tight_layout(pad=0.4)

    out = os.path.join(OUT_DIR, "exponential_growth.svg")
    fig.savefig(out, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"  {'exponential_growth.svg':35s} ({os.path.getsize(out) / 1024:.0f}K)")


if __name__ == "__main__":
    main()
