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


def load_trace(trace_path: Path) -> pd.DataFrame:
    rows = []
    text = _read_text_auto_encoding(trace_path)
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        data = obj.get("data", {})
        event = obj.get("event")

        # Format A (spec): event == macro_snapshot and fields in `data`
        if event == "macro_snapshot":
            month_val = data.get("month", obj.get("month", 0))
            year_val = data.get("year", obj.get("year", 0))
            price_val = data.get("price", obj.get("price"))
            unemp_val = data.get("unemployment", obj.get("unemployment"))
            wage_val = data.get("avg_wage", obj.get("avg_wage"))
            rows.append(
                {
                    "time": float(obj.get("time", obj.get("_sim_time", 0.0))),
                    "event": event,
                    "month": int(month_val),
                    "year": int(year_val),
                    "price": price_val,
                    "unemployment": unemp_val,
                    "avg_wage": wage_val,
                }
            )
            continue

        # Format B (current generated trace): top-level monthly snapshot fields
        if all(k in obj for k in ("month", "year", "price", "unemployment", "avg_wage")):
            rows.append(
                {
                    "time": float(obj.get("time", obj.get("_sim_time", 0.0))),
                    "event": "macro_snapshot_compat",
                    "month": int(obj.get("month", 0)),
                    "year": int(obj.get("year", 0)),
                    "price": obj.get("price"),
                    "unemployment": obj.get("unemployment"),
                    "avg_wage": obj.get("avg_wage"),
                }
            )
    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError("No monthly macro snapshots found in trace.")
    # Keep the last snapshot for each (year, month) pair.
    if "year" in df.columns and not df["year"].isna().all():
        df = df.sort_values(["year", "month", "time"]).drop_duplicates(subset=["year", "month"], keep="last")
    else:
        df = df.sort_values(["month", "time"]).drop_duplicates(subset=["month"], keep="last")
    return df


def compute_annual_metrics(monthly_df: pd.DataFrame) -> pd.DataFrame:
    df = monthly_df.copy()
    if "year" not in df.columns or df["year"].isna().all() or (df["year"] == 0).all():
        df["year"] = ((df["month"] - 1) // 12 + 1).astype(int)

    annual = (
        df.groupby("year", as_index=False)
        .agg(
            avg_price=("price", "mean"),
            avg_unemployment=("unemployment", "mean"),
            avg_wage=("avg_wage", "mean"),
        )
        .sort_values("year")
    )

    annual["inflation_rate"] = annual["avg_price"].pct_change()
    annual["wage_inflation_rate"] = annual["avg_wage"].pct_change()
    return annual


def plot_results(annual: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(annual["year"], annual["inflation_rate"], label="Inflation Rate")
    ax1.plot(annual["year"], annual["avg_unemployment"], label="Unemployment Rate")
    ax1.set_title("Inflation and Unemployment Time Series")
    ax1.set_xlabel("Year")
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    fig1.tight_layout()
    fig1.savefig(out_dir / "inflation_unemployment_timeseries.png", dpi=180)
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(6, 6))
    ax2.scatter(
        annual["avg_unemployment"],
        annual["wage_inflation_rate"],
        alpha=0.8,
    )
    ax2.set_title("Phillips Curve Proxy")
    ax2.set_xlabel("Unemployment Rate")
    ax2.set_ylabel("Wage Inflation Rate")
    ax2.grid(True, alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(out_dir / "phillips_curve_scatter.png", dpi=180)
    plt.close(fig2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate EconAgent trace outputs.")
    parser.add_argument("--trace", type=Path, required=True, help="Path to JSONL trace file.")
    parser.add_argument(
        "--out_dir",
        type=Path,
        default=Path("eval_results/econagent"),
        help="Directory for csv and figures.",
    )
    args = parser.parse_args()

    monthly = load_trace(args.trace)
    annual = compute_annual_metrics(monthly)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(args.out_dir / "monthly_macro.csv", index=False)
    annual.to_csv(args.out_dir / "annual_metrics.csv", index=False)
    plot_results(annual, args.out_dir)

    print(f"Saved metrics and plots to: {args.out_dir}")


if __name__ == "__main__":
    main()
