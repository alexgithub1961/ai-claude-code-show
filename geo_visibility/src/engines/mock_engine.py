"""
Mock engine for testing and engines without public APIs.
"""
from datetime import datetime
from typing import Optional
import time

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class MockEngine(AIEngineBase):
    """
    Mock engine for testing or engines without public APIs.
    Used for Chrome AI Summary which requires manual testing.
    """

    def __init__(self, engine_type: AIEngine = AIEngine.CHROME_AI, **kwargs):
        """
        Initialize mock engine.

        Args:
            engine_type: Engine type to mock
            **kwargs: Additional configuration
        """
        super().__init__(api_key="mock", **kwargs)
        self.engine_type_value = engine_type

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return self.engine_type_value

    def is_configured(self) -> bool:
        """Mock engine is always configured."""
        return True

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Mock query - returns a placeholder response.

        Args:
            prompt: The query prompt
            **kwargs: Additional parameters

        Returns:
            EngineResponse object with mock data
        """
        start_time = time.time()

        # Simulate some processing time
        await asyncio.sleep(0.1)

        latency_ms = (time.time() - start_time) * 1000

        mock_response = f"""
[MOCK RESPONSE - {self.engine_type_value.value}]

This is a placeholder response for testing purposes.
For actual results with {self.engine_type_value.value}, you need to:
1. Manually query {self.engine_type_value.value} with: "{prompt}"
2. Copy the response
3. Import the response into the system

You can use the import functionality to add real results.
"""

        return EngineResponse(
            engine=self.get_engine_type(),
            query=prompt,
            response_text=mock_response.strip(),
            timestamp=datetime.now(),
            metadata={
                "is_mock": True,
                "engine": self.engine_type_value.value,
            },
            latency_ms=latency_ms,
        )


import asyncio  # Import at top if not already there
