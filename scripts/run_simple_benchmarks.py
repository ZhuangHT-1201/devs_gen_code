"""Run paper-reproduction benchmark suite."""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = ROOT / ".venv312" / "Scripts" / "python.exe"

DEFAULT_SEEDS = [1, 7, 13, 42, 77, 99, 123, 256, 314, 999]

EXPERIMENTS = [
    # --- Akata 2023 IPD (official 10-round protocol) ---
    {"name": "ipd_vs_ac", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "ac"], "eval": "scripts/ipd_eval.py"},
    {"name": "ipd_vs_ad", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "ad"], "eval": "scripts/ipd_eval.py"},
    {"name": "ipd_vs_tft", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "tft"], "eval": "scripts/ipd_eval.py"},
    {"name": "ipd_vs_llm", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "llm"], "eval": "scripts/ipd_eval.py"},
    {"name": "ipd_vs_defect_once", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "defect_once"], "eval": "scripts/ipd_eval.py"},
    {"name": "ipd_vs_tft_scot", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "ipd.generated_simulation.run_ipd", "args": ["--rounds", "10", "--opponent", "tft", "--scot"], "eval": "scripts/ipd_eval.py"},
    # --- Akata 2023 BoS ---
    {"name": "bos_llm", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "bos.generated_simulation.run_bos", "args": ["--rounds", "10", "--opponent", "llm"], "eval": "scripts/bos_eval.py"},
    {"name": "bos_llm_scot", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "bos.generated_simulation.run_bos", "args": ["--rounds", "10", "--opponent", "llm", "--scot"], "eval": "scripts/bos_eval.py"},
    {"name": "bos_vs_ac", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "bos.generated_simulation.run_bos", "args": ["--rounds", "10", "--opponent", "ac"], "eval": "scripts/bos_eval.py"},
    {"name": "bos_vs_alternate", "paper": "Playing Repeated Games with LLMs (Akata 2023)", "paper_id": "2305.16867",
     "module": "bos.generated_simulation.run_bos", "args": ["--rounds", "10", "--opponent", "alternate"], "eval": "scripts/bos_eval.py"},
    # --- Horton 2023 Dictator Game ---
    {"name": "dictator_100", "paper": "LLMs as Simulated Economic Agents (Horton 2023)", "paper_id": "2301.07640",
     "module": "dictator.generated_simulation.run_dictator", "args": ["--endowment", "100"], "eval": "scripts/dictator_eval.py"},
    # --- CompeteAI mini ---
    {"name": "competeai_2x3x4", "paper": "CompeteAI (Zhao ICML 2024)", "paper_id": "2310.17512",
     "module": "competeai.generated_simulation.run_competeai_mini",
     "args": ["--num_restaurants", "2", "--num_customers", "3", "--num_rounds", "4", "--seed", "42"], "eval": "scripts/competeai_eval.py"},
    {"name": "competeai_2x5x6", "paper": "CompeteAI (Zhao ICML 2024)", "paper_id": "2310.17512",
     "module": "competeai.generated_simulation.run_competeai_mini",
     "args": ["--num_restaurants", "2", "--num_customers", "5", "--num_rounds", "6", "--seed", "42"], "eval": "scripts/competeai_eval.py"},
    {"name": "competeai_2x5x6_s99", "paper": "CompeteAI (Zhao ICML 2024)", "paper_id": "2310.17512",
     "module": "competeai.generated_simulation.run_competeai_mini",
     "args": ["--num_restaurants", "2", "--num_customers", "5", "--num_rounds", "6", "--seed", "99"], "eval": "scripts/competeai_eval.py"},
]


