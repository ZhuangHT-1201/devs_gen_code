"""Entry point for CompeteAI mini simulation."""

import runpy
import sys

if __name__ == "__main__":
    runpy.run_module("competeai.generated_simulation.run_competeai_mini", run_name="__main__")
