# CompeteAI Pipeline Sample

Paper: [CompeteAI (ICML 2024)](https://arxiv.org/abs/2310.17512)

## Files

| Path | Description |
|------|-------------|
| `benchmark/CompeteAI/CompeteAI_D1.yaml` | Paper → DEVS spec |
| `devs_app/working_dirs/.../competeai_model/` | DEVS-GEN output (Qwen3-Coder) |
| `competeai/generated_simulation/run_competeai_mini.py` | Runnable mini sim (procedural fix) |
| `scripts/competeai_eval.py` | Eval: market share / revenue plots |

## Run (smoke)

```powershell
cd SocioDEVS
# load .env (OPENROUTER_API_KEY, OPENAI_BASE_URL)
$env:PYTHONUTF8="1"
.\.venv312\Scripts\python.exe -m competeai.generated_simulation.run_competeai_mini `
  --num_restaurants 2 --num_customers 3 --num_rounds 4 `
  --api_model deepseek/deepseek-chat > competeai_trace.jsonl

.\.venv312\Scripts\python.exe .\scripts\competeai_eval.py `
  --trace competeai_trace.jsonl `
  --out_dir .\eval_results\competeai_2x3x4
```

Note: SOCKS proxy `127.0.0.1:10808` was offline during run; OpenRouter worked directly with `deepseek/deepseek-chat`.
