#!/usr/bin/env python3
"""
Test script for ANGL ETF with smart PDF search
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from full_etf_downloader import FullVanEckETFDownloader

async def test_angl():
    """Test downloading ANGL ETF with smart search."""
    
    # Create test downloader
    downloader = FullVanEckETFDownloader(download_dir="test_angl_download", max_concurrent=1)
    
    # ANGL ETF data
    angl_etf = {
        'ticker': 'ANGL',
        'name': 'Fallen Angel High Yield Bond ETF',
        'slug': 'fallen-angel-high-yield-bond-etf'
    }
    
    print("\n" + "="*60)
    print("Testing ANGL ETF Download with Smart PDF Search")
    print("="*60 + "\n")
    
    # Create session
    import aiohttp
    async with aiohttp.ClientSession() as session:
        # Test download
        result = await downloader.download_etf_data(angl_etf, session, None)
        
        print("\n" + "="*60)
        print("Test Results:")
        print("="*60)
        print(f"PDF Downloaded: {result['pdf_downloaded']}")
        print(f"PDF Verified: {result['pdf_verified']}")
        print(f"PDF Size: {result['pdf_size']} bytes")
        print(f"CSV Downloaded: {result['csv_downloaded']}")
        print(f"CSV Size: {result['csv_size']} bytes")
        
        if result['errors']:
            print(f"\nErrors encountered:")
            for error in result['errors']:
                print(f"  - {error}")
        
        # Check files
        test_dir = Path("test_angl_download/ANGL")
        if test_dir.exists():
            print(f"\nFiles created:")
            for file in test_dir.iterdir():
                print(f"  - {file.name} ({file.stat().st_size:,} bytes)")
        
        return result

if __name__ == "__main__":
    result = asyncio.run(test_angl())
    
    if result['pdf_verified']:
        print("\n✅ SUCCESS: ANGL PDF was downloaded and verified using smart search!")
    else:
        print("\n❌ FAILED: Could not download ANGL PDF")
    
    sys.exit(0 if result['pdf_verified'] else 1)