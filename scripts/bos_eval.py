"""Evaluate Battle of the Sexes trace."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows, summary = [], {}
    for line in args.trace.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip().startswith("{"):
            continue
        obj = json.loads(line)
        if obj.get("event") == "round_action":
            rows.append(obj["data"])
        elif obj.get("event") == "run_summary":
            summary = obj["data"]

    df = pd.DataFrame(rows)
    df["cum_coord"] = df["coordinated"].astype(int).expanding().mean()
    df.to_csv(args.out_dir / "round_actions.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["round"], df["cum_coord"], label="Coordination rate")
    if summary.get("paper_baseline_coord_rate"):
        ax.axhline(summary["paper_baseline_coord_rate"], color="r", linestyle="--", label="Paper baseline (approx)")
    ax.set_xlabel("Round")
    ax.set_ylabel("Coordination rate")
    ax.set_title("Battle of the Sexes — Akata et al. 2023")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(args.out_dir / "coordination_rate.png", dpi=150)
    plt.close(fig)

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
