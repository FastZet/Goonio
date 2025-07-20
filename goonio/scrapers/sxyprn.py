from curl_cffi.requests import AsyncSession
from base64 import b64encode
from typing import List, Dict

from ..core.logger import logger

# Correct, working API endpoints
SEARCH_API_URL = "https://api.sxyprn.com/videos/search"
VIDEO_API_URL = "https://api.sxyprn.com/video/get"

# Headers to impersonate a real browser, crucial for bypassing Cloudflare/API blocks
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://sxyprn.net/' # Sending the Referer is good practice
}

async def search(query: str) -> List[Dict]:
    """
    Searches sxyprn.com's API for a given query and returns Stremio meta objects.
    """
    params = {'query': query, 'page': 1}
    metas = []
    
    try:
        async with AsyncSession(headers=HEADERS, impersonate="chrome110") as session:
            response = await session.get(SEARCH_API_URL, params=params)
            response.raise_for_status()
            json_data = response.json()

            # The API returns a list of video objects directly in the 'result' key
            for item in json_data.get('result', []):
                # The unique identifier is now the 'id' field
                video_id = item.get('id')
                if not video_id:
                    continue
                
                # We prefix the ID to create a unique identifier for our manager
                item_id = f"sxyprn_{video_id}"
                
                metas.append({
                    "id": item_id,
                    "type": "movie", # We treat all scenes as "movies" for Stremio
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
    'item_id' is expected to be in the format 'sxyprn_12345'
    """
    video_id = item_id.replace("sxyprn_", "")
    params = {'id': video_id}
    streams = []

    try:
        async with AsyncSession(headers=HEADERS, impersonate="chrome110") as session:
            response = await session.get(VIDEO_API_URL, params=params)
            response.raise_for_status()
            json_data = response.json()
            
            # The m3u8 URL is in a different location in this response
            m3u8_url = json_data.get('result', {}).get('video_url')
            
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
                logger.warning(f"SXYPRN API: No video_url found for ID: {video_id}")

        return streams

    except Exception as e:
        logger.error(f"SXYPRN API: Error getting streams for {item_id}: {e}")
        return []
