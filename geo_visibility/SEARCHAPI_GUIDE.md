# SearchAPI Integration Guide

## Overview

This tool now supports **SearchAPI** for accessing Google AI Overview (Chrome AI Summary) results programmatically.

SearchAPI provides access to Google's AI-powered search results, including the AI Overview feature (formerly SGE - Search Generative Experience), which is what users see when searching on Google with AI features enabled.

## Why Use SearchAPI?

**Problem**: Google's AI Overview (Chrome AI Summary) doesn't have a public API.

**Solution**: SearchAPI provides programmatic access to Google's AI search results, including:
- AI Overview/Summary responses
- Related questions
- Source citations
- Organic search results

## Getting Started

### 1. Get a SearchAPI Key

Visit: https://www.searchapi.io/

- Sign up for a free account
- Get your API key from the dashboard
- Free tier includes 100 searches/month

### 2. Add to .env

```bash
SEARCHAPI_API_KEY=your_api_key_here
```

### 3. Run Assessment

```bash
python -m src.main assess
```

The tool will automatically use SearchAPI for Chrome AI queries if the key is configured.

## How It Works

When you query Chrome AI Summary:

1. **With SearchAPI key**: Makes real Google AI Overview queries via SearchAPI
2. **Without SearchAPI key but with OpenAI**: Simulates using GPT-4
3. **Without any key**: Returns mock response

### Priority Order

```
Chrome AI Query
    ↓
SearchAPI available? → Use SearchAPI (real AI Overview)
    ↓ No
OpenAI available? → Simulate with GPT-4
    ↓ No
Return mock response
```

## SearchAPI Response Format

SearchAPI returns Google AI Overview in this format:

```json
{
  "ai_overview": {
    "text": "The AI-generated summary text",
    "snippets": [
      {
        "text": "Supporting snippet 1",
        "title": "Source Title",
        "link": "https://..."
      }
    ],
    "sources": [...]
  },
  "organic_results": [...]
}
```

## Alternative: Simulated Engines

If you don't want to use SearchAPI, the tool can simulate AI engine responses using GPT-4 with web search capabilities.

### How Simulation Works

```python
# Example: Simulate Perplexity with GPT
from src.engines import EngineFactory

simulated_perplexity = EngineFactory.create_simulated_engine(
    target_engine=AIEngine.PERPLEXITY,
    credentials=credentials
)
```

The simulated engine:
1. Takes your query
2. Instructs GPT to respond like the target engine
3. Includes context about what companies/solutions to mention
4. Returns a response that approximates what the real engine would say

### Simulated vs Real

| Aspect | Real Engine | Simulated |
|--------|------------|-----------|
| Accuracy | 100% | ~70-80% |
| Cost | Engine-specific | OpenAI pricing |
| Rate Limits | Engine-specific | OpenAI limits |
| Use Case | Production | Testing, approximation |

## Configuration Options

### Force SearchAPI Usage

```python
from src.engines import SearchAPIEngine

engine = SearchAPIEngine(api_key="your_key")
response = await engine.query("your query")
```

### Force Simulation

```python
from src.engines import SimulatedAIEngine

engine = SimulatedAIEngine(
    openai_api_key="your_key",
    target_engine=AIEngine.CHROME_AI
)
response = await engine.query("your query")
```

### Use All Simulated Engines

```bash
# In your code
engines = EngineFactory.create_all_engines(
    credentials=credentials,
    use_simulation=True  # Enables simulation fallback
)
```

## Cost Comparison

### SearchAPI
- **Free tier**: 100 searches/month
- **Paid**: $29/month for 1,000 searches
- **Best for**: Chrome AI Overview access

### OpenAI Simulation
- **Cost**: ~$0.01-0.03 per query (GPT-4)
- **Best for**: Multiple engine simulation with one key

### Real APIs
- **Perplexity**: $5/month for 5,000 queries
- **ChatGPT**: Pay-per-use (varies)
- **Claude**: Pay-per-use (varies)

## Recommendations

### For Chrome AI Summary

✅ **Use SearchAPI** - Provides real Google AI Overview results

### For Other Engines

✅ **Use real APIs** when available (Perplexity, ChatGPT, Claude)

⚠️ **Use simulation** only for:
- Testing and development
- When API access is temporarily unavailable
- Quick approximations

❌ **Don't use simulation** for:
- Production visibility measurements
- Critical business decisions
- Accurate competitor analysis

## Example Usage

```python
import asyncio
from src.engines import SearchAPIEngine, SimulatedAIEngine
from src.config import AIEngine, EngineCredentials

async def test_engines():
    credentials = EngineCredentials(
        searchapi_api_key="your_searchapi_key",
        openai_api_key="your_openai_key"
    )

    # Real Chrome AI via SearchAPI
    searchapi = SearchAPIEngine(api_key=credentials.searchapi_api_key)
    real_response = await searchapi.query("managed AI services for enterprises")
    print("Real AI Overview:", real_response.response_text[:200])

    # Simulated Perplexity with GPT
    sim_perplexity = SimulatedAIEngine(
        openai_api_key=credentials.openai_api_key,
        target_engine=AIEngine.PERPLEXITY
    )
    sim_response = await sim_perplexity.query("managed AI services for enterprises")
    print("Simulated Perplexity:", sim_response.response_text[:200])

asyncio.run(test_engines())
```

## Troubleshooting

### SearchAPI not working

**Check**:
1. API key is valid
2. You haven't exceeded rate limits
3. Query is not empty
4. Internet connection is stable

**Debug**:
```python
# Enable detailed logging
response = await engine.query("test query")
print(response.metadata)  # Check for errors
print(response.error)     # See error message
```

### Simulation returning generic responses

**Issue**: GPT not mentioning your company

**Solution**: The simulation prompts are designed to consider First Line Software when relevant. If not working:
1. Make queries more specific to your services
2. Adjust the system prompt in `simulated_engine.py`
3. Use real APIs for accurate results

## API Documentation

- **SearchAPI**: https://www.searchapi.io/docs/google
- **OpenAI**: https://platform.openai.com/docs/api-reference
- **Perplexity**: https://docs.perplexity.ai/
- **Anthropic**: https://docs.anthropic.com/

## Support

For issues with:
- **SearchAPI integration**: Check SearchAPI documentation
- **Simulation accuracy**: This is experimental, use real APIs for production
- **Tool errors**: See main README.md troubleshooting section

---

**Last Updated**: 2024-11-05
