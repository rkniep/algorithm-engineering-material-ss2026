"""
Generate the "algorithm wall" plot for the slide after "NP-hard ≠ unsolvable".

Three exponential runtime curves hit a time-budget line at different problem
sizes, illustrating two independent levers:
  1. Reduce the constant factor  → curve shifts DOWN  → wall moves right a little
  2. Reduce the effective base   → curve bends flatter → wall moves right a lot

Runtime model (log scale y-axis so all curves are visible):
  Curve 1 — brute force:         c1 * 2^n,   c1 = 1e-6 s  (μs/step)
  Curve 2 — better impl:         c2 * 2^n,   c2 = 1e-9 s  (ns/step)
  Curve 3 — smart pruning/B&B:   c2 * 1.5^n  (smaller effective branching factor)

Time budget: 3600 s (1 hour).  Crossings: n≈32, n≈42, n≈73.

Usage:
    python gen_algorithm_wall.py
"""

import matplotlib.pyplot as plt
import numpy as np
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Palette — match dark slide theme
C_BRUTE = "#e86450"   # red    — brute force
C_IMPL  = "#f0a030"   # amber  — better implementation
C_SMART = "#50b866"   # green  — smart pruning
C_LIMIT = "#cccccc"   # light  — time limit line
C_TEXT  = "#dddddd"
C_GRID  = "#333333"
C_LABEL = "#aaaaaa"

TIME_LIMIT = 3600.0   # seconds (1 hour)
C          = 1e-9          # per-step time
B1, B2     = 2.0, 1.5      # brute force vs smart (reduced effective branching factor)
N_MAX      = 80
Y_MIN      = 1e-10
Y_MAX      = TIME_LIMIT * 1e5


def crossing(c, base):
    return np.log(TIME_LIMIT / c) / np.log(base)


def main():
    ns = np.linspace(0, N_MAX + 5, 2000)   # extend slightly past window
    y1 = C * B1 ** ns   # red:   brute force
    y2 = C * B2 ** ns   # green: smart algorithm (reduced effective branching factor)

    n1 = crossing(C, B1)
    n2 = crossing(C, B2)

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_alpha(0)
    ax.set_facecolor("none")

    # Shaded tractable region (below time budget)
    ax.axhspan(0, TIME_LIMIT, alpha=0.06, color=C_SMART, zorder=0)

    # Time-budget line — this IS the wall
    ax.axhline(TIME_LIMIT, color=C_LIMIT, linewidth=1.5, linestyle="--", zorder=2)

    # Two curves — linear scale, clipped at ylim so they shoot off the top
    ax.plot(ns, y1, color=C_BRUTE, linewidth=2.2, zorder=3)
    ax.plot(ns, y2, color=C_SMART, linewidth=2.2, zorder=3)

    # ── Axes ────────────────────────────────────────────────────────────────
    ax.set_xlim(0, N_MAX)
    ax.set_ylim(0, TIME_LIMIT * 1.15)
    ax.axis("off")

    plt.tight_layout(pad=0.4)

    out = os.path.join(OUT_DIR, "algorithm_wall.svg")
    fig.savefig(out, bbox_inches="tight", transparent=True)
    plt.close(fig)
    print(f"  {'algorithm_wall.svg':35s} ({os.path.getsize(out) / 1024:.0f}K)")


if __name__ == "__main__":
    main()
