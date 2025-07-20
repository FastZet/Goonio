import aiohttp
from base64 import b64encode
from typing import List, Dict

from ..core.logger import logger

BASE_URL = "https://sxyprn.net"
API_BASE_URL = "https://sxyprn.net/api/v1"

async def search(query: str) -> List[Dict]:
    """
    Searches sxyprn.net's API for a given query and returns Stremio meta objects.
    """
    # Use the API endpoint for search
    search_url = f"{API_BASE_URL}/search/videos?query={query.replace(' ', '+')}&page=1"
    metas = []
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(search_url) as response:
                response.raise_for_status()
                json_data = await response.json()

                # The API returns a list of video objects directly
                for item in json_data.get('data', []):
                    # The unique identifier is the 'slug'
                    slug = item.get('slug')
                    if not slug:
                        continue
                    
                    item_id = f"sxyprn_post/{slug}"
                    
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
    'item_id' is expected to be in the format 'post/some-video-slug'
    """
    # Use the API endpoint for getting post details
    video_api_url = f"{API_BASE_URL}/{item_id}"
    streams = []

    try:
        async with aiohttp.ClientSession() as session:
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
