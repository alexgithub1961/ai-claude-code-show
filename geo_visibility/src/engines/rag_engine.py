"""
RAG-based AI Engine with Web Search Grounding
Implements Retrieval-Augmented Generation following best practices.

This engine:
1. Performs web search for the query
2. Retrieves relevant search results
3. Grounds LLM response with search data
4. Generates contextually accurate responses
"""
import asyncio
from datetime import datetime
from typing import Optional, List, Dict
import time
import httpx
from openai import AsyncOpenAI

from .base import AIEngineBase, EngineResponse
from ..config import AIEngine


class RAGSearchEngine(AIEngineBase):
    """
    RAG-based search engine that grounds AI responses with web search results.

    Best Practices Implemented:
    - Retrieval before generation (RAG core principle)
    - Multiple diverse sources
    - Source citation
    - Factual grounding
    - Recency weighting
    - Domain authority consideration
    """

    def __init__(
        self,
        openai_api_key: str,
        search_api_key: str,
        target_engine: AIEngine = AIEngine.PERPLEXITY,
        max_search_results: int = 5,
        **kwargs
    ):
        """
        Initialize RAG search engine.

        Args:
            openai_api_key: OpenAI API key for LLM
            search_api_key: SearchAPI key for web search
            target_engine: Which AI engine to simulate
            max_search_results: Number of search results to include (default 5)
        """
        super().__init__(openai_api_key, **kwargs)
        self.search_api_key = search_api_key
        self.target_engine = target_engine
        self.max_search_results = max_search_results
        self.openai_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key else None
        self.search_base_url = "https://www.searchapi.io/api/v1/search"

    def is_configured(self) -> bool:
        """Check if both OpenAI and SearchAPI are configured."""
        return bool(self.api_key and self.search_api_key and self.openai_client)

    def get_engine_type(self) -> AIEngine:
        """Get the target engine type being simulated."""
        return self.target_engine

    async def _perform_web_search(self, query: str) -> Dict:
        """
        Perform web search and retrieve results.

        Args:
            query: Search query

        Returns:
            Dict with search results
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.search_base_url,
                params={
                    "q": query,
                    "api_key": self.search_api_key,
                    "engine": "google",
                    "num": 10,  # Get more results for diversity
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                return {"error": f"Search API error: {response.status_code}"}

            return response.json()

    def _extract_search_context(self, search_data: Dict) -> str:
        """
        Extract and format search results for RAG context.

        Best Practices:
        - Include title, snippet, and source
        - Maintain source attribution
        - Prioritize authoritative domains
        - Include diverse perspectives

        Args:
            search_data: Raw search API response

        Returns:
            Formatted context string
        """
        organic_results = search_data.get("organic_results", [])

        if not organic_results:
            return ""

        # Take top N results
        top_results = organic_results[: self.max_search_results]

        # Format as numbered sources
        context_parts = []
        for i, result in enumerate(top_results, 1):
            title = result.get("title", "")
            snippet = result.get("snippet", "")
            domain = result.get("domain", result.get("link", ""))

            if title and snippet:
                context_parts.append(
                    f"[{i}] {title}\n"
                    f"Source: {domain}\n"
                    f"{snippet}\n"
                )

        return "\n".join(context_parts)

    def _get_system_prompt(self, search_context: str) -> str:
        """
        Generate system prompt for RAG-grounded response.

        Best Practices:
        - Instruct to use provided sources
        - Encourage citation
        - Emphasize accuracy over speculation
        - Maintain target engine's style

        Args:
            search_context: Formatted search results

        Returns:
            System prompt string
        """
        # Engine-specific styles
        style_instructions = {
            AIEngine.PERPLEXITY: (
                "Provide a comprehensive, well-cited answer similar to Perplexity AI. "
                "Include inline citations [1], [2], etc. for specific facts. "
                "Be academic and thorough."
            ),
            AIEngine.CHATGPT: (
                "Provide a helpful, conversational answer similar to ChatGPT. "
                "Be clear and accessible. Mention sources naturally in the text."
            ),
            AIEngine.CHROME_AI: (
                "Provide a concise, informative summary similar to Google AI Overview. "
                "Focus on answering the question directly. Include key facts."
            ),
            AIEngine.DEEPSEEK: (
                "Provide a detailed, technical answer. "
                "Be precise and include technical specifics when relevant."
            ),
            AIEngine.GROK: (
                "Provide a direct, no-nonsense answer. "
                "Be concise but accurate. Focus on practical information."
            ),
        }

        style = style_instructions.get(
            self.target_engine,
            "Provide a helpful, accurate answer based on the search results."
        )

        return f"""You are a helpful AI assistant that answers questions using web search results.

