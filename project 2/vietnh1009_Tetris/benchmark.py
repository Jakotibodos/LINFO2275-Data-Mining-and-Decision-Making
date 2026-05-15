"""
Benchmark script: evaluates each reward-mode model across training checkpoints.
Plays N games in parallel per checkpoint, records scores, saves charts and CSV.

Usage:
    python benchmark.py
    python benchmark.py --games 10 --saved_path trained_models --output_dir benchmark_results
    python benchmark.py --workers 8
"""

import argparse
import os
import numpy as np
import torch
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
import multiprocessing as mp
from src.tetris import Tetris


REWARD_MODES = ["nn_heuristic_model","cnn_model"]
CHECKPOINTS  = [50000, 100000, 150000, 200000, 250000, 300000]

COLORS = {
    "nn_heuristic_model":  "#2196F3",
    "cnn_model":   "#FF9800"
}


def get_args():
    parser = argparse.ArgumentParser(description="Benchmark trained Tetris DQN models")
    parser.add_argument("--width",      type=int, default=10)
    parser.add_argument("--height",     type=int, default=20)
    parser.add_argument("--block_size", type=int, default=30)
    parser.add_argument("--games",      type=int, default=10,
                        help="Number of games to play per checkpoint")
    parser.add_argument("--max_steps",  type=int, default=100000,
                        help="Max piece placements per game before forced termination")
    parser.add_argument("--workers",    type=int, default=max(1, mp.cpu_count() - 1),
                        help="Number of parallel worker processes (default: CPU count - 1)")
    parser.add_argument("--saved_path", type=str, default="trained_models")
    parser.add_argument("--output_dir", type=str, default="benchmark_results")
    return parser.parse_args()


def load_model(saved_path, model_name):
    path = os.path.join(saved_path, model_name)
    if not os.path.exists(path):
        return None
    model = torch.load(path, weights_only=False, map_location=torch.device("cpu"))
    model.eval()
    return model


def _play_single_game(args):
    """Worker: reconstructs model from state_dict, plays one game, returns stats dict."""
    state_dict, model_class, width, height, block_size, max_steps, reward_scheme, is_cnn = args
    model = model_class()
    model.load_state_dict(state_dict)
    model.eval()

    env = Tetris(width=width, height=height, block_size=block_size,
                 use_cnn=is_cnn, reward_mode=reward_scheme)
    env.reset()
    steps = 0
    while True:
        next_steps = env.get_next_states()
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        with torch.no_grad():
            predictions = model(next_states)[:, 0]
        index = torch.argmax(predictions).item()
        action = next_actions[index]
        _, done = env.step(action, render=False)
        steps += 1
        if done or steps >= max_steps:
            return {
                "cleared_lines":              env.cleared_lines,
                "tetrominoes":                env.tetrominoes,
                "cleared_lines_distribution": dict(env.cleared_lines_distribution),
            }


