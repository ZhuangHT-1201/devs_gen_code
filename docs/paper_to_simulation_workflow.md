# 论文 → DEVS 仿真 → 评估结果：工作流

本文档描述如何把一篇**带 LLM Agent 的社会/经济仿真论文**转成可运行的 DEVS 仿真，并产出可对比的宏观/行为结果。  
以 **EconAgent** 为首个完整样例；后续新论文按同一流程复用，只需替换 benchmark 规格与评估脚本。

---

## 0. 适用场景与前置条件

### 适用论文类型

优先选择同时满足以下条件的论文：

1. 使用 **LLM 驱动 Agent** 做决策（而非纯规则或纯 RL）
2. 论文给出或可提取：**实体结构、硬规则、Agent Prompt、实验规模**
3. 有 **可观测的宏观/群体行为** 用于对标（通胀/失业、传播曲线、竞争格局等）
4. **最好有开源代码**（作为 reference implementation，不要求完全一致）

### 环境要求

```powershell
# 推荐 Python 3.12（3.14 部分依赖不兼容）
py -3.12 -m venv .venv312
.\.venv312\Scripts\python -m pip install --upgrade pip
.\.venv312\Scripts\python -m pip install -r requirements.txt xdevs openai matplotlib pandas socksio

# 配置 API（OpenRouter 或 OpenAI 兼容）
copy .env.example .env
# 填写 OPENAI_API_KEY / OPENAI_BASE_URL 或 OPENROUTER_API_KEY / OPENROUTER_API_BASE

# 如需代理
$env:http_proxy="socks5://127.0.0.1:10808"
$env:https_proxy="socks5://127.0.0.1:10808"
$env:PYTHONUTF8="1"
$env:PYTHONIOENCODING="utf-8"
```

先用 **ABP** 跑通 pipeline 基线：

```powershell
.\.venv312\Scripts\python -m devs_app.run --mode generate --debug_args_file benchmark/ABP/ABP_D1.yaml --concur_num 4
```

---

## 1. 阅读论文并提取规格（人工 + Agent）

从论文中提取四类信息，填入后续 YAML：

| 类别 | 内容 | EconAgent 示例 |
|------|------|----------------|
| **实体 (Entities)** | 哪些 Atomic / Coupled 模型 | Household, Government, Bank, Market |
| **硬规则 (Hard Rules)** | 不由 LLM 决定的确定性逻辑 | 累进税、泰勒规则、库存/价格更新 |
| **LLM 决策 (Agent Prompt)** | 角色设定、输入状态、输出 JSON 字段 | `work`, `consumption` ∈ [0,1] |
| **实验参数** | agent 数、时间步、初始条件 | 100 agents × 240 months |

同时记录论文用于对标的 **图表与指标**（如 Figure 2 通胀/失业时序、Figure 3 菲利普斯曲线）。

参考开源实现（若有）：

- EconAgent: https://github.com/tsinghua-fib-lab/ACL24-EconAgent
- 论文: https://arxiv.org/abs/2310.10436

---

## 2. 编写 Benchmark 输入 YAML

在 `benchmark/<PaperName>/` 下新建规格文件，命名建议 `<ModelName>_D1.yaml`。

### YAML 结构（与 ABP / EconAgent 一致）

```yaml
root_model_name: EconAgent_D1          # 生成的根 Coupled 模型名
requirements:
  general: |                           # 语言、依赖、CLI、trace 格式
    ...
  scenario: |                          # 实体、硬规则、LLM prompt、API 约束
    ...
  args_input_output: |                 # 命令行参数与必须输出的 JSONL 事件
    ...
base_folder: econagent_model           # 生成产物目录名
skip_simulation_check: false
only_ensure_executable: false
```

### 编写要点

1. **`general`**：声明 Python 版本、`xdevs`、若需 LLM 则写 `asyncio` + `openai.AsyncOpenAI`
2. **`scenario`**：
   - 列出所有 DEVS 实体及职责
   - **硬规则**写清公式/流程（税、市场、政策等）
   - **LLM 部分**写清：哪些决策必须走 API、prompt 模板、输出 JSON 字段名与类型
   - 明确「禁止用公式替代 LLM 决策」的模型（如 Household）
