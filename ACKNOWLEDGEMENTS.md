# Acknowledgements

This project builds on and integrates ideas, code, and tooling from several open-source projects.

- HAMLET by MINDS-THU: https://github.com/MINDS-THU/HAMLET
  - This repository is a DEVS-focused fork and extension of HAMLET.

- smolagents by Hugging Face: https://github.com/huggingface/smolagents
  - Core agent abstractions and execution patterns are based on smolagents.

- AutoGen by Microsoft: https://github.com/microsoft/autogen
  - Parts of the text web browsing utilities in `default_tools/text_web_browser/` are adapted from AutoGen code (see `THIRD_PARTY_NOTICES.md` for details).

- Baseline frameworks used for experiments:
  - OpenHands: https://github.com/OpenHands/OpenHands
  - MetaGPT: https://github.com/FoundationAgents/MetaGPT
  - SWE-agent: https://github.com/SWE-agent/SWE-agent

- DEVS simulator ecosystem:
  - xDEVS.py: https://github.com/iscar-ucm/xdevs.py
  - The SWE-agent Docker environment installs xdevs from PyPI for DEVS execution.

We thank all original authors and maintainers for their contributions to the open-source community.
