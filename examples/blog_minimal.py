#!/usr/bin/env python3
"""
Minimal blog-friendly example: crush a single web page with LangGraph.

Requires:
  pip install -e .
  pip install requests beautifulsoup4 openai  # openai optional

Env:
  export TOKENCRUSH_API_KEY="your-tokencrush-api-key"
  # optional overrides
  # export TC_BASE_URL="http://localhost:8000"
  # export OPENAI_API_KEY="your-openai-api-key"
  # export OPENAI_MODEL="gpt-4o-mini"
"""

import os
import sys
from typing import Optional

import requests
from bs4 import BeautifulSoup

try:
    from openai import OpenAI  # optional
except Exception:  # pragma: no cover - optional dep
    OpenAI = None  # type: ignore

from tokencrush_langraph import build_tokencrush_graph


def fetch_text(url: str) -> str:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return "\n".join(t.strip() for t in soup.stripped_strings)


def maybe_answer_with_openai(context: str, question: str) -> Optional[str]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise, helpful assistant."},
            {
                "role": "user",
                "content": (
                    "Answer the following question based only on the provided context.\n\n"
                    f"Context:\n{context}\n\n"
                    f"Question: {question}"
                ),
            },
        ],
        temperature=0.2,
    )
    return completion.choices[0].message.content if completion.choices else None


def main() -> int:
    api_key = os.environ.get("TOKENCRUSH_API_KEY")
    if not api_key:
        print("Please set TOKENCRUSH_API_KEY", file=sys.stderr)
        return 1

    base_url = os.environ.get("TC_BASE_URL")
    url = os.environ.get(
        "BLOG_URL",
        "https://epoch.ai/blog/can-ai-scaling-continue-through-2030",
    )
    question = os.environ.get(
        "BLOG_QUESTION",
        "Will AI plateau or will progress continue?",
    )

    print("Fetching page...")
    text = fetch_text(url)

    print("Building LangGraph app and crushing content...")
    app = build_tokencrush_graph(api_key=api_key, base_url=base_url, fallback_to_input=True)
    result = app.invoke({"prompt": text}) or {}
    crush = result.get("crush", {})

    optimized = crush.get("optimized_prompt", text)
    orig_len = len(text)
    new_len = len(optimized)
    pct = crush.get("percentage_reduction")

    print("\n--- TokenCrush Result ---")
    print(f"Original length:  {orig_len} chars")
    print(f"Optimized length: {new_len} chars")
    if pct is not None:
        print(f"Reported reduction: ~{pct}%")

    print("\nPreview (first 600 chars):\n")
    print(optimized[:600] + ("..." if len(optimized) > 600 else ""))

    # Optional: ask an LLM using optimized context
    answer = maybe_answer_with_openai(optimized, question)
    if answer:
        print("\n--- LLM Answer ---\n")
        print(answer)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


