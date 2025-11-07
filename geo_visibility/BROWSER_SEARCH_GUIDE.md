# Browser-Based Search Guide
## Why Browser Results May Differ from API Results

**Date**: November 7, 2025
**Critical Insight**: User observed that browser-based searches show vendor names, contradicting our API-based findings.

---

## The Problem

Our SearchAPI-based assessments showed:
- **0-5% AI Overview appearance rate**
- **Minimal company mentions**
- **"An AI Overview is not available for this search"** for most queries

**BUT** - Real browser searches may show completely different results!

---

## Why Browser Results May Differ

### 1. JavaScript Rendering
- **API Response**: Static HTML
- **Browser**: Fully rendered JavaScript
- **Impact**: AI Overview may be dynamically loaded via JS

### 2. User Agent Differences
- **API**: Identified as bot/crawler
- **Browser**: Identified as real user
- **Impact**: Google serves different content to users vs bots

### 3. Personalization
- **API**: No personalization
- **Browser**: Location, history, preferences
- **Impact**: Different rankings and features

### 4. A/B Testing
- **API**: May not participate in experiments
- **Browser**: Gets latest features being tested
- **Impact**: AI Overview availability varies

### 5. Rate Limiting & Detection
- **API**: Known bot behavior
- **Browser**: Natural human patterns
- **Impact**: API requests may be filtered/limited

---

## Evidence from User Observation

**User reported**: "browser based searches show vendor names for similar queries"

This suggests:
- ✅ AI Overview appears more frequently in real browsers
- ✅ Company names DO appear in browser results
- ✅ Our API-based assessment may have missed actual visibility
- ✅ SearchAPI may not reflect real user experience

---

## Browser-Based Implementation

We created `browser_search_engine.py` using Playwright to emulate real browser searches:

### Key Features

```python
class BrowserSearchEngine:
    """
    Real browser automation with Playwright.
    Gets the actual results users see.
    """

    async def search_google(self, query: str) -> Dict:
        # Opens real Chromium browser
        # Navigates to google.com
        # Searches like a real user
        # Extracts AI Overview, organic results, etc.
        # Takes screenshots for verification
```

### What It Extracts

1. **AI Overview**:
   - Full text content
   - Source citations
   - Links and references

2. **Organic Results**:
   - Title, link, snippet for top 20 results
   - Position tracking
   - Domain information

3. **Knowledge Panel**:
   - Company information boxes
   - Right-side info cards

4. **Featured Snippets**:
   - Position 0 answers
   - Source attribution

---

## Expected Findings (When Run in Real Environment)

### Hypothesis

**Based on user observation, we expect**:

1. **Higher AI Overview Rate**:
   - API: 0-5%
   - Browser: 15-40% (predicted)

2. **More Company Mentions**:
   - API: 0 mentions
   - Browser: 5-15% mention rate (predicted)

3. **Different Query Performance**:
   - Some query types trigger AI Overview in browser
   - Vendor-seeking queries may show company names
   - Industry queries may have company mentions

### Critical Queries to Test

**High Priority** (most likely to show differences):

```python
critical_queries = [
    # Direct company queries
    "EPAM software company",
    "First Line Software Ukraine",
    "DataArt consulting services",

    # Service + vendor combination
    "top AI consulting companies",
    "best LLM implementation firms",
    "generative AI consultants",

    # Problem + solution
    "who can build custom RAG system",
    "companies that implement AI chatbots",
    "LLM integration consulting",

    # Comparison queries
    "EPAM competitors",
    "companies like Endava",
    "DataArt alternatives",
]
```

---

## Running Browser-Based Assessment

### Prerequisites

```bash
# Install dependencies
pip install playwright

# Install browser binaries
python -m playwright install chromium

# Ensure network access (not available in sandboxed environments)
```

### Basic Usage

```python
from browser_search_engine import BrowserSearchEngine

async def main():
    async with BrowserSearchEngine(headless=True) as browser:
        result = await browser.search_google("EPAM software company")

        print(f"AI Overview: {result['has_ai_overview']}")
        print(f"Text: {result['ai_overview']['text']}")
        print(f"Organic results: {len(result['organic_results'])}")

asyncio.run(main())
```

### Comparison Script

```python
from browser_search_engine import compare_api_vs_browser

# Compare SearchAPI vs real browser
await compare_api_vs_browser(
    query="generative AI consulting services",
    searchapi_key="your-key"
)
```

### Full Assessment

