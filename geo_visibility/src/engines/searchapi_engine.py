"""
SearchAPI integration for Chrome AI Summary and other AI overviews.
SearchAPI provides access to Google's AI Overview/Summary results.
"""
import asyncio
from datetime import datetime
from typing import Optional
import time
import httpx

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class SearchAPIEngine(AIEngineBase):
    """
    SearchAPI integration for Google AI Overview (Chrome AI Summary).

    SearchAPI provides programmatic access to Google's AI-powered search results,
    including the AI Overview (formerly known as SGE - Search Generative Experience).

    Get API key from: https://www.searchapi.io/
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize SearchAPI engine.

        Args:
            api_key: SearchAPI API key
            **kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.base_url = "https://www.searchapi.io/api/v1/search"
        self.engine_name = kwargs.get("engine_name", "google_ai_overview")

    def get_engine_type(self) -> AIEngine:
        """Get the engine type."""
        return AIEngine.CHROME_AI

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query Google AI Overview via SearchAPI.

        Args:
            prompt: The query/prompt to send
            **kwargs: Additional parameters

        Returns:
            EngineResponse object
        """
        start_time = time.time()
        metadata = {
            "provider": "searchapi",
            "engine": self.engine_name
        }

        if not self.is_configured():
            return EngineResponse(
                engine=self.get_engine_type(),
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error="SearchAPI not configured. Get API key from https://www.searchapi.io/",
                latency_ms=0,
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.base_url,
                    params={
                        "q": prompt,
                        "api_key": self.api_key,
                        "engine": "google",
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
                        error=f"SearchAPI error: {response.status_code} - {response.text}",
                        latency_ms=latency_ms,
                    )

                data = response.json()

                # Extract AI Overview from SearchAPI response
                ai_overview = data.get("ai_overview", {})

                if ai_overview and isinstance(ai_overview, dict):
                    # Get the AI-generated summary
                    response_text = ai_overview.get("text", "")

                    # If no text, try to get it from snippets
                    if not response_text and "snippets" in ai_overview:
                        snippets = ai_overview.get("snippets", [])
                        response_text = "\n\n".join(
                            snippet.get("text", "") for snippet in snippets if snippet.get("text")
                        )

                    metadata.update({
                        "has_ai_overview": True,
                        "sources_count": len(ai_overview.get("sources", [])),
                        "snippets_count": len(ai_overview.get("snippets", [])),
                    })
                else:
                    # No AI Overview available for this query
                    # Fall back to organic results summary
                    organic_results = data.get("organic_results", [])
                    if organic_results:
                        # Create a summary from top organic results
                        summaries = []
                        for result in organic_results[:3]:
                            title = result.get("title", "")
                            snippet = result.get("snippet", "")
                            if title and snippet:
                                summaries.append(f"{title}: {snippet}")

                        response_text = "\n\n".join(summaries) if summaries else ""
                        metadata.update({
                            "has_ai_overview": False,
                            "fallback": "organic_results",
                            "organic_count": len(organic_results),
                        })
                    else:
                        response_text = ""
                        metadata["has_ai_overview"] = False

                if not response_text:
                    return EngineResponse(
                        engine=self.get_engine_type(),
                        query=prompt,
                        response_text="",
                        timestamp=datetime.now(),
                        metadata=metadata,
                        error="No AI Overview or organic results found",
                        latency_ms=latency_ms,
                    )

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