def play_games(model, model_class, num_games, width, height, block_size,
               max_steps, num_workers, desc="", reward_scheme="regular_reward", is_cnn=False):
    state_dict = model.state_dict()
    task_args = [
        (state_dict, model_class, width, height, block_size, max_steps, reward_scheme, is_cnn)
        for _ in range(num_games)
    ]

    results = []
    with mp.Pool(processes=num_workers) as pool:
        with tqdm(total=num_games, desc=desc, unit="game", ncols=80) as pbar:
            for result in pool.imap_unordered(_play_single_game, task_args, chunksize=5):
                results.append(result)
                pbar.update(1)
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
    ax.legend(fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    path = os.path.join(output_dir, "chart_lines_cleared.png")
    fig.savefig(path, dpi=150)
    print(f"Chart saved to {path}")
    return fig


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
    ax.legend(fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    path = os.path.join(output_dir, "chart_blocks_placed.png")
    fig.savefig(path, dpi=150)
    print(f"Chart saved to {path}")
    return fig


def plot_clear_distribution(results, output_dir):
    """
    Stacked horizontal bar chart showing the % breakdown of 1/2/3/4-line
    clears for each reward mode's 300k checkpoint.
    """
    clear_labels = [1, 2, 3, 4]
    clear_colors = ["#90CAF9", "#42A5F5", "#1565C0", "#0D47A1"]  # light → dark blue

    # Aggregate distribution across all games for the 300k checkpoint
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
        return None

    modes = list(mode_pcts.keys())
    fig, ax = plt.subplots(figsize=(10, 3 + len(modes)))

    bar_height = 0.5
    y_positions = np.arange(len(modes))

    lefts = np.zeros(len(modes))
    for i, (n_lines, color) in enumerate(zip(clear_labels, clear_colors)):
        values = [mode_pcts[m][i] for m in modes]
        bars = ax.barh(y_positions, values, left=lefts, height=bar_height,
                       color=color, label=f"{n_lines}-line")
        # Annotate each segment if wide enough
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
    ax.legend(loc="lower right", fontsize=10)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    fig.tight_layout()
    path = os.path.join(output_dir, "chart_clear_distribution.png")
    fig.savefig(path, dpi=150)
    print(f"Chart saved to {path}")
    return fig


def main():
    mp.set_start_method("spawn", force=True)

    opt = get_args()
    os.makedirs(opt.output_dir, exist_ok=True)

    print(f"Workers={opt.workers}  |  games={opt.games}  |  max_steps={opt.max_steps}\n")

    from src.deep_q_network import DeepQNetwork
    from src.cnn_q_network import CnnQNetwork
    

    # ------------------------------------------------------------------ #
    # Collect results                                                       #
    # ------------------------------------------------------------------ #
    # results[mode][checkpoint] = {mean_lines, std_lines, mean_tetrominoes,
    #                               std_tetrominoes, clear_distribution, ...}
    results = {mode: {} for mode in REWARD_MODES}
    rows = []

    for mode in REWARD_MODES:
        for ckpt in CHECKPOINTS:
            model_class = CnnQNetwork if mode=="cnn_model" else DeepQNetwork
            model_name = f"{mode}_{ckpt}"
            print(f"Loading {model_name} ...", end=" ", flush=True)
            model = load_model(opt.saved_path, model_name)
            if model is None:
                print("NOT FOUND — skipping")
                continue
            print("OK")
            print(mode=="cnn_model")
            game_results = play_games(
                model, model_class,
                num_games=opt.games,
                width=opt.width, height=opt.height, block_size=opt.block_size,
                max_steps=opt.max_steps,
                num_workers=opt.workers,
                desc=f"{mode} @ {ckpt//1000}k",
                reward_scheme=mode,
                is_cnn = mode=="cnn_model"
            )

            lines      = [g["cleared_lines"] for g in game_results]
            tetrominoes = [g["tetrominoes"]   for g in game_results]

            # Aggregate clear distribution across all games
            agg_dist = {1: 0, 2: 0, 3: 0, 4: 0}
            for g in game_results:
                for k, v in g["cleared_lines_distribution"].items():
                    agg_dist[k] += v

            mean_l, std_l = float(np.mean(lines)),       float(np.std(lines))
            mean_t, std_t = float(np.mean(tetrominoes)), float(np.std(tetrominoes))

            results[mode][ckpt] = {
                "mean_lines":        mean_l,
                "std_lines":         std_l,
                "mean_tetrominoes":  mean_t,
                "std_tetrominoes":   std_t,
                "clear_distribution": agg_dist,
            }
            print(f"  → lines: mean={mean_l:.1f} std={std_l:.1f} "
                  f"| blocks: mean={mean_t:.1f} std={std_t:.1f}")

            rows.append({
                "reward_mode":       mode,
                "checkpoint":        ckpt,
                "mean_lines":        mean_l,
                "std_lines":         std_l,
                "min_lines":         int(np.min(lines)),
                "max_lines":         int(np.max(lines)),
                "median_lines":      float(np.median(lines)),
                "mean_tetrominoes":  mean_t,
                "std_tetrominoes":   std_t,
                "clears_1":          agg_dist[1],
                "clears_2":          agg_dist[2],
                "clears_3":          agg_dist[3],
                "clears_4":          agg_dist[4],
            })

    # ------------------------------------------------------------------ #
    # CSV                                                                   #
    # ------------------------------------------------------------------ #
    csv_path = os.path.join(opt.output_dir, "benchmark_results.csv")
    df = pd.DataFrame(rows)
    df.sort_values(["reward_mode", "checkpoint"], inplace=True)
    df.to_csv(csv_path, index=False)
    print(f"\nCSV saved to {csv_path}")

    # ------------------------------------------------------------------ #
    # Charts                                                                #
    # ------------------------------------------------------------------ #
    plot_lines_cleared(results, opt.output_dir)
    plot_blocks_placed(results, opt.output_dir)
    plot_clear_distribution(results, opt.output_dir)
    plt.show()


if __name__ == "__main__":
    main()