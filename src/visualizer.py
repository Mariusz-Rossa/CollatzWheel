# Copyright (c) 2026 Mariusz Rossa
# Licensed under the MIT License — see LICENSE file for details.
# src/visualizer.py

"""
Collatz × Wheel Algebra visualisations.

Plots:
    plot_length_by_mod(results)         → boxplot of path lengths by start_mod
    plot_transition_heatmap(results)    → heatmap of Wheel transition frequencies
    plot_collatz_path(n)                → Collatz path with Wheel colouring
    plot_length_scatter(results)        → scatter: n vs length, colour=start_mod
    save_all(results, out_dir)          → saves all plots
"""

from __future__ import annotations
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from collections import Counter, defaultdict
from pathlib import Path

from collatz import collatz_sequence, collatz_metrics, wheel_signature
from analysis import batch_analysis, top_records


# ------------------------------------------------------------------ #
#  Wheel mod 6 colour palette                                        #
#  0=grey, 1=gold, 2=blue, 3=red, 4=green, 5=purple                  #
# ------------------------------------------------------------------ #

WHEEL_COLORS = {
    "0": "#6c757d",
    "1": "#f4a435",
    "2": "#4dabf7",
    "3": "#f03e3e",
    "4": "#51cf66",
    "5": "#cc5de8",
    "⊥": "#000000",
    "∞": "#ffffff",
}

DARK_BG    = "#0d1117"
PANEL_BG   = "#161b22"
TEXT_COLOR = "#e6edf3"
GRID_COLOR = "#21262d"


def _apply_dark_theme():
    plt.rcParams.update({
        "figure.facecolor":  DARK_BG,
        "axes.facecolor":    PANEL_BG,
        "axes.edgecolor":    GRID_COLOR,
        "axes.labelcolor":   TEXT_COLOR,
        "axes.titlecolor":   TEXT_COLOR,
        "xtick.color":       TEXT_COLOR,
        "ytick.color":       TEXT_COLOR,
        "text.color":        TEXT_COLOR,
        "grid.color":        GRID_COLOR,
        "grid.linewidth":    0.5,
        "font.family":       "monospace",
        "figure.dpi":        120,
    })


# ------------------------------------------------------------------ #
#  1. Boxplot: path length by start_mod                              #
# ------------------------------------------------------------------ #

def plot_length_by_mod(results: list[dict], save_path: str | None = None):
    _apply_dark_theme()
    fig, ax = plt.subplots(figsize=(10, 6))

    groups = defaultdict(list)
    for r in results:
        groups[str(r["start_mod"])].append(r["length"])

    labels  = sorted(groups.keys())
    data    = [groups[k] for k in labels]
    colors  = [WHEEL_COLORS.get(k, "#888") for k in labels]

    bp = ax.boxplot(data, patch_artist=True, labels=labels,
                    medianprops=dict(color="#ffffff", linewidth=2),
                    whiskerprops=dict(color=GRID_COLOR),
                    capprops=dict(color=GRID_COLOR),
                    flierprops=dict(marker="o", markersize=2, alpha=0.4))

    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)

    ax.set_title("Collatz path length by n mod 6  (starting Wheel signature))",
                 fontsize=13, pad=14)
    ax.set_xlabel("n mod 6", fontsize=11)
    ax.set_ylabel("Path length (steps to 1)", fontsize=11)
    ax.grid(axis="y", alpha=0.4)

    ax.annotate("mod=1 dominates →", xy=(1, max(groups["1"])),
                xytext=(2.2, max(groups["1"]) * 0.95),
                color=WHEEL_COLORS["1"], fontsize=9,
                arrowprops=dict(arrowstyle="->", color=WHEEL_COLORS["1"]))

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.show()


# ------------------------------------------------------------------ #
#  2. Wheel transition heatmap                                       #
# ------------------------------------------------------------------ #

def plot_transition_heatmap(results: list[dict], save_path: str | None = None):
    _apply_dark_theme()

    total: Counter = Counter()
    for r in results:
        for (a, b), cnt in r.get("top_transitions", []):
            total[(a, b)] += cnt

    labels = list(range(6))
    matrix = np.zeros((6, 6), dtype=float)
    for (a, b), cnt in total.items():
        if isinstance(a, int) and isinstance(b, int) and 0 <= a < 6 and 0 <= b < 6:
            matrix[a][b] = cnt

    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    matrix_norm = matrix / row_sums

    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(matrix_norm, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)

    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Transition frequency (row-normalised)", color=TEXT_COLOR)
    cbar.ax.yaxis.set_tick_params(color=TEXT_COLOR)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color=TEXT_COLOR)

    ax.set_xticks(range(6))
    ax.set_yticks(range(6))
    ax.set_xticklabels(labels)
    ax.set_yticklabels(labels)
    ax.set_xlabel("To (mod 6)", fontsize=11)
    ax.set_ylabel("From (mod 6)", fontsize=11)
    ax.set_title("Wheel transition heatmap:  P(a → b)  for n=1..N", fontsize=13, pad=14)

    for i in range(6):
        for j in range(6):
            val = matrix_norm[i][j]
            if val > 0.01:
                ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                        fontsize=8, color="black" if val > 0.5 else "white")

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        print(f"  Zapisano: {save_path}")
    plt.show()


