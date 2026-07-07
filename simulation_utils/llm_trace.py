"""Shared helpers for paper-to-simulation procedural runners."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

from openai import AsyncOpenAI


def make_client() -> AsyncOpenAI:
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
    base = os.getenv("OPENROUTER_API_BASE") or os.getenv("OPENAI_BASE_URL") or "https://openrouter.ai/api/v1"
    if not key:
        raise RuntimeError("Missing OPENROUTER_API_KEY or OPENAI_API_KEY")
    return AsyncOpenAI(api_key=key, base_url=base)


def emit_trace(
    event: str,
    data: dict[str, Any],
    *,
    model: str,
    sim_time: float = 0.0,
) -> None:
    print(json.dumps({"time": sim_time, "model": model, "event": event, "data": data}, ensure_ascii=False))


async def llm_text(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    *,
    max_tokens: int = 8,
    temperature: float = 0.0,
) -> str:
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"[warn] LLM call failed: {exc}", file=sys.stderr)
        return ""


async def llm_json(
    client: AsyncOpenAI,
    model: str,
    prompt: str,
    *,
    max_tokens: int = 120,
    temperature: float = 0.3,
) -> dict[str, Any]:
    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = (resp.choices[0].message.content or "").strip()
        if not content:
            return {}
        return json.loads(content)
    except Exception as exc:
        print(f"[warn] LLM call failed: {exc}", file=sys.stderr)
        return {}
