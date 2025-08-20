# VanEck ETF Downloader - Debug Analysis & Solution

## Problem Summary

The original VanEck ETF downloader in `src/vaneck_etf_downloader.py` was failing to download PDFs because it was using incorrect URL patterns that resulted in redirects to HTML pages instead of actual PDF files.

## Root Cause Analysis

### 1. Incorrect URL Construction

**Original problematic code (lines 135-136):**
```python
fact_sheet_url = etf['url'].replace('/etf/', '/assets/resources/fact-sheets/')
fact_sheet_url += f"-fact-sheet.pdf"
```

**Issues:**
- Constructed URLs like `/assets/resources/fact-sheets/gdx-fact-sheet.pdf`
- These URLs return HTTP 301 redirects to the ETF product pages
- No actual PDF files exist at these locations

### 2. Inadequate Headers

**Original headers:**
```python
self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.vaneck.com/us/en/etf-mutual-fund-finder/"
}
```

**Problems:**
- Generic User-Agent string (incomplete)
- Missing browser-specific security headers
- Wrong Accept header for PDF downloads
- Generic referer that doesn't match the actual source page

### 3. No Retry Logic or URL Pattern Fallbacks

- Only tried one URL pattern per document type
- No validation of response content type
- No verification that downloaded content was actually a PDF

## Investigation Process

### 1. Debug Script Results

Created `simple_debug_downloads.py` to test multiple URL patterns:
- Tested 72 different URL combinations (2 tickers × 12 patterns × 3 header variants)
- **0% success rate** - all URLs redirected to HTML pages
- Discovered that VanEck redirects incorrect URLs to product pages

### 2. Product Page Scraping

Created `scrape_product_page.py` to find real PDF URLs:
- Successfully discovered actual working URL pattern
- Found real fact sheet URLs:
  - `https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx-fact-sheet.pdf`
  - `https://www.vaneck.com/us/en/investments/junior-gold-miners-etf-gdxj-fact-sheet.pdf`

### 3. URL Pattern Analysis

**Correct URL Pattern:**
```
{base_url}/us/en/investments/{etf-name}-fact-sheet.pdf
```

Where `{etf-name}` comes from the product page URL path, e.g.:
- Product URL: `/us/en/investments/gold-miners-etf-gdx/`
- Fact Sheet: `/us/en/investments/gold-miners-etf-gdx-fact-sheet.pdf`

## Solution Implementation

### 1. Improved Headers

**Browser-like headers:**
```python
self.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# PDF-specific headers
self.pdf_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/octet-stream,*/*",
    "Accept-Language": "en-GB,en;q=0.9",
    "Cache-Control": "no-cache",
}
```

### 2. URL Pattern Discovery & Retry Logic

**Multiple URL patterns with priority:**
1. **Direct product path** (highest priority): Extract from product URL
2. **Common naming patterns**: Various ticker-based patterns
3. **Legacy patterns**: For backward compatibility

**Implementation:**
```python
def _generate_fact_sheet_urls(self, ticker: str, product_url: str) -> List[Tuple[str, str]]:
    patterns = []
    
    # Pattern 1: Direct fact sheet URL (discovered working pattern)
    if product_url and 'investments/' in product_url:
        match = re.search(r'/investments/([^/]+)', product_url)
        if match:
            etf_path = match.group(1)
            fact_sheet_url = f"{self.base_url}/us/en/investments/{etf_path}-fact-sheet.pdf"
            patterns.append(("direct_product_path", fact_sheet_url))
    
    # Pattern 2: Fallback patterns
    ticker_lower = ticker.lower()
    common_patterns = [
        ("simple_ticker", f"{self.base_url}/us/en/investments/{ticker_lower}-etf-fact-sheet.pdf"),
        ("ticker_with_etf", f"{self.base_url}/us/en/investments/{ticker_lower}-fact-sheet.pdf"),
        ("assets_resources", f"{self.base_url}/us/en/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
        ("direct_assets", f"{self.base_url}/assets/resources/fact-sheets/{ticker_lower}-fact-sheet.pdf"),
    ]
    
    patterns.extend(common_patterns)
    return patterns
```

### 3. Content Validation

**PDF validation:**
```python
if response.status_code == 200:
    content_type = response.headers.get('content-type', '').lower()
    
    # Check if it's actually a PDF
    if ('pdf' in content_type or response.content.startswith(b'%PDF')):
        # Valid PDF - save it
        with open(pdf_file, 'wb') as f:
            f.write(response.content)
        return True
    else:
        # Not a PDF - try next pattern
        continue
```

### 4. Error Handling & Logging

**Comprehensive error tracking:**
- Log each attempted URL pattern
- Track success/failure reasons
- Provide detailed error messages
- Save download results for analysis

## Test Results

### Improved Downloader Performance

**Test run with 2 ETFs (NLR, GPZ):**
- **Success rate: 100%**
- **Total files downloaded: 9**
  - NLR: 5 files (fact sheet, holdings, metadata, 2 other documents)
  - GPZ: 4 files (fact sheet, metadata, 2 other documents)

**File types successfully downloaded:**
- ✅ PDF fact sheets
- ✅ CSV holdings data
- ✅ Additional PDF documents found on product pages
- ✅ JSON metadata
- ✅ Privacy notices and other supporting documents

### Working URLs Examples

**Successful fact sheet downloads:**
- `https://www.vaneck.com/us/en/investments/uranium-nuclear-energy-etf-nlr-fact-sheet.pdf`
- `https://www.vaneck.com/us/en/investments/alternative-asset-manager-etf-gpz-fact-sheet.pdf`

**Additional documents discovered:**
- Fund profiles, investment theses, privacy notices
- Holdings data (when available)
- Product-specific marketing materials

## Implementation Files

### 1. `src/improved_vaneck_etf_downloader.py`
- Complete rewrite with all improvements
- Uses httpx instead of aiohttp
- Comprehensive error handling and logging
- Multiple document type support
- Product page scraping for additional documents

### 2. Updated `src/vaneck_etf_downloader.py`
- Applied key improvements to original file
- Enhanced headers and URL patterns
- Added retry logic
- Note: Still requires aiohttp dependency

### 3. Debug/Analysis Scripts
- `simple_debug_downloads.py`: URL pattern testing
- `scrape_product_page.py`: Product page analysis
- `test_real_urls.py`: URL validation

## Key Improvements Summary

1. **✅ Fixed URL Construction**: Using correct URL patterns based on product page structure
2. **✅ Enhanced Headers**: Browser-like headers with proper security tokens
3. **✅ Retry Logic**: Multiple URL patterns tried in order of probability
4. **✅ Content Validation**: Verify downloaded content is actually PDF/CSV
5. **✅ Comprehensive Logging**: Detailed error tracking and success reporting
6. **✅ Multiple Document Types**: Fact sheets, holdings, additional documents
7. **✅ Product Page Scraping**: Discover additional document links automatically

## Recommendations

1. **Use the improved downloader** (`improved_vaneck_etf_downloader.py`) for new implementations
2. **Install httpx** if not available: `pip install httpx beautifulsoup4`
3. **Monitor URL patterns** as VanEck may change their website structure
4. **Implement rate limiting** for respectful scraping (already included)
5. **Cache product page mappings** to reduce redundant requests

## Success Metrics

- **Before**: 0% PDF download success rate
- **After**: 100% success rate for tested ETFs
- **Error reduction**: From complete failure to graceful degradation with detailed logging
- **Document coverage**: Extended from just fact sheets to comprehensive document collection