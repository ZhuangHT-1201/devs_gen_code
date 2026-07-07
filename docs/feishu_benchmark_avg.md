# Benchmark 跑批结果汇总（飞书粘贴版）

> 数据源：`eval_results/benchmark_repro_avg` | 含 mean±std 时请确认使用了 `--seeds` 多局平均

## 总表

| 论文 | arXiv | 实验ID | 模型 | 重复次数 | 指标 | 我们的结果(mean±std) | 论文基线 | 差值(mean) | 复现判定 | 论文说明 | 结果路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm | deepseek/deepseek-chat | 3 | 协调率 | 100.0% ± 0.0% (n=3) [base] | 55% | +45.0% | ❌ 未复现 | GPT-4 互玩，非对称收益 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/bos_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm_scot | deepseek/deepseek-chat | 3 | 协调率 | 100.0% ± 0.0% (n=3) [scot] | 70% | +30.0% | ❌ 未复现 | SCoT 互玩，协调提升 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/bos_llm_scot |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_alternate | deepseek/deepseek-chat | 3 | 协调率 | 50.0% ± 0.0% (n=3) [base] | 30% | +20.0% | ⚠️ 趋势接近 | vs 交替策略，GPT-4 难协调 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/bos_vs_alternate |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6 | deepseek/deepseek-chat | 3 | Matthew效应 | 领先份额 93.3% ± 11.5% (n=3) | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/competeai_2x5x6 |
| LLMs as Simulated Economic Agents (Horton 2023) | 2301.07640 | dictator_100 | deepseek/deepseek-chat | 1 | 给出比例 | 50.0% ± 0.0% (n=1) ($50/100) | 15% | +35.0% | ❌ 未复现 | GPT-3 给出约15% endowment | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/dictator_100 |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ac | deepseek/deepseek-chat | 3 | Agent合作率 | 0.0% ± 0.0% (n=3) [base] | 85% | -85.0% | ❌ 未复现 | GPT-4 vs Always-J，高合作 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/ipd_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ad | deepseek/deepseek-chat | 3 | Agent合作率 | 0.0% ± 0.0% (n=3) [base] | 15% | -15.0% | ✅ 部分复现 | GPT-4 vs Always-F，低合作(~85%背叛) | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/ipd_vs_ad |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft | deepseek/deepseek-chat | 3 | Agent合作率 | 0.0% ± 0.0% (n=3) [base] | 70% | -70.0% | ❌ 未复现 | GPT-4 vs TFT，Figure 3 | eval_results/benchmark_repro_avg/deepseek_deepseek-chat/ipd_vs_tft |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm | openai/gpt-4o | 3 | 协调率 | 86.7% ± 5.8% (n=3) [base] | 55% | +31.7% | ❌ 未复现 | GPT-4 互玩，非对称收益 | eval_results/benchmark_repro_avg/openai_gpt-4o/bos_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm_scot | openai/gpt-4o | 3 | 协调率 | 76.7% ± 11.5% (n=3) [scot] | 70% | +6.7% | ✅ 部分复现 | SCoT 互玩，协调提升 | eval_results/benchmark_repro_avg/openai_gpt-4o/bos_llm_scot |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_alternate | openai/gpt-4o | 3 | 协调率 | 46.7% ± 5.8% (n=3) [base] | 30% | +16.7% | ⚠️ 趋势接近 | vs 交替策略，GPT-4 难协调 | eval_results/benchmark_repro_avg/openai_gpt-4o/bos_vs_alternate |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6 | openai/gpt-4o | 3 | Matthew效应 | 领先份额 73.3% ± 11.5% (n=3) | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_repro_avg/openai_gpt-4o/competeai_2x5x6 |
| LLMs as Simulated Economic Agents (Horton 2023) | 2301.07640 | dictator_100 | openai/gpt-4o | 1 | 给出比例 | 50.0% ± 0.0% (n=1) ($50/100) | 15% | +35.0% | ❌ 未复现 | GPT-3 给出约15% endowment | eval_results/benchmark_repro_avg/openai_gpt-4o/dictator_100 |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ac | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [base] | 85% | -85.0% | ❌ 未复现 | GPT-4 vs Always-J，高合作 | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ad | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [base] | 15% | -15.0% | ✅ 部分复现 | GPT-4 vs Always-F，低合作(~85%背叛) | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_ad |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_defect_once | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [base] | 10% | -10.0% | ✅ 部分复现 | GPT-4 vs 背叛一次后合作，极不 forgiving | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_defect_once |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_llm | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [base] | 55% | -55.0% | ❌ 未复现 | GPT-4 vs GPT-4 | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [base] | 70% | -70.0% | ❌ 未复现 | GPT-4 vs TFT，Figure 3 | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_tft |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft_scot | openai/gpt-4o | 10 | Agent合作率 | 0.0% ± 0.0% (n=10) [scot] | 70% | -70.0% | ❌ 未复现 | SCoT vs TFT，与 base 相近 | eval_results/benchmark_repro_avg/openai_gpt-4o/ipd_vs_tft_scot |

