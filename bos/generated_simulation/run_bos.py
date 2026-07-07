"""Battle of the Sexes — Akata et al. (2023) official protocol reproduction.

Asymmetric payoffs per player (question_1 vs question_2 in official repo).
"""

from __future__ import annotations

import argparse
import asyncio
import random
import sys

from simulation_utils.akata_games import (
    BOS_PAYOFF_P1,
    BOS_PAYOFF_P2,
    PAPER_BASELINES_BOS,
    Option,
    bos_rules_p1,
    bos_rules_p2,
    build_choice_prompt,
    build_scot_action_prompt,
    normalize_option,
    opponent_bos,
    update_history,
)
from simulation_utils.llm_trace import emit_trace, llm_text, make_client


async def player_move(
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
        pred_prompt, _ = build_choice_prompt(rules, history, rnd, scot=True, shuffled=False, seed=seed)
        pred_raw = await llm_text(client, model, pred_prompt, max_tokens=2)
        prediction = normalize_option(pred_raw or "J")
        act_prompt = build_scot_action_prompt(rules, history, rnd, prediction)
        raw = await llm_text(client, model, act_prompt, max_tokens=2)
    else:
        prompt, _ = build_choice_prompt(rules, history, rnd, shuffled=False, seed=seed)
        raw = await llm_text(client, model, prompt, max_tokens=2)
    return normalize_option(raw or "J")


async def run(args: argparse.Namespace) -> None:
    client = make_client()
    random.seed(args.seed)
    rules_p1 = bos_rules_p1(args.rounds)
    rules_p2 = bos_rules_p2(args.rounds)
    hist_p1 = ""
    hist_p2 = ""
    rounds: list[tuple[Option, Option]] = []
    coords = 0

    for rnd in range(1, args.rounds + 1):
        a = await player_move(
            client, args.api_model, rules_p1, hist_p1, rnd, args.seed, scot=args.scot
        )
        if args.opponent == "llm":
            b = await player_move(
                client, args.api_model, rules_p2, hist_p2, rnd, args.seed + 1000, scot=args.scot
            )
        else:
            b = opponent_bos(args.opponent, rnd - 1, rounds)

        p1 = BOS_PAYOFF_P1[(a, b)]
        if a == b:
            coords += 1
        rounds.append((a, b))
        hist_p1 = update_history(hist_p1, rnd, a, b, p1[0], p1[1])
        hist_p2 = update_history(hist_p2, rnd, b, a, BOS_PAYOFF_P2[(a, b)][1], BOS_PAYOFF_P2[(a, b)][0])

        emit_trace(
            "round_action",
            {"round": rnd, "agent_choice": a, "opponent_choice": b, "coordinated": a == b, "agent_payoff": p1[0]},
            model="BOS_D1",
            sim_time=float(rnd),
        )

    rate = coords / max(args.rounds, 1)
    key = "llm_scot" if (args.opponent == "llm" and args.scot) else args.opponent
    baseline = PAPER_BASELINES_BOS.get(key, PAPER_BASELINES_BOS.get("llm", 0.55))

    emit_trace(
        "run_summary",
        {
            "rounds": args.rounds,
            "opponent": args.opponent,
            "prompt_mode": "scot" if args.scot else "base",
            "coordination_rate": rate,
            "paper_baseline_coord_rate": baseline,
            "delta_vs_paper": rate - baseline,
        },
        model="BOS_D1",
        sim_time=float(args.rounds),
    )
    print(f"[done] coordination={rate:.2%} mode={'scot' if args.scot else 'base'}", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rounds", type=int, default=10)
    p.add_argument("--opponent", choices=["ac", "ad", "alternate", "llm"], default="llm")
    p.add_argument("--api_model", default="openai/gpt-4o")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--scot", action="store_true")
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
