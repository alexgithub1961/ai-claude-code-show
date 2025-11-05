# GEO Visibility Assessment Tool

A comprehensive tool to assess the **Generative Engine Optimization (GEO)** visibility of **First Line Software** across major AI-powered search engines and LLMs.

## Overview

This tool evaluates how prominently your company appears in responses from:
- **ChatGPT** (OpenAI)
- **Perplexity AI**
- **Claude** (Anthropic)
- **DeepSeek**
- **Grok** (xAI)
- **Chrome AI Summary** (manual testing)

### Business Areas Covered

1. **Gen AI / Managed AI Services**
   - Generative AI solutions
   - AI consulting and implementation
   - Managed AI infrastructure
   - Custom LLM development

2. **Digital Publishing / Digital Experience (DX)**
   - Content management systems
   - Digital publishing platforms
   - Headless CMS
   - Omnichannel publishing

## Features

✅ **Comprehensive Query Testing**
- 60+ seed queries across both business areas
- Query refinement and expansion
- Multiple query categories (Direct, Service, Comparison, Problem-Solving, Industry)

✅ **Multi-Engine Assessment**
- Parallel testing across multiple AI engines
- API integration with major platforms
- Mock engine support for manual testing

✅ **Advanced Visibility Analysis**
- Company mention detection
- Ranking among competitors
- Prominence scoring
- Context quality analysis
- Sentiment detection

✅ **Detailed Reporting**
- Overall visibility score (0-100)
- Per-engine breakdown
- Per-business area analysis
- Strengths and weaknesses
- Actionable recommendations

✅ **Multiple Output Formats**
- Console (readable text with charts)
- Markdown (documentation)
- JSON (programmatic access)

## Installation

### Prerequisites

- Python 3.9+
- API keys for AI engines (optional, at least one required)

### Setup

1. **Clone or navigate to the directory:**
```bash
cd geo_visibility
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure API keys:**
```bash
python -m src.main config --create
```

Edit the `.env` file with your API keys:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...
DEEPSEEK_API_KEY=...
GROK_API_KEY=...
```

## Usage

### Run Full Assessment

Test all configured engines with default settings:
```bash
python -m src.main assess
```

### Customize Assessment

**Test specific engines:**
```bash
python -m src.main assess --engines chatgpt --engines perplexity
```

**Test specific business areas:**
```bash
python -m src.main assess --business-areas gen_ai
```

**Adjust query count:**
```bash
python -m src.main assess --max-queries 10
```

**Disable query refinement:**
```bash
python -m src.main assess --no-refine
```

**Custom output directory:**
```bash
python -m src.main assess --output-dir ./custom_reports
```

### List Available Queries

View all seed queries:
```bash
python -m src.main list-queries
```

### Generate Query Suggestions

Get new query ideas:
```bash
python -m src.main suggest-queries gen_ai --count 20
```

```bash
python -m src.main suggest-queries digital_publishing --count 15
```

## Query Categories

The tool uses 5 types of queries:

1. **Direct**: Company name queries
   - "First Line Software AI services"

2. **Service**: Service-specific queries
   - "managed AI services for enterprises"

3. **Comparison**: Competitive queries
   - "best AI consulting companies 2024"

4. **Problem-Solving**: Solution-seeking queries
   - "how to implement AI in enterprise workflows"

5. **Industry**: Domain-specific queries
   - "AI solutions for financial services"

## Understanding Results

### Visibility Score (0-100)

The overall score is calculated from:
- **Mention Rate (50%)**: How often the company is mentioned
- **Prominence (30%)**: Position and frequency of mentions
- **Context Quality (20%)**: Quality of surrounding context

### Interpretation

- **70-100**: Excellent visibility
- **40-69**: Good visibility, room for improvement
- **0-39**: Limited visibility, requires attention

### Report Sections

1. **Overall Score**: Summary metrics
2. **Engine Breakdown**: Performance per AI engine
3. **Business Area Breakdown**: Performance per business area
4. **Strengths**: What's working well
5. **Weaknesses**: Areas needing improvement
6. **Recommendations**: Actionable next steps
7. **Detailed Results**: Query-by-query analysis

