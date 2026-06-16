# EconAgent Local Pipeline Guide

## 1) Environment and baseline

Use Python 3.12 venv (3.14 has dependency incompatibilities):

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\python -m pip install --upgrade pip
.\.venv312\Scripts\python -m pip install -r requirements.txt xdevs openai matplotlib
copy .env.example .env
```

Fill `.env` with at least one LLM key (`OPENAI_API_KEY` or `OPENROUTER_API_KEY`).

Run ABP baseline generation:

```powershell
.\.venv312\Scripts\python -m devs_app.run --mode generate --debug_args_file benchmark/ABP/ABP_D1.yaml --concur_num 4
```

Then evaluate generated project (replace paths):

```powershell
cd devs_tester
..\.venv312\Scripts\python eval_runner.py --benchmark ABP --sim_cwd <generated_abp_project_path> --sim_script run.py --workspace <abp_eval_workspace>
```

## 2) EconAgent specification input

Prepared benchmark spec file:

- `benchmark/EconAgent/EconAgent_D1.yaml`

It includes:

- Entity definitions: `Household`, `Government`, `Bank`, `Market`, `EconSystem`.
- Hard rules: tax/redistribution, Taylor rule, inventory and market dynamics.
- Household LLM prompt adapted from EconAgent appendix.
- Mandatory async OpenAI structured JSON call constraints.

## 3) Pipeline prompt-template modifications

Updated generation constraints:

- `devs_tools/devs_construct_pure_fast_plan/tools/model_creator_fast/unified_model_creator.py`
- `devs_tools/devs_construct_pure_fast_plan/tools/model_creator_fast/code_fixer.py`

Added requirements force generated atomic code to:

- import `asyncio` and `AsyncOpenAI`.
- call `await client.chat.completions.create(..., response_format={"type":"json_object"})`.
- parse JSON and extract `work` / `consumption` floats.
- avoid formula-only decisions when spec demands LLM behavior.

## 4) Generate and debug EconAgent

Run generation:

```powershell
.\.venv312\Scripts\python -m devs_app.run --mode generate --debug_args_file benchmark/EconAgent/EconAgent_D1.yaml --concur_num 4
```

After generation:

- Open generated household atomic model and check async call syntax.
- Confirm no blocking loop in DEVS transition handlers.
- Run simulation with target scale (example: 100 agents, 240 months).

## 5) Evaluation script and charts

Prepared script:

- `scripts/econagent_eval.py`

Usage:

```powershell
.\.venv312\Scripts\python scripts/econagent_eval.py --trace <path_to_event_trace.jsonl> --out_dir eval_results/econagent
```

Outputs:

- `monthly_macro.csv`
- `annual_metrics.csv`
- `inflation_unemployment_timeseries.png`
- `phillips_curve_scatter.png`

Use these two plots to compare against EconAgent paper Figure 2 and Figure 3 trends.