```python
# Run comprehensive comparison
queries = [
    "First Line Software AI services",
    "LLM implementation companies",
    "generative AI consulting firms",
    # ... more queries
]

results = []
async with BrowserSearchEngine() as browser:
    for query in queries:
        result = await browser.search_google(query)
        results.append(result)
        await asyncio.sleep(3)  # Be nice to Google

# Analyze results
analyze_browser_vs_api_differences(results)
```

---

## What to Look For

### 1. AI Overview Differences

**If browser shows AI Overview but API doesn't**:
- ✅ Confirms API limitation
- ✅ Real users see AI Overview
- ✅ GEO visibility EXISTS but wasn't measured

### 2. Company Mention Patterns

**Check for**:
- Which companies appear in AI Overview text?
- What query types trigger company mentions?
- Position of company names (early vs late)?
- Context of mentions (positive, neutral, list)?

### 3. Query Category Analysis

**Test by category**:
- Generic service queries
- Specific technology queries
- Vendor selection queries
- Problem-solving queries
- Comparison queries

### 4. Competitive Intelligence

**Compare**:
- First Line Software vs competitors
- Frequency of mentions
- Context and prominence
- Which queries show which companies

---

## Analyzing Browser Results

### Company Detection

```python
def analyze_company_visibility(browser_results):
    companies = [
        "First Line Software",
        "EPAM",
        "DataArt",
        "Endava",
        # ...
    ]

    visibility = defaultdict(lambda: {
        "ai_overview_mentions": 0,
        "organic_appearances": 0,
        "knowledge_panels": 0,
        "queries": [],
    })

    for result in browser_results:
        # Check AI Overview
        if result['has_ai_overview']:
            ai_text = result['ai_overview']['text']
            for company in companies:
                if company.lower() in ai_text.lower():
                    visibility[company]["ai_overview_mentions"] += 1
                    visibility[company]["queries"].append(result['query'])

        # Check organic results
        for organic in result['organic_results']:
            for company in companies:
                if company.lower() in organic['title'].lower() or \
                   company.lower() in organic['snippet'].lower():
                    visibility[company]["organic_appearances"] += 1

    return visibility
```

### Comparison Metrics

```python
def compare_api_vs_browser_overall(api_results, browser_results):
    """
    Compare aggregate findings from API vs browser assessments.
    """
    comparison = {
        "ai_overview_rate": {
            "api": calculate_rate(api_results, "has_ai_overview"),
            "browser": calculate_rate(browser_results, "has_ai_overview"),
        },
        "company_mention_rate": {
            "api": calculate_mention_rate(api_results),
            "browser": calculate_mention_rate(browser_results),
        },
        "avg_organic_results": {
            "api": avg_count(api_results, "organic_results"),
            "browser": avg_count(browser_results, "organic_results"),
        },
    }

    # Show differences
    for metric, values in comparison.items():
        diff = values["browser"] - values["api"]
        print(f"{metric}:")
        print(f"  API:     {values['api']:.1f}%")
        print(f"  Browser: {values['browser']:.1f}%")
        print(f"  Diff:    {diff:+.1f}% {'⚠️ SIGNIFICANT' if abs(diff) > 10 else ''}")
```

---

## Expected Scenarios

### Scenario A: Major Difference
**If browser shows 30-50% AI Overview rate vs API's 0-5%**:
- ✅ **Finding**: SearchAPI is not representative
- ✅ **Action**: Browser-based assessment is critical
- ✅ **Strategy**: GEO visibility may be viable after all

### Scenario B: Moderate Difference
**If browser shows 10-20% AI Overview rate**:
- ✅ **Finding**: Some AI Overview availability
- ✅ **Action**: Focus on query types that trigger it
- ✅ **Strategy**: Selective GEO optimization

### Scenario C: Minimal Difference
**If browser shows similar 0-10% rate**:
- ✅ **Finding**: API assessment was accurate
- ✅ **Action**: GEO still not viable
- ✅ **Strategy**: Focus on other channels

---

## Implementation Challenges

### Sandboxed Environment Issues

**Current limitation**: DNS resolution fails in Docker sandbox
```
ERR_NAME_NOT_RESOLVED at https://www.google.com/
```

**Solutions**:
1. Run in local development environment
2. Run on cloud VM with network access
3. Use proxy/VPN if needed
4. Consider headless=False for debugging

### Google Bot Detection

**Challenge**: Google may detect automation

**Solutions**:
1. **Stealth Mode**:
   ```python
   from playwright_stealth import stealth_async

   async def search_with_stealth(page):
       await stealth_async(page)
       await page.goto("https://www.google.com")
   ```

