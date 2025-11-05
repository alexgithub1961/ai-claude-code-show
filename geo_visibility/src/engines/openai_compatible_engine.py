"""
OpenAI-compatible API engine for DeepSeek, Grok, etc.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time
import httpx

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class OpenAICompatibleEngine(AIEngineBase):
    """Generic OpenAI-compatible API engine."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "",
        engine_type: AIEngine = AIEngine.DEEPSEEK,
        model: str = "deepseek-chat",
        **kwargs
    ):
        """
        Initialize OpenAI-compatible engine.

        Args:
            api_key: API key
            base_url: Base URL for the API
            engine_type: Engine type identifier
            model: Model name
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = base_url
        self.engine_type_value = engine_type
        self.model = model

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return self.engine_type_value

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query the OpenAI-compatible API.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        start_time = time.time()
        metadata = {"model": self.model, "base_url": self.base_url}

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
                            {"role": "system", "content": "You are a helpful assistant."},
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
