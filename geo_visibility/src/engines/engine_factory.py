"""
Factory for creating AI engine instances.
"""
from typing import Optional, Dict, Any

from .base import AIEngineBase
from .openai_engine import ChatGPTEngine
from .perplexity_engine import PerplexityEngine
from .anthropic_engine import ClaudeEngine
from ..config import AIEngine, EngineCredentials


class EngineFactory:
    """Factory for creating AI engine instances."""

    @staticmethod
    def create_engine(
        engine_type: AIEngine,
        credentials: Optional[EngineCredentials] = None,
        **kwargs
    ) -> AIEngineBase:
        """
        Create an AI engine instance.

        Args:
            engine_type: Type of engine to create
            credentials: API credentials
            **kwargs: Additional configuration

        Returns:
            AIEngineBase instance

        Raises:
            ValueError: If engine type is not supported
        """
        if credentials is None:
            credentials = EngineCredentials()

        if engine_type == AIEngine.CHATGPT:
            return ChatGPTEngine(
                api_key=credentials.openai_api_key,
                **kwargs
            )
        elif engine_type == AIEngine.PERPLEXITY:
            return PerplexityEngine(
                api_key=credentials.perplexity_api_key,
                **kwargs
            )
        elif engine_type == AIEngine.CLAUDE:
            return ClaudeEngine(
                api_key=credentials.anthropic_api_key,
                **kwargs
            )
        elif engine_type == AIEngine.DEEPSEEK:
            # DeepSeek - can use OpenAI-compatible API
            from .openai_compatible_engine import OpenAICompatibleEngine
            return OpenAICompatibleEngine(
                api_key=credentials.deepseek_api_key,
                base_url="https://api.deepseek.com/v1",
                engine_type=AIEngine.DEEPSEEK,
                model="deepseek-chat",
                **kwargs
            )
        elif engine_type == AIEngine.GROK:
            # Grok (xAI) - uses OpenAI-compatible API
            from .openai_compatible_engine import OpenAICompatibleEngine
            return OpenAICompatibleEngine(
                api_key=credentials.grok_api_key,
                base_url="https://api.x.ai/v1",
                engine_type=AIEngine.GROK,
                model="grok-beta",
                **kwargs
            )
        elif engine_type == AIEngine.CHROME_AI:
            # Chrome AI Summary - no public API, would need manual testing
            from .mock_engine import MockEngine
            return MockEngine(engine_type=AIEngine.CHROME_AI)
        else:
            raise ValueError(f"Unsupported engine type: {engine_type}")

    @staticmethod
    def create_all_engines(
        credentials: Optional[EngineCredentials] = None,
        exclude: Optional[list[AIEngine]] = None,
    ) -> Dict[AIEngine, AIEngineBase]:
        """
        Create instances of all available engines.

        Args:
            credentials: API credentials
            exclude: List of engines to exclude

        Returns:
            Dictionary mapping engine types to instances
        """
        if exclude is None:
            exclude = []

        engines = {}
        for engine_type in AIEngine:
            if engine_type not in exclude:
                try:
                    engine = EngineFactory.create_engine(engine_type, credentials)
                    if engine.is_configured() or engine_type == AIEngine.CHROME_AI:
                        engines[engine_type] = engine
                except Exception as e:
                    print(f"Warning: Could not create {engine_type.value} engine: {e}")

        return engines
