# -*- coding: utf-8 -*-
"""Temperature-chart style visualisation (matplotlib)."""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DISCLAIMER_SHORT = "Heuristic self-observation only. NOT a medical measurement, diagnosis, or validated scale."

def plot_condition(rows, path, title="Shin-MBC — condition over time"):
    dates = [r["date"] for r in rows]
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.6], "hspace": 0.25})
    ax = axes[0]
    ax.axhspan(70, 100, color="#d9f2d9", zorder=0)
    ax.axhspan(40, 70, color="#fff6cc", zorder=0)
    ax.axhspan(0, 40, color="#fde0e0", zorder=0)
    ax.plot(dates, [r["condition"] for r in rows], marker="o", ms=3, lw=1.1, color="#90a4ae", label="daily score")
    if "condition_7d" in rows[0]:
        ax.plot(dates, [r["condition_7d"] for r in rows], lw=2.4, color="#1565c0", label="7-day average")
    ax.set_ylim(0, 100); ax.set_ylabel("condition score (higher = better-ish)")
    ax.grid(alpha=.25); ax.legend(fontsize=9)
    ax.set_title(f"{title}\n{DISCLAIMER_SHORT}", fontsize=12, loc="left")
    ax = axes[1]
    ax.bar(dates, [r["night_ratio_pct"] for r in rows], color="#3949ab", alpha=.75)
    ax.set_ylabel("posts 00:00-05:00 (%)"); ax.grid(alpha=.25)
    fig.savefig(path, dpi=170, bbox_inches="tight"); plt.close(fig)
    return path