2. **Human-like Behavior**:
   ```python
   # Random delays
   await page.wait_for_timeout(random.randint(1000, 3000))

   # Mouse movements
   await page.mouse.move(100, 100)

   # Gradual typing
   await search_box.type(query, delay=random.randint(50, 150))
   ```

3. **Residential Proxies**: Route through residential IPs

### Rate Limiting

**Challenge**: Too many searches trigger blocks

**Solutions**:
- 3-5 second delays between queries
- Rotate user agents
- Vary search patterns
- Use different browsers/profiles
- Spread across multiple IPs

---

## Next Steps

### Immediate (Run in Non-Sandboxed Environment)

1. **Setup**:
   ```bash
   # On local machine or VM with internet
   git clone <repo>
   cd geo_visibility
   pip install -r requirements.txt
   python -m playwright install chromium
   ```

2. **Test Single Query**:
   ```python
   python -c "
   import asyncio
   from browser_search_engine import BrowserSearchEngine

   async def test():
       async with BrowserSearchEngine(headless=False) as browser:
           result = await browser.search_google('EPAM software company')
           print(f'AI Overview: {result[\"has_ai_overview\"]}')

   asyncio.run(test())
   "
   ```

3. **Run Comparison**:
   ```bash
   export SEARCHAPI_API_KEY=dUngVqvqnKPAr1p1BKqKENJW
   python browser_search_engine.py
   ```

### Follow-Up Assessment

Create `browser_assessment_full.py`:
- 25 critical queries
- API vs browser comparison
- Company visibility tracking
- Screenshot capture
- Detailed HTML analysis

### Analysis & Reporting

Generate:
- Browser vs API comparison report
- Actual GEO visibility metrics
- Query type performance analysis
- Strategic recommendations update

---

## Technical Details

### Browser Selectors for AI Overview

```python
# Multiple selector strategies (Google changes these)
ai_overview_selectors = [
    # Data attributes
    "[data-attrid*='SGE']",
    "[data-attrid*='AIOverview']",
    "[jsname*='SGE']",
    "div[data-content-feature='1']",

    # Class names
    ".AIOverview",
    ".ai-overview",
    ".sge-container",

    # Text content
    "text=/AI-generated/i",
    "text=/AI Overview/i",
    "text=/Generative AI is experimental/i",

    # Structural
    "div[role='region'][aria-label*='AI']",
]
```

### Organic Result Extraction

```python
# Google search result selectors
result_selectors = [
    "div.g",              # Standard result
    ".tF2Cxc",            # Alternative format
    "[data-sokoban-container]",  # Container format
]

# Title extraction
title = result.locator("h3").first

# Link extraction
link = result.locator("a[href]").first

# Snippet extraction
snippet_selectors = [
    ".VwiC3b",     # Standard snippet
    "[data-sncf='1']",  # Snippet alternative
    ".IsZvec",     # Older format
]
```

---

## Cost Considerations

### Browser-Based Search Costs

**Infrastructure**:
- Local machine: Free
- Cloud VM: ~$5-20/month
- Residential proxy: ~$50-100/month (if needed)

**Time**:
- ~5-10 seconds per query (vs 2-3 for API)
- 143 queries = 12-24 minutes total

**Comparison**:
- SearchAPI: ~$29/month for 1000 searches
- Browser: Free queries, but infrastructure cost

---

## Validation Strategy

### How to Verify Results

1. **Manual Spot Checks**:
   - Run query in real Chrome
   - Compare with browser automation results
   - Verify AI Overview matches

2. **Screenshot Comparison**:
   - Automated screenshot
   - Manual screenshot
   - Visual diff

3. **HTML Analysis**:
   - Save full page HTML
   - Inspect element structure
   - Verify selectors

4. **Multiple Runs**:
   - Run same query 3-5 times
   - Check consistency
   - Note variations (A/B tests)

---

## Conclusion

### Critical Insight

**User observation that browser searches show vendor names is potentially game-changing.**

If true, it means:
- ✅ Our API assessment underestimated visibility
- ✅ GEO visibility may actually exist
- ✅ Browser-based assessment is essential
- ✅ Strategy recommendations may need revision

### Next Action

**HIGH PRIORITY**: Run `browser_search_engine.py` in environment with network access to validate user observation and get accurate GEO visibility data.

**Expected Impact**: May completely change our findings and recommendations.

---

**Status**: Implementation ready, waiting for network-accessible environment
**File**: `browser_search_engine.py`
**Dependencies**: playwright, chromium
**Run Time**: ~15-20 minutes for full assessment
**Confidence**: High that browser results will differ from API

**Last Updated**: November 7, 2025
