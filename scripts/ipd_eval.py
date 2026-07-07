"""Evaluate IPD trace vs paper baselines."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_trace(path: Path) -> tuple[pd.DataFrame, dict]:
    rounds, summary = [], {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        obj = json.loads(line)
        ev, data = obj.get("event"), obj.get("data", {})
        if ev == "round_action":
            rounds.append(data)
        elif ev == "run_summary":
            summary = data
    return pd.DataFrame(rounds), summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    df, summary = load_trace(args.trace)
    if df.empty:
        raise ValueError("No round_action events")

    if "agent_cooperated" in df.columns:
        df["agent_cooperated"] = df["agent_cooperated"].astype(int)
    else:
        df["agent_cooperated"] = df["agent_action"].isin(["C", "J"]).astype(int)
    df["mutual_coop"] = (
        df["agent_action"].isin(["C", "J"]) & df["opponent_action"].isin(["C", "J"])
    ).astype(int)
    df["cum_coop_rate"] = df["agent_cooperated"].expanding().mean()
    df.to_csv(args.out_dir / "round_actions.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["round"], df["cum_coop_rate"], label="Agent cooperation (cumulative)")
    if summary.get("paper_baseline_coop_rate") is not None:
        ax.axhline(summary["paper_baseline_coop_rate"], color="r", linestyle="--", label="Paper GPT-4 baseline (approx)")
    ax.set_xlabel("Round")
    ax.set_ylabel("Cooperation rate")
    ax.set_title(f"IPD vs {summary.get('opponent', '?')} — Akata et al. 2023")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(args.out_dir / "cooperation_rate.png", dpi=150)
    plt.close(fig)

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
