"""Aggregate benchmark results into Feishu-friendly markdown + CSV."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAPER_BASELINES = {
    # Akata IPD — cooperation rate (Option J)
    "ipd_vs_tft": ("Agent合作率(J)", 0.70, "GPT-4 vs TFT，Figure 3"),
    "ipd_vs_ac": ("Agent合作率(J)", 0.85, "GPT-4 vs Always-J，高合作"),
    "ipd_vs_ad": ("Agent合作率(J)", 0.15, "GPT-4 vs Always-F，低合作(~85%背叛)"),
    "ipd_vs_llm": ("Agent合作率(J)", 0.55, "GPT-4 vs GPT-4"),
    "ipd_vs_defect_once": ("Agent合作率(J)", 0.10, "GPT-4 vs 背叛一次后合作，极不 forgiving"),
    "ipd_vs_tft_scot": ("Agent合作率(J)", 0.70, "SCoT vs TFT，与 base 相近"),
    # Akata BoS — coordination rate
    "bos_llm": ("协调率", 0.55, "GPT-4 互玩，非对称收益"),
    "bos_llm_scot": ("协调率", 0.70, "SCoT 互玩，协调提升"),
    "bos_vs_ac": ("协调率", 0.90, "vs Always-J，易协调"),
    "bos_vs_alternate": ("协调率", 0.30, "vs 交替策略，GPT-4 难协调"),
    # Horton Dictator
    "dictator_100": ("给出比例", 0.15, "GPT-3 给出约15% endowment"),
    # CompeteAI
    "competeai_2x3x4": ("Matthew效应", None, "领先餐厅份额扩大；mini 配置"),
    "competeai_2x5x6": ("Matthew效应", None, "同上"),
    "competeai_2x5x6_s99": ("Matthew效应", None, "同上"),
}


def metric_from_summary(name: str, summary: dict) -> tuple[str, float | str | None]:
    mean = summary.get("mean")
    std = summary.get("std")
    n = summary.get("n_seeds")

    def fmt_val(v: float, label: str) -> tuple[str, float]:
        if mean is not None and n:
            s = std if std is not None else 0.0
            return f"{mean:.1%} ± {s:.1%} (n={n})", float(mean)
        return f"{v:.1%}", float(v)

    if name.startswith("ipd"):
        v = summary.get("agent_cooperation_rate")
        extra = summary.get("mutual_cooperation_rate")
        mode = summary.get("prompt_mode", "")
        if v is not None:
            s, val = fmt_val(v, "coop")
            tag = f" [{mode}]" if mode else ""
            extra_s = f" (互合作{extra:.1%})" if extra is not None else ""
            return s + extra_s + tag, val
    if name.startswith("bos"):
        v = summary.get("coordination_rate")
        mode = summary.get("prompt_mode", "")
        if v is not None:
            s, val = fmt_val(v, "coord")
            return s + (f" [{mode}]" if mode else ""), val
    if name.startswith("dictator"):
        v = summary.get("offer_pct")
        if v is not None:
            s, val = fmt_val(v, "offer")
            return s + f" (${summary.get('offer', v * 100):.0f}/100)", val
    if name.startswith("competeai"):
        if summary.get("leader_market_share_mean") is not None:
            v = summary["leader_market_share_mean"]
            s, val = fmt_val(v, "share")
            return f"领先份额 {s}", val
        shares = summary.get("final_market_shares") or {}
        if shares:
            parts = [f"R{k}:{v:.0%}" for k, v in sorted(shares.items(), key=lambda x: x[0])]
            max_share = max(shares.values()) if shares else 0
            return " / ".join(parts), max_share
    return "—", None


def repro_status(name: str, ours: float | None, baseline: float | None) -> str:
    if baseline is None:
        return "Pipeline验证"
    if ours is None:
        return "未出数"
    delta = abs(ours - baseline)
    if delta <= 0.15:
        return "✅ 部分复现"
    if delta <= 0.30:
        return "⚠️ 趋势接近"
    return "❌ 未复现"


def collect(root: Path) -> list[dict]:
    rows = []
    for meta_path in sorted(root.rglob("run_meta.json")):
        if "seeds" in meta_path.parts:
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if meta.get("status") not in ("ok", "partial"):
            continue
        name = meta["name"]
        summary = meta.get("summary", {})
        metric_label, paper_base, paper_note = PAPER_BASELINES.get(name, ("—", None, ""))
        ours_str, ours_val = metric_from_summary(name, summary)
        base_str = f"{paper_base:.0%}" if paper_base is not None else "定性"
        delta = ours_val - paper_base if (ours_val is not None and paper_base is not None) else None
        rows.append({
            "论文": meta.get("paper", ""),
            "arXiv": meta.get("paper_id", ""),
            "实验ID": name,
            "模型": meta.get("model", ""),
            "重复次数": summary.get("n_seeds", 1),
            "指标": metric_label.split("(")[0].strip(),
            "我们的结果(mean±std)": ours_str,
            "论文基线": base_str,
            "差值(mean)": f"{delta:+.1%}" if delta is not None else "—",
            "复现判定": repro_status(name, ours_val, paper_base),
            "论文说明": paper_note,
            "结果路径": meta.get("out_dir", str(meta_path.parent.relative_to(ROOT))),
        })
    return rows


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="eval_results/benchmark_repro")
    ap.add_argument("--out_md", default="docs/feishu_benchmark_results.md")
    ap.add_argument("--out_csv", default="docs/feishu_benchmark_results.csv")
    args = ap.parse_args()

    root = ROOT / args.input
    rows = collect(root)
    if not rows:
        for alt in ["eval_results/benchmark_full", "eval_results/benchmark_suite"]:
            if (ROOT / alt).exists():
                rows.extend(collect(ROOT / alt))

    out_md = ROOT / args.out_md
    out_csv = ROOT / args.out_csv
    out_md.parent.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys()) if rows else []
    with out_csv.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    lines = [
        "# Benchmark 跑批结果汇总（飞书粘贴版）",
        "",
        f"> 数据源：`{args.input}` | 含 mean±std 时请确认使用了 `--seeds` 多局平均",
        "",
        "## 总表",
        "",
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join(["---"] * len(fields)) + " |",
    ]
    for r in rows:
        lines.append("| " + " | ".join(str(r[k]) for k in fields) + " |")

    lines += ["", "## 按论文分组结论", ""]
    papers: dict[str, list] = {}
    for r in rows:
        papers.setdefault(r["论文"], []).append(r)
    for paper, pr in papers.items():
        ok = sum(1 for x in pr if "✅" in x["复现判定"])
        partial = sum(1 for x in pr if "⚠️" in x["复现判定"])
        lines.append(f"### {paper}")
        lines.append(f"- 实验数 {len(pr)}，✅部分复现 {ok}，⚠️趋势接近 {partial}")
        for x in pr:
            lines.append(f"  - `{x['实验ID']}` ({x['模型']}): {x['我们的结果(mean±std)']} vs 论文{x['论文基线']} → {x['复现判定']}")
        lines.append("")

    lines += [
        "",
        "## 结果文件位置",
        "",
        f"- **原始跑批目录**：`{args.input}/`（每个实验含 trace.jsonl、summary.json、图表）",
        "- **飞书 CSV**：`docs/feishu_benchmark_results.csv`",
        "- **飞书 Markdown**：`docs/feishu_benchmark_results.md`",
        "",
        "## 飞书导入",
        "",
        "1. 飞书文档 → 插入 → 表格 → 导入 CSV → 选 `docs/feishu_benchmark_results.csv`",
        "2. 或将上方总表复制粘贴",
        "",
    ]
    out_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_csv} ({len(rows)} rows)")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()
