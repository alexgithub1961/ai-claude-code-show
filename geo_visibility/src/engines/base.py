"""
Base interface for AI engines.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from ..config import AIEngine


@dataclass
class EngineResponse:
    """Response from an AI engine."""
    engine: AIEngine
    query: str
    response_text: str
    timestamp: datetime
    metadata: Dict[str, Any]
    error: Optional[str] = None
    latency_ms: Optional[float] = None


class AIEngineBase(ABC):
    """Base class for AI engine interfaces."""

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the engine.

        Args:
            api_key: API key for the engine
            **kwargs: Additional configuration
        """
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Send a query to the AI engine.

        Args:
            prompt: The query/prompt to send
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        pass

    @abstractmethod
    def get_engine_type(self) -> AIEngine:
        """
        Get the engine type.

        Returns:
            AIEngine enum value
        """
        pass

    def is_configured(self) -> bool:
        """
        Check if the engine is properly configured.

        Returns:
            True if configured, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0

    async def batch_query(self, prompts: list[str], **kwargs) -> list[EngineResponse]:
        """
        Send multiple queries to the engine.

        Args:
            prompts: List of prompts to send
            **kwargs: Additional parameters

        Returns:
            List of EngineResponse objects
        """
        responses = []
        for prompt in prompts:
            response = await self.query(prompt, **kwargs)
            responses.append(response)
        return responses
