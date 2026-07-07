"""Evaluate Dictator Game trace."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--out_dir", type=Path, required=True)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    summary = {}
    for line in args.trace.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip().startswith("{"):
            continue
        obj = json.loads(line)
        if obj.get("event") == "run_summary":
            summary = obj["data"]

    fig, ax = plt.subplots(figsize=(5, 4))
    ours = summary.get("offer_pct", 0)
    base = summary.get("paper_baseline_offer_pct", 0.15)
    ax.bar(["Our model", "Paper GPT-3 ref"], [ours, base], color=["steelblue", "coral"])
    ax.set_ylabel("Offer fraction of endowment")
    ax.set_title("Dictator Game — Horton 2023")
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(args.out_dir / "offer_comparison.png", dpi=150)
    plt.close(fig)

    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
