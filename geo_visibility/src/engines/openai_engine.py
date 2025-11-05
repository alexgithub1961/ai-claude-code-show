"""
OpenAI ChatGPT engine implementation.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class ChatGPTEngine(AIEngineBase):
    """OpenAI ChatGPT engine."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o", **kwargs):
        """
        Initialize ChatGPT engine.

        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4o)
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        self.client = None

        if self.is_configured():
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
            except ImportError:
                print("Warning: openai package not installed. Install with: pip install openai")

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return AIEngine.CHATGPT

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query ChatGPT.

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
                error="Engine not configured or OpenAI package not installed",
                latency_ms=0,
            )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant providing comprehensive answers about companies and their services."},
                    {"role": "user", "content": prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
            )

            latency_ms = (time.time() - start_time) * 1000
            response_text = response.choices[0].message.content

            metadata.update({
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
                "finish_reason": response.choices[0].finish_reason,
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
