# DEVS-Agent (HAMLET Fork)

This repository is a specialized version of the [**HAMLET**](https://github.com/MINDS-THU/HAMLET) framework (Hierarchical Agents for Multi-level Learning, Execution & Tasking), enhanced with capabilities for generating and executing **Discrete Event System (DEVS)** simulations.

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd HAMLET_publish
```

### 2. Environment Setup

We recommend using Conda:

```bash
conda create -n hamlet_env python=3.10 -y
conda activate hamlet_env

conda install -c pytorch faiss-cpu -y
conda install pandas -y
conda install pytorch -y

pip install -r requirements.txt
```

### 3. API Key Configuration

Copy the example file and fill in your keys:

```bash
cp .env.example .env
```

Then edit `.env` with your API credentials:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes (recommended) | API key from [OpenRouter](https://openrouter.ai/) |
| `OPENROUTER_API_BASE` | No | OpenRouter base URL, default: `https://openrouter.ai/api/v1` |
| `OPENAI_API_KEY` | Yes (alternative) | OpenAI-compatible API key (also works with Aliyun, etc.) |
| `OPENAI_BASE_URL` | No | OpenAI-compatible base URL, default: `https://api.openai.com/v1` |
| `SERPER_API_KEY` | Yes | API key from [Serper](https://serper.dev/) for web search |
| `JINA_API_KEY` | Yes | API key from [Jina](https://jina.ai/) for web scraping |
| `HF_TOKEN` | Optional | Hugging Face token for downloading models |

> **Note:** You need at least one of `OPENROUTER_API_KEY` or `OPENAI_API_KEY`. `SERPER_API_KEY` and `JINA_API_KEY` are required for web search capabilities.

## DEVS Model Construction

### Interactive Mode (Gradio UI)

```bash
python -m devs_app.run
```

### CLI Mode

```bash
python -m devs_app.run --mode cli
```

### Non-interactive Generation Mode

Generate a DEVS model from a benchmark specification:

```bash
python -m devs_app.run \
  --mode generate \
  --debug_args_file benchmark/ABP/ABP_D1.yaml \
  --concur_num 4
```

### Key Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--model_id` | `gpt-4.1` | Model for the agent (weak model) |
| `--model_id_strong` | `gpt-5.2` | Model for check/repair steps (strong model) |
| `--mode` | `gradio` | `gradio`, `cli`, `server`, `generate`, `generate_and_test` |
| `--debug_args_file` | `devs_app/devs_model_inputs/example1.json` | Path to JSON/YAML file with tool parameters |
| `--target_tool` | `devs_construct_tree` | Tool name to invoke in generate modes |
| `--concur_num` | `4` | Number of concurrent generation workers |
| `--agent_planning_interval` | `4` | Planning interval for manager agent |
| `--agent_max_steps` | `80` | Max reasoning steps for manager agent |
| `--agent_log_level` | `DEBUG` | Log verbosity: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Reproducing Experiments

### 1. Prepare Baselines

We compare against OpenHands, MetaGPT, and SWE-agent. **Each baseline requires a separate Conda environment and has its own `.env` and `requirements.txt` in its folder**. Fill in the API keys in each baseline's `.env` file.

#### OpenHands

```bash
conda create -n openhands python=3.12
conda activate openhands
pip install -r devs_baseline/openhands_run/requirements.txt
```

Then edit `devs_baseline/openhands_run/.env` with your API keys. See `devs_baseline/openhands_run/README.md` for details.

#### MetaGPT

```bash
conda create -n metagpt python=3.10
conda activate metagpt
pip install -r devs_baseline/meta_gpt_run/requirements.txt
```

Then edit `devs_baseline/meta_gpt_run/.env` with your API keys. See `devs_baseline/meta_gpt_run/README.md` for details.

#### SWE-agent

```bash
conda create -n sweagent python=3.12
conda activate sweagent
pip install -r devs_baseline/swe_agent_run/requirements.txt
```

Build the Docker image:

```bash
cd devs_baseline/swe_agent_run/docker_construct
docker build -t python-xdevs-simpy .
```

Then edit `devs_baseline/swe_agent_run/.env` with your API keys. See `devs_baseline/swe_agent_run/README.md` for details.

Then edit `devs_baseline/openhands_run/.env` with your API keys. See `devs_baseline/openhands_run/README.md` for details.

#### MetaGPT

```bash
conda create -n metagpt python=3.10
conda activate metagpt
pip install -r devs_baseline/meta_gpt_run/requirements.txt
```

Then edit `devs_baseline/meta_gpt_run/.env` with your API keys. See `devs_baseline/meta_gpt_run/README.md` for details.

#### SWE-agent

```bash
conda create -n sweagent python=3.12
conda activate sweagent
pip install -r devs_baseline/swe_agent_run/requirements.txt
```

Build the Docker image:

```bash
cd devs_baseline/swe_agent_run/docker_construct
docker build -t python-xdevs-simpy .
```

Then edit `devs_baseline/swe_agent_run/.env` with your API keys. See `devs_baseline/swe_agent_run/README.md` for details.

### 2. Run Experiments

Navigate to the tester directory:

```bash
cd devs_tester
```

Run a single generation task:

```bash
python gen_runner.py --framework devs_fast_plan --model openai/qwen3.6-plus --benchmark ABP --workspace /tmp/ws
```

List available frameworks and benchmarks:

```bash
python gen_runner.py --list-frameworks
python gen_runner.py --list-benchmarks
```

Evaluate a generated project:

```bash
python eval_runner.py --benchmark ABP --sim_cwd /tmp/ws/abp_model --sim_script run.py --workspace /tmp/results
```

### 3. Experiment Configuration

Edit `devs_tester/experiment_config.py` to configure:

- `BENCHMARKS` -- benchmark catalog with paths to gen config, test config, and checker
- `TARGET_BENCHMARKS` -- which benchmarks to run
- `EXPERIMENT_LLMS` -- model short_name to OpenRouter model_id mapping
- `EXPERIMENT_FRAMEWORKS` -- which frameworks to test
- `GENERATION_TIMEOUTS` -- per-framework generation timeouts

## Project Structure

```
HAMLET_publish/
├── benchmark/              # Benchmark specifications (ABP, SEIRD, SA, etc.)
├── default_tools/          # Default HAMLET tools (file editing, web search, KB, etc.)
├── devs_app/               # Main DEVS agent application
│   └── run.py              # Entry point for all modes
├── devs_baseline/          # Baseline implementations
│   ├── devs_skill/         # Skill-guided baseline scripts
│   ├── meta_gpt_run/       # MetaGPT runner
│   ├── openhands_run/      # OpenHands runner
│   └── swe_agent_run/      # SWE-agent runner
├── devs_tester/            # Experiment orchestration suite
│   ├── experiment_config.py # All experiment parameters
│   ├── gen_runner.py       # Code generation engine
│   └── eval_runner.py      # Evaluation pipeline (simulation + checker)
├── devs_tools/             # DEVS-specific tools
│   └── devs_construct_pure_fast_plan/  # Plan-then-construct DEVS tool
├── example_app/            # Standard HAMLET example application
├── src/                    # Core HAMLET framework code
│   ├── models.py           # Model definitions
│   ├── local_python_executor.py
│   ├── remote_executors.py
│   └── ...
└── requirements.txt
```

## Benchmarks

| Name | Description |
|------|-------------|
| ABP | Alternating Bit Protocol |
| SEIRD | Epidemiological model |
| SA | Simulated Annealing |
| OTrain | Airport Operations Train |
| IOBS | Island Observing Station |
| barbershop | Barber Shop simulation |
| oft | Ocean Freight Terminal |
| ComplexSup1 | Complex Supply Network 1 |
| ComplexSup2 | Complex Supply Network 2 |

## Frameworks

| Framework | Description |
|-----------|-------------|
| `devs_tool` | DEVS construct with check loop |
| `devs_fast_plan` | DEVS fast plan-then-construct (no check, concurrent) |
| `meta_gpt` | MetaGPT multi-agent |
| `swe_agent` | SWE-Agent standard |
| `openhands` | OpenHands standard |

## Core HAMLET Features

Since this project is built on HAMLET, it supports all standard HAMLET features for general-purpose agent tasks.

### Key Tools

HAMLET includes a suite of default tools located in `default_tools/`:

- **File Management**: `list_dir`, `see_text_file`, `modify_file`, etc.
- **Knowledge Base (KB)**: Semantic search, file addition, and management.
- **Web Capabilities**: `web_search` (Deep Search), `text_web_browser`.
- **Visual Capabilities**: `visualizer` (Visual QA).

### Running Standard Agent Example

A pre-configured example application is included in `example_app/`:

```bash
python -m example_app.run
```
