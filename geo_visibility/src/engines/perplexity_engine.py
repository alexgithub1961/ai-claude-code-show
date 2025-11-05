"""
Perplexity AI engine implementation.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time
import httpx

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class PerplexityEngine(AIEngineBase):
    """Perplexity AI engine."""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.1-sonar-large-128k-online", **kwargs):
        """
        Initialize Perplexity engine.

        Args:
            api_key: Perplexity API key
            model: Model to use
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.base_url = "https://api.perplexity.ai"

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return AIEngine.PERPLEXITY

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query Perplexity AI.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        start_time = time.time()
        metadata = {"model": self.model}

        if not self.is_configured():
            return EngineResponse(
                engine=self.get_engine_type(),
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error="Engine not configured",
                latency_ms=0,
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "Be precise and informative."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": kwargs.get("temperature", 0.7),
                        "max_tokens": kwargs.get("max_tokens", 1000),
                    },
                    timeout=30.0,
                )

                latency_ms = (time.time() - start_time) * 1000

                if response.status_code != 200:
                    return EngineResponse(
                        engine=self.get_engine_type(),
                        query=prompt,
                        response_text="",
                        timestamp=datetime.now(),
                        metadata=metadata,
                        error=f"API error: {response.status_code} - {response.text}",
                        latency_ms=latency_ms,
                    )

                data = response.json()
                response_text = data["choices"][0]["message"]["content"]

                metadata.update({
                    "usage": data.get("usage", {}),
                    "citations": data.get("citations", []),
                })

                return EngineResponse(
                    engine=self.get_engine_type(),
                    query=prompt,
                    response_text=response_text,
                    timestamp=datetime.now(),
                    metadata=metadata,
                    latency_ms=latency_ms,
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return EngineResponse(
                engine=self.get_engine_type(),
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error=str(e),
                latency_ms=latency_ms,
            )
