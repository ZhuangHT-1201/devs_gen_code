"""CompeteAI mini procedural runner (post-generation fix).

The auto-generated DEVS coupled model lacks a round orchestrator, so this script
implements the benchmark YAML spec directly while keeping the same JSONL schema.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from typing import Any

from openai import AsyncOpenAI


def _client() -> AsyncOpenAI:
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    base = os.getenv("OPENROUTER_API_BASE") or os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1"
    return AsyncOpenAI(api_key=key, base_url=base)


def _emit(event: str, data: dict, model: str = "CompeteAI_D1", sim_time: float = 0.0) -> None:
    print(json.dumps({"time": sim_time, "model": model, "event": event, "data": data}, ensure_ascii=False))


async def _llm_json(client: AsyncOpenAI, model: str, prompt: str) -> dict[str, Any]:
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0.7,
        )
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            return {}
        return json.loads(content)
    except Exception as exc:
        print(f"[warn] LLM JSON parse failed: {exc}", file=sys.stderr)
        return {}


async def _restaurant_strategy(
    client: AsyncOpenAI,
    model: str,
    rid: int,
    rnd: int,
    state: dict[str, Any],
) -> dict[str, Any]:
    prompt = (
        f"You are restaurant owner #{rid}. Round {rnd}.\n"
        f"Market shares last round: {state['market_shares']}\n"
        f"Revenues: {state['revenues']}\n"
        f"Reputations: {state['reputations']}\n"
        "Return JSON: {\"focus\": str, \"price_level\": int 1-3, \"promotion\": str}"
    )
    out = await _llm_json(client, model, prompt)
    price = max(1, min(3, int(round(float(out.get("price_level", 2))))))
    data = {
        "round": rnd,
        "restaurant_id": rid,
        "focus": str(out.get("focus", "General")),
        "price_level": price,
        "promotion": str(out.get("promotion", "")),
    }
    _emit("restaurant_strategy", data, model="RestaurantAgent", sim_time=float(rnd))
    return data


async def _customer_choice(
    client: AsyncOpenAI,
    model: str,
    cid: int,
    rnd: int,
    strategies: list[dict[str, Any]],
) -> dict[str, Any]:
    lines = "\n".join(
        f"- id={s['restaurant_id']}: focus={s['focus']}, price={s['price_level']}, promo={s['promotion']}"
        for s in strategies
    )
    prompt = (
        f"You are customer #{cid}. Round {rnd}.\n"
        f"Restaurants:\n{lines}\n"
        "Pick one restaurant. Return JSON: {\"restaurant_id\": int, \"satisfaction\": float 1-5}"
    )
    out = await _llm_json(client, model, prompt)
    valid_ids = {s["restaurant_id"] for s in strategies}
    rid = int(out.get("restaurant_id", strategies[0]["restaurant_id"]))
    sat = max(1.0, min(5.0, float(out.get("satisfaction", 3.0))))
    if rid not in valid_ids:
        rid = random.choice(list(valid_ids))
        sat = max(1.0, sat - 1.0)
    data = {"round": rnd, "customer_id": cid, "restaurant_id": rid, "satisfaction": sat}
    _emit("customer_choice", data, model="CustomerAgent", sim_time=float(rnd))
    return data


def _settle_round(
    rnd: int,
    choices: list[dict[str, Any]],
    strategies: list[dict[str, Any]],
    state: dict[str, Any],
    base_ticket: float,
) -> dict[str, Any]:
    num_restaurants = len(state["revenues"])
    visits = {str(i): 0 for i in range(num_restaurants)}
    sat_sum = {str(i): 0.0 for i in range(num_restaurants)}
    price_map = {s["restaurant_id"]: s["price_level"] for s in strategies}

    for c in choices:
        rid = str(c["restaurant_id"])
        if rid in visits:
            visits[rid] += 1
            sat_sum[rid] += c["satisfaction"]

    total = sum(visits.values())
    shares = {k: (v / total if total else 1.0 / num_restaurants) for k, v in visits.items()}

    for i in range(num_restaurants):
        key = str(i)
        rev_inc = visits[key] * price_map.get(i, 2) * base_ticket
        state["revenues"][key] = state["revenues"].get(key, 0.0) + rev_inc
        if visits[key] > 0:
            avg_sat = sat_sum[key] / visits[key]
            state["reputations"][key] = 0.7 * state["reputations"][key] + 0.3 * avg_sat

    state["market_shares"] = shares
    snap = {
        "round": rnd,
        "market_shares": shares,
        "revenues": dict(state["revenues"]),
        "reputations": dict(state["reputations"]),
        "total_visits": total,
    }
    _emit("round_snapshot", snap, model="CompetitionMarket", sim_time=float(rnd))
    return snap


async def run_sim(args: argparse.Namespace) -> None:
    client = _client()
    random.seed(args.seed)

    state: dict[str, Any] = {
        "market_shares": {str(i): 1.0 / args.num_restaurants for i in range(args.num_restaurants)},
        "revenues": {str(i): 0.0 for i in range(args.num_restaurants)},
        "reputations": {str(i): 5.0 for i in range(args.num_restaurants)},
    }

    for rnd in range(1, args.num_rounds + 1):
        print(f"[stderr] Round {rnd}/{args.num_rounds}", file=sys.stderr)
        strategies = await asyncio.gather(
            *[
                _restaurant_strategy(client, args.api_model, rid, rnd, state)
                for rid in range(args.num_restaurants)
            ]
        )
        choices = await asyncio.gather(
            *[
                _customer_choice(client, args.api_model, cid, rnd, strategies)
                for cid in range(args.num_customers)
            ]
        )
        _settle_round(rnd, choices, strategies, state, args.base_ticket)


def main() -> None:
    parser = argparse.ArgumentParser(description="CompeteAI mini procedural simulation")
    parser.add_argument("--num_restaurants", type=int, default=2)
    parser.add_argument("--num_customers", type=int, default=5)
    parser.add_argument("--num_rounds", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--simulate_time", type=float, default=6.0)
    parser.add_argument("--api_model", type=str, default="deepseek/deepseek-chat")
    parser.add_argument("--base_ticket", type=float, default=10.0)
    args = parser.parse_args()
    asyncio.run(run_sim(args))


if __name__ == "__main__":
    main()
