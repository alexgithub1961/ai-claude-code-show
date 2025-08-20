"""Sample data for testing."""

# Sample HTML responses
VANECK_HOMEPAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>VanEck - ETF and Investment Solutions</title>
    <meta charset="utf-8">
</head>
<body>
    <header>
        <nav>
            <a href="/us/en/etf-mutual-fund-finder/">ETF Finder</a>
            <a href="/us/en/investments/">Investments</a>
        </nav>
    </header>
    <main>
        <h1>Welcome to VanEck</h1>
        <p>Discover our range of ETF products</p>
    </main>
</body>
</html>
"""

ETF_FINDER_HTML = """
<!DOCTYPE html>
<html>
<head><title>VanEck ETF Finder</title></head>
<body>
    <div class="etf-finder">
        <h1>ETF & Mutual Fund Finder</h1>
        <div class="etf-results">
            <div class="etf-card" data-ticker="GDX">
                <h3 class="etf-name">VanEck Vectors Gold Miners ETF</h3>
                <div class="etf-details">
                    <span class="ticker">GDX</span>
                    <span class="nav">$25.43</span>
                    <span class="expense-ratio">0.52%</span>
                </div>
                <a href="/us/en/investments/gold-miners-etf-gdx/" class="detail-link">View Details</a>
                <div class="download-links">
                    <a href="/us/en/investments/gold-miners-etf-gdx/holdings.csv" class="download-csv">Holdings CSV</a>
                    <a href="/us/en/investments/gold-miners-etf-gdx/fact-sheet.pdf" class="download-pdf">Fact Sheet</a>
                </div>
            </div>
            <div class="etf-card" data-ticker="SMH">
                <h3 class="etf-name">VanEck Vectors Semiconductor ETF</h3>
                <div class="etf-details">
                    <span class="ticker">SMH</span>
                    <span class="nav">$145.67</span>
                    <span class="expense-ratio">0.35%</span>
                </div>
                <a href="/us/en/investments/semiconductor-etf-smh/" class="detail-link">View Details</a>
                <div class="download-links">
                    <a href="/us/en/investments/semiconductor-etf-smh/holdings.xlsx" class="download-excel">Holdings Excel</a>
                    <a href="/us/en/investments/semiconductor-etf-smh/performance.json" class="download-json">Performance Data</a>
                </div>
            </div>
            <div class="etf-card" data-ticker="OIH">
                <h3 class="etf-name">VanEck Vectors Oil Services ETF</h3>
                <div class="etf-details">
                    <span class="ticker">OIH</span>
                    <span class="nav">$198.32</span>
                    <span class="expense-ratio">0.35%</span>
                </div>
                <a href="/us/en/investments/oil-services-etf-oih/" class="detail-link">View Details</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

ETF_DETAIL_PAGE_HTML = """
<!DOCTYPE html>
<html>
<head><title>VanEck Vectors Gold Miners ETF (GDX)</title></head>
<body>
    <div class="etf-detail">
        <header>
            <h1>VanEck Vectors Gold Miners ETF</h1>
            <div class="etf-summary">
                <span class="ticker">GDX</span>
                <span class="nav">$25.43</span>
                <span class="assets">$12.5B AUM</span>
            </div>
        </header>
        
        <section class="downloads">
            <h2>Downloads</h2>
            <ul class="download-list">
                <li><a href="/content/files/etf/gdx/holdings.csv" class="download-link" data-type="csv">Daily Holdings CSV</a></li>
                <li><a href="/content/files/etf/gdx/fact-sheet.pdf" class="download-link" data-type="pdf">Fact Sheet PDF</a></li>
                <li><a href="/content/files/etf/gdx/prospectus.pdf" class="download-link" data-type="pdf">Prospectus</a></li>
                <li><a href="/content/files/etf/gdx/annual-report.pdf" class="download-link" data-type="pdf">Annual Report</a></li>
                <li><a href="/content/files/etf/gdx/performance.json" class="download-link" data-type="json">Performance Data</a></li>
            </ul>
        </section>
        
        <section class="fund-details">
            <h2>Fund Details</h2>
            <table>
                <tr><td>Inception Date</td><td>May 16, 2006</td></tr>
                <tr><td>Expense Ratio</td><td>0.52%</td></tr>
                <tr><td>Distribution Frequency</td><td>Quarterly</td></tr>
            </table>
        </section>
    </div>
</body>
</html>
"""

# Sample CSV content
SAMPLE_HOLDINGS_CSV = """Ticker,Company Name,Weight %,Market Value,Shares
NEM,Newmont Corporation,8.45,1234567890,48653421
GOLD,Barrick Gold Corporation,7.32,1098765432,54321098
AEM,Agnico Eagle Mines Limited,6.28,987654321,12345678
WPM,Wheaton Precious Metals Corp,5.91,876543210,9876543
KGC,Kinross Gold Corporation,4.87,765432109,87654321
"""

# Sample JSON performance data
SAMPLE_PERFORMANCE_JSON = """{
  "fund_ticker": "GDX",
  "fund_name": "VanEck Vectors Gold Miners ETF",
  "as_of_date": "2024-01-15",
  "nav": 25.43,
  "returns": {
    "1_day": -0.85,
    "1_week": 2.14,
    "1_month": -3.21,
    "3_months": 8.76,
    "6_months": -12.45,
    "1_year": 15.32,
    "3_years": -8.91,
    "5_years": 45.67
  },
  "benchmark_returns": {
    "1_day": -0.92,
    "1_week": 1.89,
    "1_month": -2.98,
    "3_months": 7.54,
    "6_months": -11.23,
    "1_year": 14.08,
    "3_years": -9.87,
    "5_years": 42.19
  },
  "top_holdings": [
    {"ticker": "NEM", "weight": 8.45, "name": "Newmont Corporation"},
    {"ticker": "GOLD", "weight": 7.32, "name": "Barrick Gold Corporation"},
    {"ticker": "AEM", "weight": 6.28, "name": "Agnico Eagle Mines Limited"}
  ]
}"""

