# SWE agent 适配方法
推荐使用conda重新创建一个新环境。

1. 创建环境：
```bash
conda create -n sweagent python=3.12
conda activate sweagent
pip install -r requirements.txt
```
2. 构建需要使用的docker：
```bash
cd docker_construct
docker build -t python-xdevs-simpy .
```
3. 把测试脚本里的 conda_env 变量改成这里实际的环境名（上面的例子里是 sweagent）。
4. 在本文件夹（`devs_baseline/swe_agent_run`）底下复制一份放在最外面的 `.env` 文件。或者从零创建并指定相关环境变量:
```bash
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENROUTER_API_KEY=sk-xxx
OPENROUTER_API_BASE=https://openrouter.ai/api/v1
NEBIUS_API_KEY=sk-xxx
NEBIUS_API_BASE=https://api.tokenfactory.nebius.com/v1/
```
我们的模型会自动解析 llm 名称，会做如下选择：
  1. model_id=openrouter/**, 则使用 OPENROUTER_API_KEY, OPENROUTER_API_BASE
  2. model_id=nebius/**, 则使用 NEBIUS_API_BASE, NEBIUS_API_KEY
  3. otherwise, 使用 OPENAI_API_KEY, OPENAI_BASE_URL
