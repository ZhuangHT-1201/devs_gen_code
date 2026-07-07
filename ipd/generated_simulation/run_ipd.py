"""Iterated Prisoner's Dilemma — Akata et al. (2023) official protocol reproduction.

Paper: https://arxiv.org/abs/2305.16867
Official code: https://github.com/eliaka/repeatedgames (pd/query_main.py)
Uses Option J (cooperate) / F (defect), 10 rounds by default, temperature=0.
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys

from simulation_utils.akata_games import (
    PAPER_BASELINES_IPD,
    PD_PAYOFF,
    Option,
    build_choice_prompt,
    build_scot_action_prompt,
    normalize_option,
    opponent_pd,
    pd_rules,
    update_history,
)
from simulation_utils.llm_trace import emit_trace, llm_text, make_client


async def agent_move(
    client,
    model: str,
    rules: str,
    history: str,
    rnd: int,
    seed: int,
    *,
    scot: bool,
) -> Option:
    if scot:
        pred_prompt, _ = build_choice_prompt(rules, history, rnd, scot=True, seed=seed)
        pred_raw = await llm_text(client, model, pred_prompt, max_tokens=2)
        prediction = normalize_option(pred_raw or "F")
        act_prompt = build_scot_action_prompt(rules, history, rnd, prediction)
        raw = await llm_text(client, model, act_prompt, max_tokens=2)
    else:
        prompt, _ = build_choice_prompt(rules, history, rnd, scot=False, seed=seed)
        raw = await llm_text(client, model, prompt, max_tokens=2)
    return normalize_option(raw or "F")


async def run(args: argparse.Namespace) -> None:
    client = make_client()
    random.seed(args.seed)
    rules = pd_rules(args.rounds)
    history_agent = ""
    history_opp = ""
    rounds: list[tuple[Option, Option]] = []
    totals = [0, 0]
    agent_coops = 0

    for rnd in range(1, args.rounds + 1):
        a = await agent_move(
            client, args.api_model, rules, history_agent, rnd, args.seed, scot=args.scot
        )
        if args.opponent == "llm":
            b = await agent_move(
                client, args.api_model, rules, history_opp, rnd, args.seed + 1000, scot=args.scot
            )
        else:
            b = opponent_pd(args.opponent, rnd - 1, rounds)

        p = PD_PAYOFF[(a, b)]
        totals[0] += p[0]
        totals[1] += p[1]
        if a == "J":
            agent_coops += 1
        rounds.append((a, b))

        history_agent = update_history(history_agent, rnd, a, b, p[0], p[1])
        history_opp = update_history(history_opp, rnd, b, a, p[1], p[0])

        emit_trace(
            "round_action",
            {
                "round": rnd,
                "agent_action": a,
                "opponent_action": b,
                "agent_cooperated": a == "J",
                "agent_payoff": p[0],
                "opponent_payoff": p[1],
            },
            model="IPD_D1",
            sim_time=float(rnd),
        )

    coop_rate = agent_coops / max(args.rounds, 1)
    mutual_coop = sum(1 for x, y in rounds if x == "J" and y == "J") / max(args.rounds, 1)
    baseline = PAPER_BASELINES_IPD.get(args.opponent, PAPER_BASELINES_IPD.get("llm", 0.55))

    emit_trace(
        "run_summary",
        {
            "rounds": args.rounds,
            "opponent": args.opponent,
            "prompt_mode": "scot" if args.scot else "base",
            "agent_cooperation_rate": coop_rate,
            "mutual_cooperation_rate": mutual_coop,
            "total_payoff_agent": totals[0],
            "total_payoff_opponent": totals[1],
            "paper_baseline_coop_rate": baseline,
            "delta_vs_paper": coop_rate - baseline,
        },
        model="IPD_D1",
        sim_time=float(args.rounds),
    )
    print(f"[done] agent_coop={coop_rate:.2%} mutual={mutual_coop:.2%} mode={'scot' if args.scot else 'base'}", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=10)
    p.add_argument("--opponent", choices=["ac", "ad", "tft", "llm", "defect_once"], default="tft")
    p.add_argument("--api_model", default="openai/gpt-4o")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--scot", action="store_true", help="Social chain-of-thought (predict then act)")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
