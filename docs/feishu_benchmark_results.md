# Benchmark 跑批结果汇总（飞书粘贴版）

> 生成时间：自动汇总 | 数据源：`eval_results/benchmark_full`
> 代理：HTTP_PROXY=socks5://127.0.0.1:10808

## 总表

| 论文 | arXiv | 实验ID | 模型 | 指标 | 我们的结果 | 论文基线 | 差值 | 复现判定 | 论文说明 | 结果路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm | deepseek/deepseek-chat | 协调率 | 100.0% | 35% | +65.0% | ❌ 未复现 | GPT-4 互玩，论文协调率偏低 | eval_results/benchmark_full/deepseek_deepseek-chat/bos_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_ac | deepseek/deepseek-chat | 协调率 | 100.0% | 50% | +50.0% | ❌ 未复现 | 对手固定选A，参考50% | eval_results/benchmark_full/deepseek_deepseek-chat/bos_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_tft | deepseek/deepseek-chat | 协调率 | 100.0% | 45% | +55.0% | ❌ 未复现 | 论文：无固定策略基线，约45%参考 | eval_results/benchmark_full/deepseek_deepseek-chat/bos_vs_tft |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x3x4 | deepseek/deepseek-chat | Matthew效应 | R0:100% / R1:0% | 定性 | — | Pipeline验证 | 论文：领先餐厅份额逐日扩大；需14顾客+菜单API | eval_results/benchmark_full/deepseek_deepseek-chat/competeai_2x3x4 |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6 | deepseek/deepseek-chat | Matthew效应 | R0:100% / R1:0% | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_full/deepseek_deepseek-chat/competeai_2x5x6 |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6_s99 | deepseek/deepseek-chat | Matthew效应 | R0:100% / R1:0% | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_full/deepseek_deepseek-chat/competeai_2x5x6_s99 |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ac | deepseek/deepseek-chat | Agent合作率 | 8.0% (互合作8.0%) | 85% | -77.0% | ❌ 未复现 | GPT-4 vs Always-Cooperate，论文约85% | eval_results/benchmark_full/deepseek_deepseek-chat/ipd_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ad | deepseek/deepseek-chat | Agent合作率 | 8.0% (互合作0.0%) | 35% | -27.0% | ⚠️ 趋势接近 | GPT-4 vs Always-Defect，论文约35% | eval_results/benchmark_full/deepseek_deepseek-chat/ipd_vs_ad |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_llm | deepseek/deepseek-chat | Agent合作率 | 8.0% (互合作0.0%) | 55% | -47.0% | ❌ 未复现 | GPT-4 vs GPT-4，论文约55% | eval_results/benchmark_full/deepseek_deepseek-chat/ipd_vs_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft | deepseek/deepseek-chat | Agent合作率 | 20.0% (互合作0.0%) | 70% | -50.0% | ❌ 未复现 | GPT-4 vs TFT，论文约70% | eval_results/benchmark_full/deepseek_deepseek-chat/ipd_vs_tft |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft_seed7 | deepseek/deepseek-chat | Agent合作率 | 40.0% (互合作20.0%) | 70% | -30.0% | ⚠️ 趋势接近 | 同 ipd_vs_tft | eval_results/benchmark_full/deepseek_deepseek-chat/ipd_vs_tft_seed7 |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_llm | openai/gpt-4o | 协调率 | 100.0% | 35% | +65.0% | ❌ 未复现 | GPT-4 互玩，论文协调率偏低 | eval_results/benchmark_full/openai_gpt-4o/bos_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_ac | openai/gpt-4o | 协调率 | 100.0% | 50% | +50.0% | ❌ 未复现 | 对手固定选A，参考50% | eval_results/benchmark_full/openai_gpt-4o/bos_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | bos_vs_tft | openai/gpt-4o | 协调率 | 100.0% | 45% | +55.0% | ❌ 未复现 | 论文：无固定策略基线，约45%参考 | eval_results/benchmark_full/openai_gpt-4o/bos_vs_tft |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x3x4 | openai/gpt-4o | Matthew效应 | R0:67% / R1:33% | 定性 | — | Pipeline验证 | 论文：领先餐厅份额逐日扩大；需14顾客+菜单API | eval_results/benchmark_full/openai_gpt-4o/competeai_2x3x4 |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6 | openai/gpt-4o | Matthew效应 | R0:60% / R1:40% | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_full/openai_gpt-4o/competeai_2x5x6 |
| CompeteAI (Zhao ICML 2024) | 2310.17512 | competeai_2x5x6_s99 | openai/gpt-4o | Matthew效应 | R0:0% / R1:100% | 定性 | — | Pipeline验证 | 同上 | eval_results/benchmark_full/openai_gpt-4o/competeai_2x5x6_s99 |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ac | openai/gpt-4o | Agent合作率 | 100.0% (互合作100.0%) | 85% | +15.0% | ⚠️ 趋势接近 | GPT-4 vs Always-Cooperate，论文约85% | eval_results/benchmark_full/openai_gpt-4o/ipd_vs_ac |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_ad | openai/gpt-4o | Agent合作率 | 4.0% (互合作0.0%) | 35% | -31.0% | ❌ 未复现 | GPT-4 vs Always-Defect，论文约35% | eval_results/benchmark_full/openai_gpt-4o/ipd_vs_ad |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_llm | openai/gpt-4o | Agent合作率 | 100.0% (互合作100.0%) | 55% | +45.0% | ❌ 未复现 | GPT-4 vs GPT-4，论文约55% | eval_results/benchmark_full/openai_gpt-4o/ipd_vs_llm |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft | openai/gpt-4o | Agent合作率 | 100.0% (互合作100.0%) | 70% | +30.0% | ❌ 未复现 | GPT-4 vs TFT，论文约70% | eval_results/benchmark_full/openai_gpt-4o/ipd_vs_tft |
| Playing Repeated Games with LLMs (Akata 2023) | 2305.16867 | ipd_vs_tft_seed7 | openai/gpt-4o | Agent合作率 | 100.0% (互合作100.0%) | 70% | +30.0% | ❌ 未复现 | 同 ipd_vs_tft | eval_results/benchmark_full/openai_gpt-4o/ipd_vs_tft_seed7 |

