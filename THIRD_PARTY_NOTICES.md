# Third-Party Notices

This document summarizes major third-party components, reused source files, and their licenses as used by this repository.

## Source-level reuse and included frameworks

- HAMLET
  - Upstream: https://github.com/MINDS-THU/HAMLET
  - License: Apache-2.0
  - Usage here: Base framework this repository is forked from and extended.

- smolagents
  - Upstream: https://github.com/huggingface/smolagents
  - License: Apache-2.0
  - Usage here: Core agent library dependency.

- AutoGen (code adaptation)
  - Upstream: https://github.com/microsoft/autogen
  - Code license: MIT (see upstream `LICENSE-CODE`)
  - Files in this repository:
    - `default_tools/text_web_browser/mdconvert.py`
    - `default_tools/text_web_browser/text_web_browser.py`
  - Note: These files include attribution comments pointing to upstream source.

## Runtime dependencies used by baselines

- xDEVS.py / xdevs
  - Upstream: https://github.com/iscar-ucm/xdevs.py
  - License: GPL-3.0
  - Usage here: Installed as a runtime dependency (`xdevs==3.0.0`) for DEVS simulation in baseline environments and Docker image setup.
  - Distribution note: The xdevs source repository is not vendored in this repository.

- SWE-agent
  - Upstream: https://github.com/SWE-agent/SWE-agent
  - License: MIT
  - Usage here: Experimental baseline framework.

- MetaGPT
  - Upstream: https://github.com/FoundationAgents/MetaGPT
  - License: MIT
  - Usage here: Experimental baseline framework.

- OpenHands
  - Upstream: https://github.com/OpenHands/OpenHands
  - License: Mixed in upstream repository (MIT for open-source portions; separate license for `enterprise/` in upstream repository)
  - Usage here: Experimental baseline framework.

## Notes

- This file is informational and not a substitute for the original license texts.
- When redistributing or deploying, review upstream repositories and package metadata for the exact license terms and any updates.