IMPORTANT INSTRUCTIONS:
1. Base your answer ONLY on the provided search results below
2. DO NOT use your training data knowledge if it conflicts with search results
3. Cite sources using [1], [2], etc. format
4. If search results don't contain the answer, say so
5. Prioritize recent and authoritative sources
6. {style}

SEARCH RESULTS:
{search_context}

Remember: Ground your response in the search results above. Use citations."""

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Query using RAG approach: Search -> Retrieve -> Generate.

        Args:
            prompt: The user query
            **kwargs: Additional parameters (model, max_tokens, temperature)

        Returns:
            EngineResponse with grounded answer
        """
        start_time = time.time()
        metadata = {
            "provider": "rag_search",
            "target_engine": self.target_engine.value,
            "rag_enabled": True,
        }

        if not self.is_configured():
            return EngineResponse(
                engine=self.target_engine,
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error="RAG engine not configured. Need both OpenAI and SearchAPI keys.",
                latency_ms=0,
            )

        try:
            # Step 1: Retrieve - Perform web search
            search_data = await self._perform_web_search(prompt)

            if "error" in search_data:
                latency_ms = (time.time() - start_time) * 1000
                return EngineResponse(
                    engine=self.target_engine,
                    query=prompt,
                    response_text="",
                    timestamp=datetime.now(),
                    metadata=metadata,
                    error=search_data["error"],
                    latency_ms=latency_ms,
                )

            # Step 2: Extract context from search results
            search_context = self._extract_search_context(search_data)

            if not search_context:
                latency_ms = (time.time() - start_time) * 1000
                return EngineResponse(
                    engine=self.target_engine,
                    query=prompt,
                    response_text="",
                    timestamp=datetime.now(),
                    metadata={**metadata, "sources_found": 0},
                    error="No search results found to ground response",
                    latency_ms=latency_ms,
                )

            metadata["sources_found"] = len(search_data.get("organic_results", []))
            metadata["sources_used"] = min(self.max_search_results, metadata["sources_found"])

            # Step 3: Generate - LLM response grounded in search results
            system_prompt = self._get_system_prompt(search_context)

            model = kwargs.get("model", "gpt-4o-mini")
            max_tokens = kwargs.get("max_tokens", 500)
            temperature = kwargs.get("temperature", 0.7)

            completion = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
            )

            response_text = completion.choices[0].message.content
            latency_ms = (time.time() - start_time) * 1000

            metadata.update({
                "model": model,
                "finish_reason": completion.choices[0].finish_reason,
                "tokens_used": completion.usage.total_tokens if completion.usage else None,
            })

            return EngineResponse(
                engine=self.target_engine,
                query=prompt,
                response_text=response_text,
                timestamp=datetime.now(),
                metadata=metadata,
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return EngineResponse(
                engine=self.target_engine,
                query=prompt,
                response_text="",
                timestamp=datetime.now(),
                metadata=metadata,
                error=str(e),
                latency_ms=latency_ms,
            )


class HybridRAGEngine(RAGSearchEngine):
    """
    Hybrid approach: Try real API first, fall back to RAG if unavailable.

    Best for: Getting most accurate results when real API available,
    but maintaining coverage when it's not.
    """

    def __init__(
        self,
        openai_api_key: str,
        search_api_key: str,
        target_engine: AIEngine,
        real_engine: Optional[AIEngineBase] = None,
        **kwargs
    ):
        """
        Initialize hybrid engine.

        Args:
            openai_api_key: OpenAI API key
            search_api_key: SearchAPI key
            target_engine: Target engine to simulate
            real_engine: Actual engine implementation (if available)
        """
        super().__init__(openai_api_key, search_api_key, target_engine, **kwargs)
        self.real_engine = real_engine

    async def query(self, prompt: str, **kwargs) -> EngineResponse:
        """
        Try real engine first, fall back to RAG.

        Args:
            prompt: User query
            **kwargs: Additional parameters

        Returns:
            EngineResponse from real engine or RAG fallback
        """
        # Try real engine first
        if self.real_engine and self.real_engine.is_configured():
            try:
                response = await self.real_engine.query(prompt, **kwargs)
                if not response.error:
                    response.metadata["rag_fallback"] = False
                    return response
            except Exception:
                pass  # Fall through to RAG

        # Fall back to RAG
        response = await super().query(prompt, **kwargs)
        response.metadata["rag_fallback"] = True
        return response