# Sample fund list data
SAMPLE_ETF_LIST = [
    {
        "ticker": "GDX",
        "name": "VanEck Vectors Gold Miners ETF",
        "nav": 25.43,
        "expense_ratio": 0.52,
        "aum": "12.5B",
        "inception_date": "2006-05-16",
        "url": "https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx/",
        "category": "Precious Metals",
    },
    {
        "ticker": "SMH",
        "name": "VanEck Vectors Semiconductor ETF",
        "nav": 145.67,
        "expense_ratio": 0.35,
        "aum": "8.7B",
        "inception_date": "1999-05-05",
        "url": "https://www.vaneck.com/us/en/investments/semiconductor-etf-smh/",
        "category": "Technology",
    },
    {
        "ticker": "OIH",
        "name": "VanEck Vectors Oil Services ETF",
        "nav": 198.32,
        "expense_ratio": 0.35,
        "aum": "1.2B",
        "inception_date": "2011-12-20",
        "url": "https://www.vaneck.com/us/en/investments/oil-services-etf-oih/",
        "category": "Energy",
    },
    {
        "ticker": "GDXJ",
        "name": "VanEck Vectors Junior Gold Miners ETF",
        "nav": 32.18,
        "expense_ratio": 0.52,
        "aum": "3.1B",
        "inception_date": "2009-11-10",
        "url": "https://www.vaneck.com/us/en/investments/junior-gold-miners-etf-gdxj/",
        "category": "Precious Metals",
    },
    {
        "ticker": "VNQ",
        "name": "Vanguard Real Estate Index Fund ETF",
        "nav": 89.45,
        "expense_ratio": 0.12,
        "aum": "45.3B",
        "inception_date": "2004-09-23", 
        "url": "https://www.vaneck.com/us/en/investments/real-estate-etf-vnq/",
        "category": "Real Estate",
    },
]

# Sample error responses
HTTP_404_RESPONSE = """
<!DOCTYPE html>
<html>
<head><title>404 - Page Not Found</title></head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The requested page could not be found.</p>
</body>
</html>
"""

HTTP_500_RESPONSE = """
<!DOCTYPE html>
<html>
<head><title>500 - Internal Server Error</title></head>
<body>
    <h1>500 - Internal Server Error</h1>
    <p>An internal server error occurred.</p>
</body>
</html>
"""

# Sample file content for testing downloads
SAMPLE_PDF_CONTENT = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000010 00000 n \n0000000053 00000 n \n0000000109 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n187\n%%EOF"

SAMPLE_EXCEL_CONTENT = b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x13\x00\x08\x02[Content_Types].xml"

# URL patterns for testing
URL_PATTERNS = {
    "homepage": "https://www.vaneck.com",
    "etf_finder": "https://www.vaneck.com/us/en/etf-mutual-fund-finder/",
    "etf_detail": "https://www.vaneck.com/us/en/investments/{ticker}/",
    "holdings_csv": "https://www.vaneck.com/content/files/etf/{ticker}/holdings.csv",
    "fact_sheet_pdf": "https://www.vaneck.com/content/files/etf/{ticker}/fact-sheet.pdf",
    "performance_json": "https://www.vaneck.com/content/files/etf/{ticker}/performance.json",
}

# Mock HTTP responses for different scenarios
MOCK_RESPONSES = {
    "success": {
        "status_code": 200,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "text": ETF_FINDER_HTML,
    },
    "not_found": {
        "status_code": 404,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "text": HTTP_404_RESPONSE,
    },
    "server_error": {
        "status_code": 500,
        "headers": {"Content-Type": "text/html; charset=utf-8"},
        "text": HTTP_500_RESPONSE,
    },
    "timeout": {
        "exception": "requests.exceptions.Timeout",
        "message": "Request timed out",
    },
    "connection_error": {
        "exception": "requests.exceptions.ConnectionError", 
        "message": "Connection failed",
    },
    "csv_download": {
        "status_code": 200,
        "headers": {
            "Content-Type": "text/csv",
            "Content-Length": str(len(SAMPLE_HOLDINGS_CSV)),
            "Content-Disposition": "attachment; filename=holdings.csv",
        },
        "content": SAMPLE_HOLDINGS_CSV.encode(),
    },
    "pdf_download": {
        "status_code": 200,
        "headers": {
            "Content-Type": "application/pdf",
            "Content-Length": str(len(SAMPLE_PDF_CONTENT)),
            "Content-Disposition": "attachment; filename=fact-sheet.pdf",
        },
        "content": SAMPLE_PDF_CONTENT,
    },
    "json_download": {
        "status_code": 200,
        "headers": {
            "Content-Type": "application/json",
            "Content-Length": str(len(SAMPLE_PERFORMANCE_JSON)),
        },
        "content": SAMPLE_PERFORMANCE_JSON.encode(),
    },
    "partial_content": {
        "status_code": 206,
        "headers": {
            "Content-Range": "bytes 0-1023/2048",
            "Content-Length": "1024",
            "Accept-Ranges": "bytes",
        },
        "content": b"x" * 1024,
    },
}

# Test configuration values
TEST_CONFIG = {
    "download_dir": "/tmp/vaneck_test_downloads",
    "max_concurrent_downloads": 2,
    "request_timeout": 5,
    "max_retries": 2,
    "retry_delay": 0.1,
    "rate_limit_delay": 0.1,
    "user_agent": "VanEck-Downloader-Test/1.0",
    "enable_resume": True,
    "chunk_size": 1024,
}