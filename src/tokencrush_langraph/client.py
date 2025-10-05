from __future__ import annotations

from typing import Optional

import httpx
from pydantic import BaseModel, Field, field_validator


class CrushRequest(BaseModel):
    prompt: str = Field(..., description="The text prompt to be optimized")

    @field_validator("prompt")
    @classmethod
    def _non_empty(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("prompt must be a non-empty string")
        return v


class CrushResponse(BaseModel):
    optimized_prompt: str
    input_tokens: int
    output_tokens: int
    percentage_reduction: float


class TokenCrushClient:
    """Thin client for TokenCrush /v1/crush."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str | None = None,
        timeout: float | httpx.Timeout | None = 30.0,
        http_client: httpx.Client | None = None,
    ):
        if not api_key:
            raise ValueError("api_key is required")
        self.api_key = api_key
        self.base_url = (base_url or "https://api.tokencrush.ai").rstrip("/")
        self._client = http_client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    def crush(self, request: CrushRequest | dict, *, timeout: Optional[float] = None) -> CrushResponse:
        if not isinstance(request, CrushRequest):
            request = CrushRequest(**request)
        url = f"{self.base_url}/v1/crush"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        resp = self._client.post(url, headers=headers, json=request.model_dump(), timeout=timeout)
        if resp.status_code // 100 != 2:
            text = resp.text or resp.reason_phrase
            raise httpx.HTTPStatusError(
                f"TokenCrush API error ({resp.status_code}): {text}",
                request=resp.request,
                response=resp,
            )
        data = resp.json()
        return CrushResponse(**data)