3. **`args_input_output`**：
   - 仿真参数（`--num_agents`, `--months`, `--simulate_time` 等）
   - **必须输出的 trace 事件名**（如 `macro_snapshot`, `household_decision`），便于后续评估脚本解析

**样例文件**：`benchmark/EconAgent/EconAgent_D1.yaml`

---

## 3. 修改 DEVS-GEN 代码生成模板（LLM 嵌入仿真时必做）

若论文要求 Agent 内嵌 LLM API，需改以下 prompt 模板，否则生成代码可能用公式代替 LLM：

| 文件 | 作用 |
|------|------|
| `devs_tools/devs_construct_pure_fast_plan/tools/model_creator_fast/unified_model_creator.py` | 主代码生成 prompt |
| `devs_tools/devs_construct_pure_fast_plan/tools/model_creator_fast/code_fixer.py` | 修复代码时保持 LLM 约束 |

### 需在模板中强制的内容

- `import asyncio` 与 `from openai import AsyncOpenAI`
- 在 `deltext` / `deltint` 中：`await client.chat.completions.create(..., response_format={"type":"json_object"})`
- 从 JSON 解析论文规定的决策字段（如 `work`, `consumption`）
- 将 LLM 相关 import 加入白名单

纯规则仿真（如 ABP）**无需**此步。

---

## 4. 生成仿真代码

```powershell
.\.venv312\Scripts\python -m devs_app.run `
  --mode generate `
  --debug_args_file benchmark/EconAgent/EconAgent_D1.yaml `
  --concur_num 4
```

生成物位于：

```
devs_app/working_dirs/working_directory_<timestamp>_<id>/<base_folder>/
├── run.py
├── README.md
└── devs_project/
    ├── EconAgent_D1.py              # 顶层 Coupled
    ├── run_econagent_d1.py          # 仿真入口
    └── EconAgent_D1_libs/
        ├── Household.py             # 应含 AsyncOpenAI
        ├── Government.py
        ├── Bank.py
        └── Market.py
```

### 生成后检查清单

- [ ] `Household.py` 是否调用 `AsyncOpenAI`，而非纯公式决策
- [ ] 顶层 Coupled 是否连接**所有** Agent（非仅第一个 household）
- [ ] `run_*.py` 传入参数是否与原子模型 `__init__` 键名一致（如 Taylor 规则参数）
- [ ] Market / Bank 是否按 YAML 描述更新宏观状态并写 `macro_snapshot` 日志
- [ ] `python -m py_compile` 通过

常见问题需人工修补（记录在案，后续可写回 YAML 减少 recurrence）：

- 仅耦合第一个 household
- Bank 调息周期错误（应按年而非按月）
- `run` 脚本与模型参数名不一致

---

## 5. 运行仿真

进入生成目录：

```powershell
cd devs_app/working_dirs/working_directory_<...>/econagent_model

$env:OPENAI_API_KEY="..."
$env:OPENAI_BASE_URL="https://openrouter.ai/api/v1"

# 小规模冒烟（快）
.\..\..\..\..\..\.venv312\Scripts\python.exe .\run.py `
  --num_agents 5 --months 12 --simulate_time 12 `
  --initial_price 100 --initial_rate 0.03 `
  > .\econ_trace_smoke.jsonl

# 论文默认规模（慢：100 agents × 240 months ≈ 数万次 LLM 调用）
.\..\..\..\..\..\.venv312\Scripts\python.exe .\run.py `
  --initial_price 100 --initial_rate 0.03 `
  > .\econ_trace_100x240.jsonl
```

说明：

- `num_agents` / `months` / `simulate_time` 默认在 `run_econagent_d1.py` 中为 100 / 240 / 240
- `initial_price`、`initial_rate` 若设为 `required=True` 则必须显式传入
- 输出为 **JSONL trace**（每行一个 JSON 事件）
- PowerShell `>` 重定向可能混入非 JSON 行；评估脚本已跳过非 `{` 开头的行

