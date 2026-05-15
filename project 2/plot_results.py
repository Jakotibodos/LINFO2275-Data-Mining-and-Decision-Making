"""
Regenerates benchmark charts as PDF files from a saved benchmark_results.csv.

Usage:
    python plot_results.py
    python plot_results.py --csv benchmark_results/benchmark_results.csv --output_dir benchmark_results
"""

import argparse
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


REWARD_MODES = ["regular_reward","lines_flat", "lines_bonus", "per_block"]
CHECKPOINTS  = [50000, 100000, 150000, 200000, 250000, 300000]

COLORS = {
    "regular_reward":"#C64191", 
    "lines_flat":  "#2196F3",
    "lines_bonus": "#4CAF50",
    "per_block":   "#FF9800"
}



def get_args():
    parser = argparse.ArgumentParser(description="Regenerate benchmark charts from CSV")
    parser.add_argument("--csv",        type=str, default="benchmark_results/benchmark_results.csv")
    parser.add_argument("--output_dir", type=str, default="benchmark_results")
    return parser.parse_args()


def load_results(csv_path):
    df = pd.read_csv(csv_path)
    results = {mode: {} for mode in REWARD_MODES}
    for _, row in df.iterrows():
        mode = row["reward_mode"]
        ckpt = int(row["checkpoint"])
        if mode not in results:
            continue
        results[mode][ckpt] = {
            "mean_lines":       row["mean_lines"],
            "std_lines":        row["std_lines"],
            "mean_tetrominoes": row["mean_tetrominoes"],
            "std_tetrominoes":  row["std_tetrominoes"],
            "clear_distribution": {
                1: row["clears_1"],
                2: row["clears_2"],
                3: row["clears_3"],
                4: row["clears_4"],
            },
        }
    return results


def plot_lines_cleared(results, output_dir):
    fig, ax = plt.subplots(figsize=(12, 6))
    for mode in REWARD_MODES:
        mode_data = results[mode]
        if not mode_data:
            continue
        ckpts = sorted(mode_data.keys())
        means = [mode_data[c]["mean_lines"] for c in ckpts]
        stds  = [mode_data[c]["std_lines"]  for c in ckpts]
        ax.plot(ckpts, means, marker="o", linewidth=2, label=mode, color=COLORS[mode])
        ax.fill_between(ckpts,
                        [m - s for m, s in zip(means, stds)],
                        [m + s for m, s in zip(means, stds)],
                        alpha=0.15, color=COLORS[mode])
        ax.errorbar(ckpts, means, yerr=stds, fmt="none", ecolor=COLORS[mode],
                    elinewidth=1.2, capsize=5, capthick=1.2, alpha=0.7)
    ax.set_yscale("log")
    ax.set_xlabel("Training Checkpoint (epochs)", fontsize=13)
    ax.set_ylabel("Average Lines Cleared", fontsize=13)
    ax.set_title("Lines Cleared Across Training Checkpoints", fontsize=15)
    ax.set_xticks(CHECKPOINTS)
    ax.set_xticklabels([f"{c//1000}k" for c in CHECKPOINTS])
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    path = os.path.join(output_dir, "chart_lines_cleared.pdf")
    fig.savefig(path)
    print(f"Saved {path}")


def plot_blocks_placed(results, output_dir):
    fig, ax = plt.subplots(figsize=(12, 6))
    for mode in REWARD_MODES:
        mode_data = results[mode]
        if not mode_data:
            continue
        ckpts = sorted(mode_data.keys())
        means = [mode_data[c]["mean_tetrominoes"] for c in ckpts]
        stds  = [mode_data[c]["std_tetrominoes"]  for c in ckpts]
        ax.plot(ckpts, means, marker="o", linewidth=2, label=mode, color=COLORS[mode])
        ax.fill_between(ckpts,
                        [m - s for m, s in zip(means, stds)],
                        [m + s for m, s in zip(means, stds)],
                        alpha=0.15, color=COLORS[mode])
        ax.errorbar(ckpts, means, yerr=stds, fmt="none", ecolor=COLORS[mode],
                    elinewidth=1.2, capsize=5, capthick=1.2, alpha=0.7)
    ax.set_yscale("log")
    ax.set_xlabel("Training Checkpoint (epochs)", fontsize=13)
    ax.set_ylabel("Average Blocks Placed", fontsize=13)
    ax.set_title("Blocks Placed Across Training Checkpoints", fontsize=15)
    ax.set_xticks(CHECKPOINTS)
    ax.set_xticklabels([f"{c//1000}k" for c in CHECKPOINTS])
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    path = os.path.join(output_dir, "chart_blocks_placed.pdf")
    fig.savefig(path)
    print(f"Saved {path}")


def plot_clear_distribution(results, output_dir):
    clear_labels = [1, 2, 3, 4]
    clear_colors = ["#90CAF9", "#42A5F5", "#1565C0", "#0D47A1"]

    mode_pcts = {}
    for mode in REWARD_MODES:
        dist = results[mode].get(300000, {}).get("clear_distribution")
        if dist is None:
            continue
        total = sum(dist.get(k, 0) for k in clear_labels)
        if total == 0:
            mode_pcts[mode] = [0, 0, 0, 0]
        else:
            mode_pcts[mode] = [100.0 * dist.get(k, 0) / total for k in clear_labels]

    if not mode_pcts:
        print("No 300k checkpoints found — skipping clear distribution chart.")
        return

    modes = list(mode_pcts.keys())
    fig, ax = plt.subplots(figsize=(10, 2.5 + len(modes) * 0.8))

    bar_height = 0.5
    y_positions = np.arange(len(modes))

    lefts = np.zeros(len(modes))
    for i, (n_lines, color) in enumerate(zip(clear_labels, clear_colors)):
        values = [mode_pcts[m][i] for m in modes]
        bars = ax.barh(y_positions, values, left=lefts, height=bar_height,
                       color=color, label=f"{n_lines}-line")
        for bar, val, left in zip(bars, values, lefts):
            if val > 4:
                ax.text(left + val / 2, bar.get_y() + bar.get_height() / 2,
                        f"{val:.1f}%", ha="center", va="center",
                        fontsize=9, color="white", fontweight="bold")
        lefts += np.array(values)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(modes, fontsize=12)
    ax.set_xlabel("Percentage of clears (%)", fontsize=12)
    ax.set_title("Clear Type Distribution at 300k Checkpoint", fontsize=14)
    ax.set_xlim(0, 100)
    # Place legend outside the chart to the right so it never overlaps bars
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0, fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout(rect=[0, 0, 0.88, 1])  # leave room on right for legend
    path = os.path.join(output_dir, "chart_clear_distribution.pdf")
    fig.savefig(path)
    print(f"Saved {path}")


def main():
    opt = get_args()
    os.makedirs(opt.output_dir, exist_ok=True)
    results = load_results(opt.csv)
    plot_lines_cleared(results, opt.output_dir)
    plot_blocks_placed(results, opt.output_dir)
    plot_clear_distribution(results, opt.output_dir)
    print("Done.")


if __name__ == "__main__":
    main()