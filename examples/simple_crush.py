#!/usr/bin/env python3
import os
from tokencrush_langraph import build_tokencrush_graph, crush

def main():
    api_key = os.environ.get("TOKENCRUSH_API_KEY")
    if not api_key:
        raise SystemExit("Please set TOKENCRUSH_API_KEY")

    prompt = """Mercedes’ George Russell, who wins the Singapore Grand Prix from pole position: "It feels amazing especially after what happened a couple of years ago, that was a bit of a missed opportunity but we more than made up for it today."""
    # Option A: convenience function
    out = crush(api_key, prompt)
    print("One-shot:", out)

    # Option B: reusable compiled graph
    app = build_tokencrush_graph(api_key, fallback_to_input=True)
    res = app.invoke({"prompt": prompt})
    print("Graph invoke:", res)

if __name__ == "__main__":
    main()


