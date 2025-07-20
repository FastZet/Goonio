import aiohttp
from base64 import b64encode
from typing import List, Dict

from ..core.logger import logger

# Correct, working API endpoint
API_BASE_URL = "https://www.sxyprn.com/api/v2"

async def search(query: str) -> List[Dict]:
    """
    Searches sxyprn.net's API for a given query and returns Stremio meta objects.
    """
    # The API uses a 'q' parameter for the query
    search_url = f"{API_BASE_URL}/videos?q={query.replace(' ', '+')}&page=1"
    metas = []
    
    try:
        # The sxyprn API requires a standard User-Agent header to respond
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(search_url) as response:
                response.raise_for_status()
                json_data = await response.json()

                # The API returns a list of video objects directly in the 'data' key
                for item in json_data.get('data', []):
                    slug = item.get('slug')
                    if not slug:
                        continue
                    
                    # We prefix the slug to create a unique ID for our manager to route correctly
                    item_id = f"sxyprn_{slug}"
                    
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
    'item_id' is expected to be in the format 'sxyprn_some-video-slug'
    """
    # Remove the 'sxyprn_' prefix to get the actual slug
    slug = item_id.replace("sxyprn_", "")
    video_api_url = f"{API_BASE_URL}/videos/{slug}"
    streams = []

    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(video_api_url) as response:
                response.raise_for_status()
                json_data = await response.json()
                
                # The m3u8 URL is directly in the JSON response
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
