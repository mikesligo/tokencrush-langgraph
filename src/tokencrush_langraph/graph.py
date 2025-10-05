from __future__ import annotations

from typing import Optional, TypedDict

from langgraph.graph import StateGraph, END
from .client import TokenCrushClient, CrushResponse


class CrushState(TypedDict, total=False):
    # Input
    prompt: str
    # Output
    crush: dict  # dict form of CrushResponse
    error: str


def build_tokencrush_graph(
    api_key: str,
    *,
    base_url: Optional[str] = None,
    fallback_to_input: bool = False,
):
    """
    Build and compile a LangGraph app that:
      - takes {"prompt": str}
      - calls TokenCrush
      - returns {"crush": dict, "error"?: str}
    """
    client = TokenCrushClient(api_key=api_key, base_url=base_url)

    def crush_node(state: CrushState) -> CrushState:
        prompt = state.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("prompt is required and must be a non-empty string")

        try:
            res: CrushResponse = client.crush({"prompt": prompt})
            return {"crush": res.model_dump()}
        except Exception as e:
            if fallback_to_input:
                # Simple heuristic token estimate (4 chars/token)
                length = max(1, round(len(prompt.strip()) / 4))
                fallback_res = CrushResponse(
                    optimized_prompt=prompt,
                    input_tokens=length,
                    output_tokens=length,
                    percentage_reduction=0.0,
                )
                return {"crush": fallback_res.model_dump(), "error": str(e)}
            raise

    graph = StateGraph(CrushState)
    graph.add_node("crush", crush_node)
    graph.set_entry_point("crush")
    graph.add_edge("crush", END)

    app = graph.compile()
    return app


def crush(
    api_key: str,
    prompt: str,
    *,
    base_url: Optional[str] = None,
    fallback_to_input: bool = False,
) -> dict:
    """
    Convenience one-shot function.
    Returns the compiled graph invocation output: {"crush": {...}, "error"?: str}
    """
    app = build_tokencrush_graph(
        api_key=api_key,
        base_url=base_url,
        fallback_to_input=fallback_to_input,
    )
    return app.invoke({"prompt": prompt})


