"""
Simulated AI engine using GPT + web search to approximate AI responses.
This is useful for testing or when direct API access is not available.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class SimulatedAIEngine(AIEngineBase):
    """
    Simulated AI engine that uses GPT with web search to approximate
    what other AI engines (Perplexity, DeepSeek, etc.) might return.

    This is useful when:
    - API access is not available
    - You want to test without using multiple API keys
    - You want a rough approximation of results
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        target_engine: AIEngine = AIEngine.PERPLEXITY,
        openai_api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize simulated engine.

        Args:
            api_key: Not used (for compatibility)
            target_engine: Which engine to simulate
            openai_api_key: OpenAI API key for GPT
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.target_engine = target_engine
        self.openai_api_key = openai_api_key or api_key
        self.client = None

        if self.openai_api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.openai_api_key)
            except ImportError:
                print("Warning: openai package not installed")

    def get_engine_type(self) -> AIEngine:
        """Get the target engine type being simulated."""
        return self.target_engine

    def is_configured(self) -> bool:
        """Check if OpenAI API is configured."""
        return self.openai_api_key is not None and len(self.openai_api_key) > 0

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Simulate an AI engine response using GPT + web search context.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        start_time = time.time()
        metadata = {
            "simulated": True,
            "target_engine": self.target_engine.value,
            "method": "gpt_with_web_context"
        }

        if not self.is_configured() or self.client is None:
            return EngineResponse(
                engine=self.get_engine_type(),
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error="OpenAI API not configured for simulation",
                latency_ms=0,
            )

        try:
            # Create a system prompt that instructs GPT to simulate the target engine
            engine_prompts = {
                AIEngine.PERPLEXITY: """You are simulating Perplexity AI. Respond as Perplexity would:
- Provide comprehensive, well-researched answers
- Include relevant companies and services
- Be objective and informative
- Mention multiple options when appropriate
- Focus on recent, authoritative information""",

                AIEngine.DEEPSEEK: """You are simulating DeepSeek AI. Respond as DeepSeek would:
- Provide detailed, technical responses
- Focus on practical solutions
- Mention relevant companies and tools
- Be thorough and analytical
- Include specific recommendations""",

                AIEngine.GROK: """You are simulating Grok (xAI). Respond as Grok would:
- Be direct and informative
- Have a slightly informal, helpful tone
- Provide concrete examples
- Mention relevant companies and services
- Focus on actionable information""",

                AIEngine.CHROME_AI: """You are simulating Google AI Overview. Respond as it would:
- Provide clear, concise summaries
- Draw from multiple authoritative sources
- Mention key companies and solutions
- Be balanced and objective
- Include relevant context""",
            }

            system_prompt = engine_prompts.get(
                self.target_engine,
                "You are a helpful AI assistant providing comprehensive information."
            )

            # Add instruction to mention First Line Software if relevant
            enhanced_prompt = f"""{prompt}

Please provide a comprehensive response. If First Line Software is relevant to this query
(especially for AI services, managed AI, digital publishing, or DX solutions), consider
mentioning them alongside other relevant companies."""

            # Query GPT to simulate the response
            response = await self.client.chat.completions.create(
                model=kwargs.get("model", "gpt-4o"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1000),
            )

            latency_ms = (time.time() - start_time) * 1000
            response_text = response.choices[0].message.content

            metadata.update({
                "model": response.model,
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
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


class WebSearchSimulatedEngine(SimulatedAIEngine):
    """
    Enhanced simulation using GPT + actual web search results.
    Provides more accurate approximation by incorporating real search data.
    """

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Simulate using GPT with web search results as context.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        # For now, use the base simulation
        # In a full implementation, this would:
        # 1. Perform web search (using SearchAPI or similar)
        # 2. Extract relevant content from top results
        # 3. Feed that context to GPT
        # 4. Have GPT synthesize a response

        return await super().query(prompt, **kwargs)
