"""Akata et al. (2023) repeated-game protocol — aligned with eliaka/repeatedgames."""

from __future__ import annotations

import random
from typing import Literal

Option = Literal["J", "F"]

# Paper Figure 3 / official pd/query_main.py payoffs (J=cooperate, F=defect)
PD_PAYOFF = {
    ("J", "J"): (8, 8),
    ("J", "F"): (0, 10),
    ("F", "J"): (10, 0),
    ("F", "F"): (5, 5),
}

# Paper Figure 5 / official bos/query_main.py — player-specific matrices
BOS_PAYOFF_P1 = {("J", "J"): (10, 7), ("J", "F"): (0, 0), ("F", "J"): (0, 0), ("F", "F"): (7, 10)}
BOS_PAYOFF_P2 = {("J", "J"): (7, 10), ("J", "F"): (0, 0), ("F", "J"): (0, 0), ("F", "F"): (10, 7)}

PAPER_BASELINES_IPD = {
    "ac": 0.85,   # vs always-J (act_j)
    "ad": 0.15,   # vs always-F (act_f) — agent cooperates ~15% (defects ~85%)
    "tft": 0.70,  # approximate from Figure 3
    "llm": 0.55,
    "defect_once": 0.10,
}

PAPER_BASELINES_BOS = {
    "ac": 0.90,       # vs always-J
    "ad": 0.90,       # vs always-F (both pick same fixed option)
    "alternate": 0.30,  # vs alternating — GPT-4 poorly coordinates
    "llm": 0.55,
    "llm_scot": 0.70,
}


def normalize_option(raw: str) -> Option:
    x = raw.strip().upper()
    # Paper completes after "A: Option" — often just " J" or " F"
    for ch in x:
        if ch == "J":
            return "J"
        if ch == "F":
            return "F"
    return "F"


def pd_rules(num_rounds: int) -> str:
    return (
        "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "
        f"You will play {num_rounds} rounds in total with the same player. "
        "The rules of the game are as follows:\n"
        "If you choose Option J and the other player chooses Option J, then you win 8 points and the other player wins 8 points.\n"
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 10 points.\n"
        "If you choose Option F and the other player chooses Option J, then you win 10 points and the other player wins 0 points.\n"
        "If you choose Option F and the other player chooses Option F, then you win 5 points and the other player wins 5 points.\n\n"
    )


def bos_rules_p1(num_rounds: int) -> str:
    return (
        "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "
        f"You will play {num_rounds} rounds in total with the same player. "
        "The rules of the game are as follows:\n"
        "If you choose Option J and the other player chooses Option J, then you win 10 points and the other player wins 7 points.\n"
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"
        "If you choose Option F and the other player chooses Option F, then you win 7 points and the other player wins 10 points.\n\n"
    )


def bos_rules_p2(num_rounds: int) -> str:
    return (
        "You are playing a game repeatedly with another player. In this game, you can choose between Option J and Option F. "
        f"You will play {num_rounds} rounds in total with the same player. "
        "The rules of the game are as follows:\n"
        "If you choose Option J and the other player chooses Option J, then you win 7 points and the other player wins 10 points.\n"
        "If you choose Option J and the other player chooses Option F, then you win 0 points and the other player wins 0 points.\n"
        "If you choose Option F and the other player chooses Option J, then you win 0 points and the other player wins 0 points.\n"
        "If you choose Option F and the other player chooses Option F, then you win 10 points and the other player wins 7 points.\n\n"
    )


def update_history(history: str, rnd: int, my_choice: Option, opp_choice: Option, my_pts: int, opp_pts: int) -> str:
    return (
        history
        + f"In round {rnd}, you chose Option {my_choice} and the other player chose Option {opp_choice}. "
        + f"Thus, you won {my_pts} points and the other player won {opp_pts} points.\n"
    )


def build_choice_prompt(
    rules: str,
    history: str,
    rnd: int,
    *,
    scot: bool = False,
    shuffled: bool = True,
    seed: int = 0,
) -> tuple[str, list[str]]:
    opts = ["J", "F"]
    if shuffled:
        rng = random.Random(seed + rnd)
        rng.shuffle(opts)
    if scot:
        predict = (
            rules
            + history
            + f"You are currently playing round {rnd}.\n"
            + "Q: Which Option do you predict the other player will choose, Option J or Option F?\nA: Option"
        )
        return predict, opts
    prompt = (
        rules
        + history
        + f"\nYou are currently playing round {rnd}.\n"
        + f"Q: Which Option do you choose, Option {opts[0]} or Option {opts[1]}?\nA: Option"
    )
    return prompt, opts


def build_scot_action_prompt(rules: str, history: str, rnd: int, prediction: Option) -> str:
    return (
        rules
        + history
        + f"You are currently playing round {rnd}.\n"
        + f"Q: Given that you think the other player will choose Option {prediction} in round {rnd}, "
        + "which Option do you think is the best to choose for you in this round, Option J or Option F?\nA: Option"
    )


def opponent_pd(opponent: str, rnd_idx: int, history: list[tuple[Option, Option]]) -> Option:
    if opponent == "ac":
        return "J"
    if opponent == "ad":
        return "F"
    if opponent == "tft":
        return history[-1][0] if history else "J"
    if opponent == "defect_once":
        return "F" if rnd_idx == 0 else "J"
    raise ValueError(f"unknown pd opponent: {opponent}")


def opponent_bos(opponent: str, rnd_idx: int, history: list[tuple[Option, Option]]) -> Option:
    if opponent == "ac":
        return "J"
    if opponent == "ad":
        return "F"
    if opponent == "alternate":
        return "F" if rnd_idx % 2 == 0 else "J"
    raise ValueError(f"unknown bos opponent: {opponent}")
