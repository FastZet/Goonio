from curl_cffi.requests import AsyncSession
from base64 import b64encode
from typing import List, Dict

from ..core.logger import logger

# The correct, working API endpoint
API_BASE_URL = "https://www.sxyprn.com/api/v2"

# Headers to impersonate a real browser, crucial for bypassing Cloudflare
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://sxyprn.net/'
}

async def search(query: str) -> List[Dict]:
    """
    Searches sxyprn.net's API using curl_cffi to bypass Cloudflare.
    """
    search_url = f"{API_BASE_URL}/search/videos?q={query.replace(' ', '+')}&page=1"
    metas = []
    
    try:
        async with AsyncSession(headers=HEADERS, impersonate="chrome110") as session:
            response = await session.get(search_url)
            response.raise_for_status()
            json_data = response.json()

            for item in json_data.get('data', []):
                slug = item.get('slug')
                if not slug:
                    continue
                
                item_id = f"sxyprn_{slug}"
                
                metas.append({
                    "id": item_id,
                    "type": "movie",
                    "name": item.get('title'),
                    "poster": item.get('thumb'),
                    "posterShape": "landscape"
                })
        
        logger.log("SCRAPER", f"SXYPRN API: Found {len(metas)} results for query '{query}'")
        return metas

    except Exception as e:
        logger.error(f"SXYPRN API: Error during search for '{query}': {e}")
        return []


async def get_streams(item_id: str) -> List[Dict]:
    """
    Fetches stream URLs for a given sxyprn item ID from their API.
    """
    slug = item_id.replace("sxyprn_", "")
    video_api_url = f"{API_BASE_URL}/videos/{slug}"
    streams = []

    try:
        async with AsyncSession(headers=HEADERS, impersonate="chrome110") as session:
            response = await session.get(video_api_url)
            response.raise_for_status()
            json_data = response.json()
            
            m3u8_url = json_data.get('data', {}).get('video_url')
            
            if m3u8_url:
                encoded_url = b64encode(m3u8_url.encode()).decode()
                proxy_url = f"/playback/sxyprn/{encoded_url}.m3u8"
                
                streams.append({
                    "name": "SXYPRN",
                    "title": "Auto Quality",
                    "url": proxy_url,
                })
                logger.log("SCRAPER", f"SXYPRN API: Found stream for {item_id}")
            else:
                logger.warning(f"SXYPRN API: No video_url found for: {video_api_url}")

        return streams

    except Exception as e:
        logger.error(f"SXYPRN API: Error getting streams for {item_id}: {e}")
        return []
