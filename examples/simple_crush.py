#!/usr/bin/env python3
import os
from tokencrush_langraph import build_tokencrush_graph, crush

def main():
    api_key = os.environ.get("TOKENCRUSH_API_KEY")
    if not api_key:
        raise SystemExit("Please set TOKENCRUSH_API_KEY")

    # Option A: convenience function
    out = crush(api_key, "Summarize this text in plain English.")
    print("One-shot:", out)

    # Option B: reusable compiled graph
    app = build_tokencrush_graph(api_key, fallback_to_input=True)
    res = app.invoke({"prompt": "Explain transformers to a high-school student."})
    print("Graph invoke:", res)

if __name__ == "__main__":
    main()