## 按论文分组结论

### Playing Repeated Games with LLMs (Akata 2023)
- 实验数 16，部分复现 0，趋势接近 3
  - `bos_llm` (deepseek/deepseek-chat): 100.0% vs 论文35% → ❌ 未复现
  - `bos_vs_ac` (deepseek/deepseek-chat): 100.0% vs 论文50% → ❌ 未复现
  - `bos_vs_tft` (deepseek/deepseek-chat): 100.0% vs 论文45% → ❌ 未复现
  - `ipd_vs_ac` (deepseek/deepseek-chat): 8.0% (互合作8.0%) vs 论文85% → ❌ 未复现
  - `ipd_vs_ad` (deepseek/deepseek-chat): 8.0% (互合作0.0%) vs 论文35% → ⚠️ 趋势接近
  - `ipd_vs_llm` (deepseek/deepseek-chat): 8.0% (互合作0.0%) vs 论文55% → ❌ 未复现
  - `ipd_vs_tft` (deepseek/deepseek-chat): 20.0% (互合作0.0%) vs 论文70% → ❌ 未复现
  - `ipd_vs_tft_seed7` (deepseek/deepseek-chat): 40.0% (互合作20.0%) vs 论文70% → ⚠️ 趋势接近
  - `bos_llm` (openai/gpt-4o): 100.0% vs 论文35% → ❌ 未复现
  - `bos_vs_ac` (openai/gpt-4o): 100.0% vs 论文50% → ❌ 未复现
  - `bos_vs_tft` (openai/gpt-4o): 100.0% vs 论文45% → ❌ 未复现
  - `ipd_vs_ac` (openai/gpt-4o): 100.0% (互合作100.0%) vs 论文85% → ⚠️ 趋势接近
  - `ipd_vs_ad` (openai/gpt-4o): 4.0% (互合作0.0%) vs 论文35% → ❌ 未复现
  - `ipd_vs_llm` (openai/gpt-4o): 100.0% (互合作100.0%) vs 论文55% → ❌ 未复现
  - `ipd_vs_tft` (openai/gpt-4o): 100.0% (互合作100.0%) vs 论文70% → ❌ 未复现
  - `ipd_vs_tft_seed7` (openai/gpt-4o): 100.0% (互合作100.0%) vs 论文70% → ❌ 未复现

### CompeteAI (Zhao ICML 2024)
- 实验数 6，部分复现 0，趋势接近 0
  - `competeai_2x3x4` (deepseek/deepseek-chat): R0:100% / R1:0% vs 论文定性 → Pipeline验证
  - `competeai_2x5x6` (deepseek/deepseek-chat): R0:100% / R1:0% vs 论文定性 → Pipeline验证
  - `competeai_2x5x6_s99` (deepseek/deepseek-chat): R0:100% / R1:0% vs 论文定性 → Pipeline验证
  - `competeai_2x3x4` (openai/gpt-4o): R0:67% / R1:33% vs 论文定性 → Pipeline验证
  - `competeai_2x5x6` (openai/gpt-4o): R0:60% / R1:40% vs 论文定性 → Pipeline验证
  - `competeai_2x5x6_s99` (openai/gpt-4o): R0:0% / R1:100% vs 论文定性 → Pipeline验证


## 附录：EconAgent 探索性跑批（非本次矩阵，pipeline 验证）

| 论文 | 实验 | 规模 | 模型 | 结论 | 路径 |
| --- | --- | --- | --- | --- | --- |
| EconAgent ACL 2024 | 宏观仿真 | 20×60 | LLM嵌入 | 链路通，宏观形态未对齐 Figure 2/3 | eval_results/econagent_20x60_tuned2 |
| EconAgent ACL 2024 | 宏观仿真 | 100×240 partial | LLM嵌入 | 112 months 快照，通胀/失业波动偏大 | eval_results/econagent_100x240_partial |
| EconAgent ACL 2024 | 宏观仿真 | 5×12 smoke | LLM嵌入 | 冒烟通过 | eval_results/econagent_smoke_5x12_tuned2 |

## 飞书导入说明

1. 打开飞书文档 → 插入 → 表格 → 导入 CSV
2. 选择仓库内 `docs/feishu_benchmark_results.csv`
3. 或将上方 Markdown 表格直接复制粘贴