# ------------------------------------------------------------------ #
#  3. Collatz path with Wheel colouring                              #
# ------------------------------------------------------------------ #

def plot_collatz_path(n: int, mod: int = 6, save_path: str | None = None):
    _apply_dark_theme()

    seq = collatz_sequence(n)
    sig = wheel_signature(n, mod)  
    colors = [WHEEL_COLORS.get(str(w), "#888") for w in sig]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8),
                                    gridspec_kw={"height_ratios": [4, 1]})

    for i in range(len(seq) - 1):
        ax1.plot([i, i+1], [seq[i], seq[i+1]], color=colors[i], linewidth=1.2, alpha=0.8)
    ax1.scatter(range(len(seq)), seq, c=colors, s=12, zorder=5)

    ax1.set_title(f"Collatz path  n={n}  "
                  f"(length={len(seq)-1}, max={max(seq)})",
                  fontsize=13, pad=12)
    ax1.set_ylabel("Value", fontsize=10)
    ax1.grid(alpha=0.3)
    ax1.set_yscale("log")

    for mod_val, color in WHEEL_COLORS.items():
        if mod_val.isdigit():
            ax1.plot([], [], "o", color=color, markersize=6,
                     label=f"mod6={mod_val}")
    ax1.legend(loc="upper right", fontsize=8, framealpha=0.3)

    for i, color in enumerate(colors):
        ax2.barh(0, 1, left=i, color=color, height=0.8, alpha=0.85)

    ax2.set_xlim(0, len(colors))
    ax2.set_ylim(-0.5, 0.5)
    ax2.set_xlabel("Sequence step", fontsize=10)
    ax2.set_yticks([])
    ax2.set_title("Wheel signature (colour = n mod 6)", fontsize=10, pad=6)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.show()


# ------------------------------------------------------------------ #
#  4. Scatter: n vs path length, colour = start_mod                  #
# ------------------------------------------------------------------ #

def plot_length_scatter(results: list[dict], save_path: str | None = None):
    _apply_dark_theme()
    fig, ax = plt.subplots(figsize=(14, 6))

    for mod_val in ["0", "1", "2", "3", "4", "5"]:
        subset = [r for r in results if str(r["start_mod"]) == mod_val]
        if not subset:
            continue
        xs = [r["start"]  for r in subset]
        ys = [r["length"] for r in subset]
        ax.scatter(xs, ys, c=WHEEL_COLORS[mod_val], s=4, alpha=0.6,
                   label=f"mod6={mod_val}")

    ax.set_title("Collatz path length vs n  (colour = n mod 6)", fontsize=13, pad=12)
    ax.set_xlabel("n", fontsize=11)
    ax.set_ylabel("Path length", fontsize=11)
    ax.legend(markerscale=3, fontsize=9, framealpha=0.3)
    ax.grid(alpha=0.3)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, bbox_inches="tight")
        print(f"  Saved: {save_path}")
    plt.show()


# ------------------------------------------------------------------ #
#  Save all plots                                                    #
# ------------------------------------------------------------------ #

def save_all(results: list[dict], out_dir: str = "data/results", mod: int = 6):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    print(f"\nSaving plots to {out_dir}/\n")

    plot_length_by_mod(results,       f"{out_dir}/01_length_by_mod.png")
    plot_transition_heatmap(results,  f"{out_dir}/02_transition_heatmap.png")
    plot_length_scatter(results,      f"{out_dir}/03_length_scatter.png")

    for r in top_records(results, 3):
        n = r["start"]
        plot_collatz_path(n, f"{out_dir}/04_path_n{n}.png", mod=mod)


# ------------------------------------------------------------------ #
#  Smoke-test                                                         #
# ------------------------------------------------------------------ #

if __name__ == "__main__":
    print("=== Visualizer — generating plots (n=1..2000) ===\n")
    results = batch_analysis(2000)
    save_all(results)
    print("\nDone!")