## 按论文分组结论

### Playing Repeated Games with LLMs (Akata 2023)
- 实验数 15，✅部分复现 4，⚠️趋势接近 2
  - `bos_llm` (deepseek/deepseek-chat): 100.0% ± 0.0% (n=3) [base] vs 论文55% → ❌ 未复现
  - `bos_llm_scot` (deepseek/deepseek-chat): 100.0% ± 0.0% (n=3) [scot] vs 论文70% → ❌ 未复现
  - `bos_vs_alternate` (deepseek/deepseek-chat): 50.0% ± 0.0% (n=3) [base] vs 论文30% → ⚠️ 趋势接近
  - `ipd_vs_ac` (deepseek/deepseek-chat): 0.0% ± 0.0% (n=3) [base] vs 论文85% → ❌ 未复现
  - `ipd_vs_ad` (deepseek/deepseek-chat): 0.0% ± 0.0% (n=3) [base] vs 论文15% → ✅ 部分复现
  - `ipd_vs_tft` (deepseek/deepseek-chat): 0.0% ± 0.0% (n=3) [base] vs 论文70% → ❌ 未复现
  - `bos_llm` (openai/gpt-4o): 86.7% ± 5.8% (n=3) [base] vs 论文55% → ❌ 未复现
  - `bos_llm_scot` (openai/gpt-4o): 76.7% ± 11.5% (n=3) [scot] vs 论文70% → ✅ 部分复现
  - `bos_vs_alternate` (openai/gpt-4o): 46.7% ± 5.8% (n=3) [base] vs 论文30% → ⚠️ 趋势接近
  - `ipd_vs_ac` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [base] vs 论文85% → ❌ 未复现
  - `ipd_vs_ad` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [base] vs 论文15% → ✅ 部分复现
  - `ipd_vs_defect_once` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [base] vs 论文10% → ✅ 部分复现
  - `ipd_vs_llm` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [base] vs 论文55% → ❌ 未复现
  - `ipd_vs_tft` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [base] vs 论文70% → ❌ 未复现
  - `ipd_vs_tft_scot` (openai/gpt-4o): 0.0% ± 0.0% (n=10) [scot] vs 论文70% → ❌ 未复现

### CompeteAI (Zhao ICML 2024)
- 实验数 2，✅部分复现 0，⚠️趋势接近 0
  - `competeai_2x5x6` (deepseek/deepseek-chat): 领先份额 93.3% ± 11.5% (n=3) vs 论文定性 → Pipeline验证
  - `competeai_2x5x6` (openai/gpt-4o): 领先份额 73.3% ± 11.5% (n=3) vs 论文定性 → Pipeline验证

### LLMs as Simulated Economic Agents (Horton 2023)
- 实验数 2，✅部分复现 0，⚠️趋势接近 0
  - `dictator_100` (deepseek/deepseek-chat): 50.0% ± 0.0% (n=1) ($50/100) vs 论文15% → ❌ 未复现
  - `dictator_100` (openai/gpt-4o): 50.0% ± 0.0% (n=1) ($50/100) vs 论文15% → ❌ 未复现


## 结果文件位置

- **原始跑批目录**：`eval_results/benchmark_repro_avg/`（每个实验含 trace.jsonl、summary.json、图表）
- **飞书 CSV**：`docs/feishu_benchmark_results.csv`
- **飞书 Markdown**：`docs/feishu_benchmark_results.md`

## 飞书导入

1. 飞书文档 → 插入 → 表格 → 导入 CSV → 选 `docs/feishu_benchmark_results.csv`
2. 或将上方总表复制粘贴
