"""Dictator Game — Horton (2023) style single-shot LLM behavioral test.

Paper: Large Language Models as Simulated Economic Agents (Horton 2023)
Agent allocates endowment between self and recipient.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys

from simulation_utils.llm_trace import emit_trace, llm_json, make_client

PAPER_BASELINE_OFFER = 0.15  # GPT-3 ~15% of endowment in Horton; GPT-4 often higher ~20-30%


async def run(args: argparse.Namespace) -> None:
    client = make_client()
    prompt = (
        f"You are playing a Dictator Game. You receive ${args.endowment}. "
        "You may keep any amount and give the rest to an anonymous recipient. "
        "The recipient cannot reject your offer.\n"
        f"How many dollars (0 to {args.endowment}) do you give to the recipient?\n"
        f'Return JSON only: {{"offer": <number between 0 and {args.endowment}>}}'
    )
    out = await llm_json(client, args.api_model, prompt, max_tokens=60, temperature=0.0)
    offer = float(out.get("offer", 0))
    offer = max(0.0, min(float(args.endowment), offer))
    offer_pct = offer / args.endowment

    emit_trace(
        "dictator_decision",
        {"endowment": args.endowment, "offer": offer, "offer_pct": offer_pct, "keep": args.endowment - offer},
        model="Dictator_D1",
    )
    emit_trace(
        "run_summary",
        {
            "endowment": args.endowment,
            "offer": offer,
            "offer_pct": offer_pct,
            "paper_baseline_offer_pct": PAPER_BASELINE_OFFER,
            "delta_vs_paper": offer_pct - PAPER_BASELINE_OFFER,
        },
        model="Dictator_D1",
    )
    print(f"[done] offer={offer}/{args.endowment} ({offer_pct:.1%})", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--endowment", type=int, default=100)
    p.add_argument("--api_model", default="openai/gpt-4o")
    p.add_argument("--seed", type=int, default=42, help="unused; for benchmark runner compatibility")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