def model_slug(model: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", model.replace("/", "_"))


def with_seed_args(exp: dict, seed: int) -> list[str]:
    args = list(exp["args"])
    if "--seed" in args:
        i = args.index("--seed")
        args[i + 1] = str(seed)
    else:
        args.extend(["--seed", str(seed)])
    return args


def extract_scalar_metric(name: str, summary: dict) -> float | None:
    if name.startswith("ipd"):
        return summary.get("agent_cooperation_rate")
    if name.startswith("bos"):
        return summary.get("coordination_rate")
    if name.startswith("dictator"):
        return summary.get("offer_pct")
    if name.startswith("competeai"):
        shares = summary.get("final_market_shares") or {}
        return max(shares.values()) if shares else None
    return None


def run_one(exp: dict, model: str, out_dir: Path, *, seed: int | None = None, skip_existing: bool = False) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    trace = out_dir / "trace.jsonl"
    summary_path = out_dir / "summary.json"

    if skip_existing and summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        metric = extract_scalar_metric(exp["name"], summary)
        return {
            "model": model,
            "name": exp["name"],
            "paper": exp["paper"],
            "paper_id": exp.get("paper_id", ""),
            "seed": seed,
            "status": "ok",
            "summary": summary,
            "metric": metric,
            "out_dir": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
            "skipped": True,
        }

    args = with_seed_args(exp, seed) if seed is not None else list(exp["args"])
    cmd = [str(PY), "-m", exp["module"], *args, "--api_model", model]
    label = f"[{model}] {exp['name']}" + (f" seed={seed}" if seed is not None else "")
    print(f"\n=== {label} ===", file=sys.stderr)
    env = os.environ.copy()
    with trace.open("w", encoding="utf-8") as f_out, (out_dir / "run.log").open("w", encoding="utf-8") as f_err:
        p = subprocess.run(cmd, cwd=ROOT, stdout=f_out, stderr=f_err, env=env)
    if p.returncode != 0:
        return {
            "model": model,
            "name": exp["name"],
            "paper": exp["paper"],
            "seed": seed,
            "status": "sim_failed",
            "returncode": p.returncode,
        }

    eval_cmd = [str(PY), str(ROOT / exp["eval"]), "--trace", str(trace), "--out_dir", str(out_dir)]
    subprocess.run(eval_cmd, cwd=ROOT, check=False, env=env)

    summary_path = out_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    if not summary and (out_dir / "round_metrics.csv").exists():
        import pandas as pd
        df = pd.read_csv(out_dir / "round_metrics.csv")
        last = df.groupby("restaurant_id").last()
        summary = {
            "final_market_shares": last["market_share"].to_dict(),
            "final_revenues": last["revenue"].to_dict(),
            "rounds": int(df["round"].max()),
        }

    metric = extract_scalar_metric(exp["name"], summary)
    return {
        "model": model,
        "name": exp["name"],
        "paper": exp["paper"],
        "paper_id": exp.get("paper_id", ""),
        "seed": seed,
        "status": "ok",
        "summary": summary,
        "metric": metric,
        "out_dir": str(out_dir.relative_to(ROOT)).replace("\\", "/"),
    }


def aggregate_runs(
    exp: dict,
    model: str,
    out_root: Path,
    seeds: list[int],
    *,
    skip_existing: bool = False,
    skip_if_aggregate: bool = False,
) -> dict:
    exp_dir = out_root / model_slug(model) / exp["name"]
    agg_path = exp_dir / "aggregate.json"
    if skip_if_aggregate and agg_path.exists():
        meta = json.loads(agg_path.read_text(encoding="utf-8"))
        print(f"  -> skip (aggregate exists) mean={meta.get('summary', {}).get('mean')}", file=sys.stderr)
        return meta

    seed_root = exp_dir / "seeds"
    values: list[float] = []
    per_seed: list[dict] = []

    for seed in seeds:
        seed_dir = seed_root / f"seed_{seed}"
        run = run_one(exp, model, seed_dir, seed=seed, skip_existing=skip_existing)
        per_seed.append({"seed": seed, "metric": run.get("metric"), "status": run.get("status"), "skipped": run.get("skipped")})
        if run.get("status") == "ok" and run.get("metric") is not None:
            values.append(float(run["metric"]))

    mean = statistics.mean(values) if values else None
    std = statistics.stdev(values) if len(values) > 1 else (0.0 if values else None)
    base_summary_path = seed_root / f"seed_{seeds[-1]}" / "summary.json"
    summary: dict = {}
    if base_summary_path.exists():
        summary = json.loads(base_summary_path.read_text(encoding="utf-8"))

    if exp["name"].startswith("ipd"):
        summary["agent_cooperation_rate"] = mean
        summary["mutual_cooperation_rate"] = None
    elif exp["name"].startswith("bos"):
        summary["coordination_rate"] = mean
    elif exp["name"].startswith("dictator"):
        summary["offer_pct"] = mean
        summary["offer"] = (mean or 0) * 100
    elif exp["name"].startswith("competeai") and values:
        summary["leader_market_share_mean"] = mean

    summary.update({
        "n_seeds": len(seeds),
        "seeds": seeds,
        "mean": mean,
        "std": std,
        "per_seed_metrics": values,
        "per_seed": per_seed,
    })

    meta = {
        "model": model,
        "name": exp["name"],
        "paper": exp["paper"],
        "paper_id": exp.get("paper_id", ""),
        "status": "ok" if values else "partial",
        "aggregated": True,
        "summary": summary,
        "out_dir": str(exp_dir.relative_to(ROOT)).replace("\\", "/"),
    }
    exp_dir.mkdir(parents=True, exist_ok=True)
    (exp_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    (exp_dir / "aggregate.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> mean={mean:.1%} std={std:.1%} n={len(values)}" if mean is not None else "  -> no metrics", file=sys.stderr)
    return meta


def run_single(exp: dict, model: str, out_root: Path) -> dict:
    out_dir = out_root / model_slug(model) / exp["name"]
    run = run_one(exp, model, out_dir)
    meta = {k: v for k, v in run.items() if k != "metric"}
    meta["out_dir"] = str(out_dir.relative_to(ROOT)).replace("\\", "/")
    if run.get("status") == "ok":
        (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["openai/gpt-4o", "deepseek/deepseek-chat"])
    ap.add_argument("--out_dir", default="eval_results/benchmark_repro")
    ap.add_argument("--only", nargs="*", help="subset of experiment names")
    ap.add_argument("--seeds", nargs="+", type=int, help="repeat each experiment with these seeds and aggregate mean±std")
    ap.add_argument("--skip_existing", action="store_true", help="reuse seed dir if summary.json exists")
    ap.add_argument("--skip_if_aggregate", action="store_true", help="skip experiment when aggregate.json exists")
    args = ap.parse_args()

    out_root = ROOT / args.out_dir
    out_root.mkdir(parents=True, exist_ok=True)

    exps = EXPERIMENTS
    if args.only:
        exps = [e for e in EXPERIMENTS if e["name"] in args.only]

    results = []
    seeds = args.seeds
    for model in args.models:
        for exp in exps:
            if seeds:
                results.append(
                    aggregate_runs(
                        exp,
                        model,
                        out_root,
                        seeds,
                        skip_existing=args.skip_existing,
                        skip_if_aggregate=args.skip_if_aggregate,
                    )
                )
            else:
                results.append(run_single(exp, model, out_root))

    report = out_root / "suite_report.json"
    report.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
