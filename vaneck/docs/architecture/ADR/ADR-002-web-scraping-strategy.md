# ADR-002: Web Scraping Strategy

## Status
Accepted

## Context
The VanEck ETF finder uses dynamic JavaScript to load fund data. We need to decide on the best approach for extracting fund information and download links.

URL: https://www.vaneck.com/us/en/etf-mutual-fund-finder/?InvType=etf&AssetClass=c,nr,t,cb,ei,ib,mb,fr,c-ra,c-da,c-g&Funds=emf,grf,iigf,mwmf,embf,ccif&ShareClass=a,c,i,y,z&tab=ov&Sort=name&SortDesc=true

## Decision
We will use a hybrid approach:
1. **Primary**: BeautifulSoup + requests for static content and API endpoints
2. **Fallback**: Selenium WebDriver for JavaScript-heavy pages if needed
3. **API Discovery**: Inspect network requests to find direct API endpoints
4. **Rate Limiting**: Implement respectful crawling with delays

**Technical Stack:**
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `selenium` as fallback for JavaScript-rendered content
- `aiohttp` for async downloads when beneficial

## Consequences
**Positive:**
- Faster scraping with requests/BeautifulSoup for static content
- Selenium fallback ensures compatibility with dynamic content
- Rate limiting prevents being blocked
- API discovery can provide more reliable data access

**Negative:**
- Selenium requires additional browser dependencies
- More complex error handling for multiple scraping strategies
- Need to handle JavaScript execution and wait times