## Example Output

```
================================================================================
                    GEO VISIBILITY ASSESSMENT REPORT
                          First Line Software
================================================================================

Generated: 2024-01-15 14:30:00

OVERALL VISIBILITY SCORE
--------------------------------------------------------------------------------
[████████████████░░░░░░░░░░░░░░░░░░░░░░░░] 42.3/100
Total Queries: 50
Total Mentions: 18
Mention Rate: 36.0%

VISIBILITY BY AI ENGINE
--------------------------------------------------------------------------------
Engine        Score   Visual
------------  ------  ------------------------------
perplexity    52.3    [███████████████░░░░░░░░░░░░░░]
chatgpt       45.1    [█████████████░░░░░░░░░░░░░░░░░]
claude        38.7    [███████████░░░░░░░░░░░░░░░░░░░]

RECOMMENDATIONS
--------------------------------------------------------------------------------
1. Increase brand awareness through thought leadership and PR
2. Create more authoritative content about digital publishing capabilities
3. Improve SEO and content marketing to rank higher in AI search results
...
```

## Advanced Features

### Query Refinement

The query refiner automatically:
- Generates synonym variations
- Creates conversational variants
- Expands queries with context
- Generates industry-specific versions
- Converts to question format

### Company Detection

The analyzer can:
- Detect company mentions with aliases
- Extract competitor mentions
- Calculate ranking among companies
- Analyze context quality
- Detect sentiment (positive/neutral/negative)

### Custom Configuration

Modify `src/config.py` to:
- Add company aliases
- Adjust scoring weights
- Configure new business areas
- Add custom query categories

## Architecture

```
geo_visibility/
├── src/
│   ├── config.py              # Data models and configuration
│   ├── main.py                # CLI interface
│   ├── queries/               # Query generation
│   │   ├── seed_queries.py    # Seed query sets
│   │   └── query_refiner.py   # Query improvement
│   ├── engines/               # AI engine interfaces
│   │   ├── base.py            # Base engine class
│   │   ├── openai_engine.py   # ChatGPT
│   │   ├── perplexity_engine.py
│   │   ├── anthropic_engine.py # Claude
│   │   └── engine_factory.py  # Engine creation
│   ├── analyzers/             # Visibility analysis
│   │   ├── company_detector.py
│   │   └── visibility_analyzer.py
│   └── reports/               # Report generation
│       ├── report_generator.py
│       └── formatters.py
├── data/                      # Cached results
├── reports/                   # Generated reports
└── tests/                     # Unit tests
```

## API Rate Limits

Be mindful of API rate limits:
- **ChatGPT**: ~3500 requests/min (tier dependent)
- **Claude**: ~1000 requests/min
- **Perplexity**: ~20-50 requests/min

The tool includes automatic rate limiting (0.5s between requests).

## Troubleshooting

### No engines configured
- Ensure at least one API key is set in `.env`
- Check API key format and validity

### Rate limit errors
- Reduce `--max-queries` parameter
- Increase delay in `src/main.py` (line with `asyncio.sleep`)

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.9 or later

## Extending the Tool

### Adding New Queries

Edit `src/queries/seed_queries.py`:
```python
GEN_AI_QUERIES[QueryCategory.SERVICE].append(
    "your new query here"
)
```

### Adding New Engines

1. Create engine class in `src/engines/`
2. Implement `AIEngineBase` interface
3. Add to `EngineFactory`
4. Update `AIEngine` enum in `config.py`

### Custom Analysis

Modify `src/analyzers/visibility_analyzer.py` to adjust:
- Scoring algorithms
- Sentiment detection
- Context quality metrics

## Roadmap

- [ ] Historical tracking and trend analysis
- [ ] Automated scheduling and monitoring
- [ ] Competitor comparison mode
- [ ] Integration with Google Search Console
- [ ] Interactive dashboard
- [ ] A/B testing for content optimization

## License

Proprietary - First Line Software

## Support

For questions or issues:
- Internal: Contact the Marketing/SEO team
- Technical: Contact the Development team

---

**Version**: 1.0.0
**Last Updated**: 2024-01-15
