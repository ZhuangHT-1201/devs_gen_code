"""Evaluate CompeteAI DEVS trace: market share & revenue dynamics."""

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _read_text_auto_encoding(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("utf-16")


def load_round_snapshots(trace_path: Path) -> pd.DataFrame:
    rows = []
    text = _read_text_auto_encoding(trace_path)
    for line in text.splitlines():
        line = line.strip()
        if not line or not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("event") != "round_snapshot":
            continue
        data = obj.get("data", obj)
        round_num = int(data.get("round", 0))
        shares = data.get("market_shares", {})
        revenues = data.get("revenues", {})
        reps = data.get("reputations", {})
        for rid, share in shares.items():
            rows.append(
                {
                    "round": round_num,
                    "restaurant_id": str(rid),
                    "market_share": float(share),
                    "revenue": float(revenues.get(str(rid), revenues.get(rid, 0.0))),
                    "reputation": float(reps.get(str(rid), reps.get(rid, 0.0))),
                    "total_visits": int(data.get("total_visits", 0)),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No round_snapshot events found in trace.")
    return df.sort_values(["round", "restaurant_id"]).reset_index(drop=True)


def plot_results(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4))
    for rid, g in df.groupby("restaurant_id"):
        ax.plot(g["round"], g["market_share"], marker="o", label=f"Restaurant {rid}")
    ax.set_xlabel("Round")
    ax.set_ylabel("Market Share")
    ax.set_title("CompeteAI Mini — Market Share over Rounds")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "market_share_timeseries.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    for rid, g in df.groupby("restaurant_id"):
        ax.plot(g["round"], g["revenue"], marker="s", label=f"Restaurant {rid}")
    ax.set_xlabel("Round")
    ax.set_ylabel("Cumulative Revenue")
    ax.set_title("CompeteAI Mini — Revenue over Rounds")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_dir / "revenue_timeseries.png", dpi=150)
    plt.close(fig)

    df.to_csv(out_dir / "round_metrics.csv", index=False)

    summary = {
        "final_market_shares": df.groupby("restaurant_id")["market_share"].last().to_dict(),
        "final_revenues": df.groupby("restaurant_id")["revenue"].last().to_dict(),
        "rounds": int(df["round"].max()),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate CompeteAI DEVS trace")
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--out_dir", type=Path, required=True)
    args = parser.parse_args()

    df = load_round_snapshots(args.trace)
    plot_results(df, args.out_dir)
    print(f"Wrote eval outputs to {args.out_dir}")
    print(df.groupby("restaurant_id")[["market_share", "revenue", "reputation"]].last())


if __name__ == "__main__":
    main()
