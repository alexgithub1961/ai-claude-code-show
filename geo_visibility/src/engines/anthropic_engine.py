"""
Anthropic Claude engine implementation.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class ClaudeEngine(AIEngineBase):
    """Anthropic Claude engine."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        """
        Initialize Claude engine.

        Args:
            api_key: Anthropic API key
            model: Model to use
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = None

        if self.is_configured():
            try:
                from anthropic import AsyncAnthropic
                self.client = AsyncAnthropic(api_key=api_key)
            except ImportError:
                print("Warning: anthropic package not installed. Install with: pip install anthropic")

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return AIEngine.CLAUDE

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query Claude.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        start_time = time.time()
        metadata = {"model": self.model}

        if not self.is_configured() or self.client is None:
            return EngineResponse(
                engine=self.get_engine_type(),
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error="Engine not configured or Anthropic package not installed",
                latency_ms=0,
            )

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
            )

            latency_ms = (time.time() - start_time) * 1000
            response_text = response.content[0].text

            metadata.update({
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "stop_reason": response.stop_reason,
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
