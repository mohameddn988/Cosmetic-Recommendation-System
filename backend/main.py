import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def test_scraping(url, user_agent=None):
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=1)
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    headers = {
        'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = session.get(url, headers=headers, timeout=10)
        print(f"✅ {url}: STATUS {response.status_code}")
        print(f"   Size: {len(response.content)/1000:.1f} KB")
        if response.status_code == 200:
            print("   🎯 PERFECT for BeautifulSoup + Requests!")
        return True
    except Exception as e:
        print(f"❌ {url}: {e}")
        return False

# TEST ALL YOUR PROJECT SITES (uncomment to run)
sites = [
    "https://www.tct.pro/used-vehicles",
]

for site in sites:
    test_scraping(site)
    print("-" * 50)