### 阶段性结果（长跑时）

仿真未跑完也可先评估已有月份：

```powershell
Copy-Item .\econ_trace_100x240.jsonl .\econ_trace_100x240_partial.jsonl
.\.venv312\Scripts\python.exe .\scripts\econagent_eval.py `
  --trace .\econ_trace_100x240_partial.jsonl `
  --out_dir .\eval_results\econagent_100x240_partial
```

---

## 6. 编写并运行评估脚本

### 与 ABP 类 benchmark 的区别

| 类型 | 评估方式 | 工具 |
|------|----------|------|
| ABP / IOBS 等 | trace 事件与参考 trace **逐条对齐** | `devs_tester/eval_runner.py` |
| EconAgent 等 LLM 宏观仿真 | 从 trace 提取宏观指标，**画图与论文趋势对比** | 自定义脚本 |

### EconAgent 评估脚本

路径：`scripts/econagent_eval.py`

```powershell
.\.venv312\Scripts\python.exe .\scripts\econagent_eval.py `
  --trace <path_to_trace.jsonl> `
  --out_dir .\eval_results\econagent_<scale>
```

输出：

| 文件 | 含义 |
|------|------|
| `monthly_macro.csv` | 月度物价、失业率、平均工资 |
| `annual_metrics.csv` | 年度通胀率、工资通胀率 |
| `inflation_unemployment_timeseries.png` | 对标论文 Figure 2 趋势 |
| `phillips_curve_scatter.png` | 对标论文 Figure 3 菲利普斯曲线 |

trace 解析逻辑：读取 `event == "macro_snapshot"` 的行（字段可在顶层或 `data` 子字典）。

### 新论文的评估脚本

每篇论文通常需要**单独写一个** `scripts/<paper>_eval.py`，至少包含：

1. `load_trace()`：解析该仿真约定的 JSONL 事件
2. `compute_metrics()`：按论文公式计算指标
3. `plot_results()`：生成与论文图表可对比的图

在 YAML 的 `args_input_output` 中**预先规定**必须输出的宏观事件字段，生成代码更容易被评估脚本消费。

---



## 7. 新论文 Agent 执行清单

```
[ ] 1. 确认论文：LLM agent + 宏观行为 + 最好有开源代码
[ ] 2. 提取：实体 / 硬规则 / LLM prompt / 实验参数 / 对标图表
[ ] 3. 新建 benchmark/<Paper>/<Model>_D1.yaml
[ ] 4. 若需 LLM：检查 unified_model_creator.py / code_fixer.py 约束
[ ] 5. 运行 devs_app.run --mode generate --debug_args_file ...
[ ] 6. 检查生成代码（Household LLM、耦合、参数名）
[ ] 7. 冒烟跑通（小 scale）→ 正式跑（论文 scale）
[ ] 8. 编写或复用 scripts/<paper>_eval.py，产出 csv + 图
[ ] 9. 与论文图表/指标做定性或定量对比
[ ] 10. 打包 yaml + 生成仿真 + 评估结果 + README
```


---

## 9. 与官方 EconAgent 工作流对比

| 步骤 | 官方 [ACL24-EconAgent](https://github.com/tsinghua-fib-lab/ACL24-EconAgent) | 本 Pipeline |
|------|---------------------------------------------------------------------------|-------------|
| 建模 | 手写 Foundation 环境 | **YAML 描述 → DEVS-GEN 自动生成** |
| Agent 决策 | GPT 调 API | 生成代码内嵌 `AsyncOpenAI` |
| 运行 | `python simulate.py --num_agents 100 --episode_length 240` | `python run.py --initial_price 100 --initial_rate 0.03` |
| 评估 | 论文自带脚本 | `scripts/econagent_eval.py` + 与 Figure 2/3 对比 |

本 pipeline 的评估目标是：**证明「从论文描述自动生成 LLM 嵌入仿真」可行**，并观察宏观现象是否同量级/同趋势；不要求与官方实现逐行一致。
