# Benchmark 复现跑批说明

## 结果在哪

| 内容 | 路径 |
|------|------|
| **全部原始结果** | `eval_results/benchmark_repro/` |
| **汇总 JSON** | `eval_results/benchmark_repro/suite_report.json` |
| **飞书 CSV（导入用）** | `docs/feishu_benchmark_repro.csv` |
| **飞书 Markdown** | `docs/feishu_benchmark_repro.md` |
| **旧版跑批（对比）** | `eval_results/benchmark_full/` |

目录结构：`eval_results/benchmark_repro/{模型}/{实验ID}/`

每个实验含：`trace.jsonl`、`summary.json`、`run_meta.json`、评估图表。

## 本次论文与实验（4 篇，28 组）

| 论文 | arXiv | 实验数 | 协议要点 |
|------|-------|--------|----------|
| Akata 重复博弈 IPD | 2305.16867 | 6×2 | 官方 J/F、10 轮、temperature=0 |
| Akata Battle of the Sexes | 2305.16867 | 4×2 | 非对称收益 + SCoT |
| Horton Dictator Game | 2301.07640 | 1×2 | 单次分配 $100 |
| CompeteAI mini | 2310.17512 | 3×2 | 2 餐厅竞争（pipeline 验证） |

## 复现亮点（GPT-4o）

- **BoS + SCoT 互玩**：协调率 **70%**，与论文 SCoT 基线 **70%** 一致 → ✅ 部分复现
- **BoS vs Always-J**：100% vs 90% → ✅
- **BoS vs 交替对手**：50% vs 30% → ⚠️ 趋势接近（比论文略高）
- **IPD**：OpenRouter GPT-4o 在官方协议下**全程背叛 (F)**，与论文 GPT-4「高合作」相反，但 **vs Always-Defect** 的 0% 合作与论文 ~15% 接近 → 行为签名不同，模型/接口差异

## 一键重跑

```powershell
$env:HTTP_PROXY="socks5://127.0.0.1:10808"
$env:HTTPS_PROXY="socks5://127.0.0.1:10808"
.\.venv312\Scripts\python.exe scripts\run_simple_benchmarks.py --out_dir eval_results/benchmark_repro
.\.venv312\Scripts\python.exe scripts\build_feishu_table.py --input eval_results/benchmark_repro --out_csv docs/feishu_benchmark_repro.csv --out_md docs/feishu_benchmark_repro.md
```

## 飞书导入

1. 关闭 IDE 中打开的 CSV（若占用）
2. 飞书 → 插入 → 表格 → 导入 → `docs/feishu_benchmark_repro.csv`
3. 复制 `docs/feishu_benchmark_repro.md` 中的分组结论
