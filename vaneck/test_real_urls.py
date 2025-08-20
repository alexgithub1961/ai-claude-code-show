#!/usr/bin/env python3
"""
Test the real PDF URLs we discovered.
"""

import asyncio
from pathlib import Path

import httpx


async def test_pdf_download(url: str, filename: str):
    """Test downloading a PDF from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/pdf,application/octet-stream,*/*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Referer": "https://www.vaneck.com/us/en/investments/",
    }
    
    print(f"Testing: {url}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                follow_redirects=True,
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
            print(f"Content-Length: {response.headers.get('content-length', 'unknown')}")
            print(f"Final URL: {response.url}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' in content_type or response.content.startswith(b'%PDF'):
                    # Save the PDF
                    test_dir = Path('test_downloads')
                    test_dir.mkdir(exist_ok=True)
                    
                    pdf_file = test_dir / filename
                    with open(pdf_file, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✓ Successfully downloaded PDF: {pdf_file}")
                    print(f"  File size: {len(response.content)} bytes")
                    return True
                else:
                    print(f"⚠ Response is not a PDF")
                    print(f"  First 100 chars: {response.content[:100]}")
                    return False
            else:
                print(f"✗ HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def main():
    """Test the discovered PDF URLs."""
    print("🧪 Testing Real PDF URLs")
    
    test_urls = [
        ("https://www.vaneck.com/us/en/investments/gold-miners-etf-gdx-fact-sheet.pdf", "gdx_fact_sheet.pdf"),
        ("https://www.vaneck.com/us/en/investments/junior-gold-miners-etf-gdxj-fact-sheet.pdf", "gdxj_fact_sheet.pdf"),
    ]
    
    results = []
    for url, filename in test_urls:
        result = await test_pdf_download(url, filename)
        results.append(result)
        print("-" * 80)
    
    success_count = sum(results)
    print(f"\n📊 Summary: {success_count}/{len(results)} downloads successful")


if __name__ == "__main__":
    asyncio.run(main())