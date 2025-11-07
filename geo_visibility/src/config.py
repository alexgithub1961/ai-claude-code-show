"""
Configuration and data models for GEO Visibility Assessment.
"""
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class BusinessArea(str, Enum):
    """Business areas for First Line Software."""
    GEN_AI = "gen_ai_managed_services"
    DIGITAL_PUBLISHING = "digital_publishing_dx"


class AIEngine(str, Enum):
    """Supported AI engines for visibility assessment."""
    CHROME_AI = "chrome_ai_summary"
    PERPLEXITY = "perplexity"
    CHATGPT = "chatgpt"
    DEEPSEEK = "deepseek"
    GROK = "grok"
    CLAUDE = "claude"  # Optional for comparison


class QueryCategory(str, Enum):
    """Categories of test queries."""
    DIRECT = "direct"  # Direct company name queries
    SERVICE = "service"  # Service-specific queries
    COMPARISON = "comparison"  # Competitive queries
    PROBLEM_SOLVING = "problem_solving"  # Solution-seeking queries
    INDUSTRY = "industry"  # Industry/domain queries


class CompanyConfig(BaseModel):
    """Configuration for the company being assessed."""
    name: str = "First Line Software"
    aliases: List[str] = ["First Line", "FLS", "First Line Software Inc"]
    website: str = "https://firstlinesoftware.com"
    business_areas: List[BusinessArea] = [
        BusinessArea.GEN_AI,
        BusinessArea.DIGITAL_PUBLISHING
    ]


class VisibilityScore(BaseModel):
    """Visibility score for a single query result."""
    engine: AIEngine
    query: str
    query_category: QueryCategory
    business_area: BusinessArea
    timestamp: datetime = Field(default_factory=datetime.now)

    # Visibility metrics
    is_mentioned: bool = False
    mention_position: Optional[int] = None  # Position in response (1-based)
    mention_count: int = 0
    prominence_score: float = 0.0  # 0-1 scale
    context_quality: float = 0.0  # 0-1 scale

    # Response metadata
    response_text: str = ""
    total_companies_mentioned: int = 0
    company_rank: Optional[int] = None  # Rank among mentioned companies

    # Analysis
    sentiment: Literal["positive", "neutral", "negative", "unknown"] = "unknown"
    key_phrases: List[str] = []
    competitor_mentions: List[str] = []


class QuerySet(BaseModel):
    """A set of test queries for a business area."""
    business_area: BusinessArea
    category: QueryCategory
    queries: List[str]
    metadata: Dict[str, str] = {}


class AssessmentReport(BaseModel):
    """Complete assessment report."""
    company: str
    generated_at: datetime = Field(default_factory=datetime.now)
    business_areas: List[BusinessArea]
    engines_tested: List[AIEngine]

    total_queries: int
    total_mentions: int
    overall_visibility_score: float  # 0-100

    # Per-engine breakdown
    engine_scores: Dict[AIEngine, float] = {}

    # Per-business area breakdown
    business_area_scores: Dict[BusinessArea, float] = {}

    # Detailed results
    results: List[VisibilityScore] = []

    # Insights
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []


class EngineCredentials(BaseModel):
    """API credentials for AI engines."""
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None
    searchapi_api_key: Optional[str] = None  # For Google AI Overview via SearchAPI
